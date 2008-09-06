#############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grokkers for the various components."""

import os

import zope.component.interface
from zope import interface, component
from zope.security.checker import NamesChecker
from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IBrowserSkinType

import martian
from martian.error import GrokError
from martian import util

import grokcore.security
import grokcore.view
from grokcore.security.util import protect_getattr
from grokcore.view import components
from grokcore.view import templatereg

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

def default_fallback_to_name(factory, module, name, **data):
    return name


class ViewGrokker(martian.ClassGrokker):
    martian.component(components.View)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)

    def grok(self, name, factory, module_info, **kw):
        # Need to store the module info object on the view class so that it
        # can look up the 'static' resource directory.
        factory.module_info = module_info
        return super(ViewGrokker, self).grok(name, factory, module_info, **kw)

    def execute(self, factory, config, context, layer, name, **kw):
        # find templates
        templates = factory.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, factory.module_info, factory)
                )

        # safety belt: make sure that the programmer didn't use
        # @grok.require on any of the view's methods.
        methods = util.methods_from_class(factory)
        for method in methods:
            if grokcore.security.require.bind().get(method) is not None:
                raise GrokError('The @grok.require decorator is used for '
                                'method %r in view %r. It may only be used '
                                'for XML-RPC methods.'
                                % (method.__name__, factory), factory)

        # __view_name__ is needed to support IAbsoluteURL on views
        factory.__view_name__ = name
        adapts = (context, layer)

        config.action(
            discriminator=('adapter', adapts, interface.Interface, name),
            callable=component.provideAdapter,
            args=(factory, adapts, interface.Interface, name),
            )
        return True

    def checkTemplates(self, templates, module_info, factory):

        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method

        def has_no_render(factory):
            return not getattr(factory, 'render', None)
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)


class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(components.View)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        for method_name in IBrowserPage:
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protect_getattr,
                args=(factory, method_name, permission),
                )
        return True


class TemplateGrokker(martian.GlobalGrokker):
    # this needs to happen before any other grokkers execute that use
    # the template registry
    martian.priority(1001)

    def grok(self, name, module, module_info, config, **kw):
        module.__grok_templates__ = templatereg.TemplateRegistry()
        return True


class FilesystemPageTemplateGrokker(martian.GlobalGrokker):
    # do this early on, but after ModulePageTemplateGrokker, as
    # findFilesystem depends on module-level templates to be
    # already grokked for error reporting
    martian.priority(999)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False
        config.action(
            discriminator=None,
            callable=templates.findFilesystem,
            args=(module_info,)
            )
        return True


class UnassociatedTemplatesGrokker(martian.GlobalGrokker):
    martian.priority(-1001)

    def grok(self, name, module, module_info, config, **kw):
        templates = module_info.getAnnotation('grok.templates', None)
        if templates is None:
            return False

        config.action(
            discriminator=None,
            callable=templates.checkUnassociated,
            args=(module_info,)
            )
        return True


allowed_resource_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                          'request', '__call__')
allowed_resourcedir_names = allowed_resource_names + ('__getitem__', 'get')

class StaticResourcesGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        # we're only interested in static resources if this module
        # happens to be a package
        if not module_info.isPackage():
            return False

        resource_path = module_info.getResourcePath('static')
        if os.path.isdir(resource_path):
            static_module = module_info.getSubModuleInfo('static')
            if static_module is not None:
                if static_module.isPackage():
                    raise GrokError(
                        "The 'static' resource directory must not "
                        "be a python package.",
                        module_info.getModule())
                else:
                    raise GrokError(
                        "A package can not contain both a 'static' "
                        "resource directory and a module named "
                        "'static.py'", module_info.getModule())

        # public checker by default
        checker = NamesChecker(allowed_resourcedir_names)

        resource_factory = components.DirectoryResourceFactory(
            resource_path, checker, module_info.dotted_name)
        adapts = (IDefaultBrowserLayer,)
        provides = interface.Interface
        name = module_info.dotted_name
        config.action(
            discriminator=('adapter', adapts, provides, name),
            callable=component.provideAdapter,
            args=(resource_factory, adapts, provides, name),
            )
        return True


_skin_not_used = object()

class SkinInterfaceDirectiveGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)

    def grok(self, name, interface, module_info, config, **kw):
        skin = grokcore.view.skin.bind(default=_skin_not_used).get(interface)
        if skin is _skin_not_used:
            # The skin directive is not actually used on the found interface.
            return False

        if not interface.extends(IBrowserRequest):
            # For layers it is required to extend IBrowserRequest.
            raise GrokError(
                "The grok.skin() directive is used on interface %r. "
                "However, %r does not extend IBrowserRequest which is "
                "required for interfaces that are used as layers and are to "
                "be registered as a skin."
                % (interface.__identifier__, interface.__identifier__),
                interface
                )
        config.action(
            discriminator=('utility', IBrowserSkinType, skin),
            callable=zope.component.interface.provideInterface,
            args=(skin, interface, IBrowserSkinType)
            )
        return True
