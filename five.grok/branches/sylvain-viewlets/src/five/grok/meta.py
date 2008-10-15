
import martian
import five.grok
import grokcore.security
import grokcore.view
import grokcore.component

from zope import interface, component
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from five.grok import components
from martian.error import GrokError

from grokcore.view.meta.views import default_view_name

from Products.Five.security import protectClass
from Globals import InitializeClass as initializeClass

import os.path

class ViewSecurityGrokker(martian.ClassGrokker):
    martian.component(five.grok.View)
    martian.directive(grokcore.security.require, name='permission')

    def execute(self, factory, config, permission, **kw):
        if permission is None:
            permission = 'zope.Public'

        config.action(
            discriminator = ('five:protectClass', factory),
            callable = protectClass,
            args = (factory, permission)
            )

        # Protect the class
        config.action(
            discriminator = ('five:initialize:class', factory),
            callable = initializeClass,
            args = (factory,)
            )

        return True


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

            # FIXME: This is public, we need to set security on resources ?
            name = module_info.dotted_name
            resource_factory = components.DirectoryResourceFactory(
                name, resource_path)
            adapts = (IDefaultBrowserLayer,)
            provides = interface.Interface

            config.action(
                discriminator=('adapter', adapts, provides, name),
                callable=component.provideAdapter,
                args=(resource_factory, adapts, provides, name),
                )
            return True

        return False


class ViewletManagerGrokker(martian.ClassGrokker):

    martian.component(components.ViewletManager)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer)
    martian.directive(five.grok.view)

    def grok(self, name, provider, module_info, **kw):
        # Store module_info on the object.
        provider.__view_name__ = name
        provider.module_info = module_info
        return super(ViewletManagerGrokker, self).grok(
            name, provider, module_info, **kw)

    def execute(self, provider, name, context, view, layer, config, **kw):
        """Register a content provider.
        """
        templates = provider.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, provider.module_info, provider)
                )

        for_ = (context, layer, view,)
        config.action(
            discriminator=('adapter', for_, IContentProvider, name),
            callable=component.provideAdapter,
            args=(provider, for_, IContentProvider, name),
            )

        return True

    def checkTemplates(self, templates, module_info, provider):
        def has_render(provider):
            return provider.render != components.ViewletManager.render
        def has_no_render(provider):
            # always has a render method
            return False
        templates.checkTemplates(module_info, provider, 'viewlet manager',
                                 has_render, has_no_render)


class ViewletGrokker(ViewletManagerGrokker):

    martian.component(components.Viewlet)
    martian.directive(five.grok.viewletmanager)

    def execute(self, provider, name, context, view,
                layer, viewletmanager, config, **kw):
        """Register a viewlet.
        """
        templates = provider.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, provider.module_info, provider)
                )

        for_ = (context, layer, view, viewletmanager)
        config.action(
            discriminator=('adapter', for_, IViewlet, name),
            callable=provideAdapter,
            args=(provider, for_, IViewlet, name),
            )

        return True

    def checkTemplates(self, templates, module_info, provider):
        def has_render(provider):
            return provider.render != components.Viewlet.render
        def has_no_render(provider):
            return not has_render(provider)
        templates.checkTemplates(module_info, provider, 'viewlet',
                                 has_render, has_no_render)
