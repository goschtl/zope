#############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

import martian
import martian.util

import os.path
import sys

from zope.annotation.interfaces import IAttributeAnnotatable
from zope import interface, component

from grokcore.component.interfaces import IContext
from grokcore.formlib.components import GrokForm as BaseGrokForm
from grokcore.formlib.components import default_display_template, \
    default_form_template
from grokcore.view.components import PageTemplate
from grokcore.viewlet.components import Viewlet as BaseViewlet
from grokcore.viewlet.components import ViewletManager as BaseViewletManager
import grokcore.view
import grokcore.security

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile \
    as BaseViewPageTemplateFile
from Products.Five.browser import resource
from Products.Five.formlib import formbase
from Products.Five.viewlet.manager import ViewletManagerBase as \
    ZopeTwoBaseViewletManager
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder


class Model(SimpleItem):
    interface.implements(IAttributeAnnotatable, IContext)


class Container(Folder):
    interface.implements(IAttributeAnnotatable, IContext)


class View(grokcore.view.View):
    pass

class ViewPageTemplateFile(BaseViewPageTemplateFile):

    def pt_getContext(self):
        c = super(ViewPageTemplateFile, self).pt_getContext()
        if hasattr(self, 'pt_grokContext'):
            c.update(self.pt_grokContext)

        return c

class ZopeTwoPageTemplate(PageTemplate):

    def setFromFilename(self, filename, _prefix=None):
        self._template = ViewPageTemplateFile(filename, _prefix)

    def render(self, view):
        namespace = self.getNamespace(view)
        template = self._template.__of__(view)
        template.pt_grokContext = namespace
        return template()


class ZopeTwoPageTemplateFile(ZopeTwoPageTemplate):

    def __init__(self, filename, _prefix=None):
        self.__grok_module__ = martian.util.caller_module()
        if _prefix is None:
            module = sys.modules[self.__grok_module__]
            _prefix = os.path.dirname(module.__file__)
        self.setFromFilename(filename, _prefix)


class ZopeTwoDirectoryResource(resource.DirectoryResource):
    # We subclass this, because we want to override the default factories for
    # the resources so that .pt and .html do not get created as page
    # templates

    resource_factories = {}
    for type, factory in (resource.DirectoryResource.resource_factories.items()):
        if factory is resource.PageTemplateResourceFactory:
            continue
        resource_factories[type] = factory


class ZopeTwoDirectoryResourceFactory(resource.DirectoryResourceFactory):
    # __name__ is needed if you want to get url's of resources

    def __init__(self, name, path):
        self.__name = name
        self.__rsrc = self.factory(path, name)

    def __call__(self, request):
        resource = ZopeTwoDirectoryResource(self.__rsrc, request)
        resource.__name__ = self.__name # We need to add name
        return resource

# forms from formlib

class GrokForm(BaseGrokForm):

    def __init__(self, *args):
        super(GrokForm, self).__init__(*args)
        self.__name__ = self.__view_name__
        # super seems not to work correctly since this is needed again.
        self.static = component.queryAdapter(
            self.request, interface.Interface,
            name = self.module_info.package_dotted_name)
        if not (self.static is None):
            self.static = self.static.__of__(self)


class Form(GrokForm, formbase.PageForm, View):

    martian.baseclass()
    template = default_form_template

class AddForm(GrokForm, formbase.AddForm, View):

    martian.baseclass()
    template = default_form_template


class EditForm(GrokForm, formbase.EditForm, View):

    martian.baseclass()
    template = default_form_template


class DisplayForm(GrokForm, formbase.DisplayForm, View):

    martian.baseclass()
    template = default_display_template


# Viewlet / Viewlet Manager


class ViewletManager(BaseViewletManager, ZopeTwoBaseViewletManager):

    martian.baseclass()

    def __init__(self, context, request, view):
        super(ViewletManager, self).__init__(context, request, view)
        if not (self.static is None):
            # XXX See View
            self.static = self.static.__of__(self)

    def filter(self, viewlets):
        # XXX Need Zope 2 filter
        return ZopeTwoBaseViewletManager.filter(self, viewlets)

    def __getitem__(self, key):
        # XXX Need Zope 2 __getitem__
        return ZopeTwoBaseViewletManager.__getitem__(self, key)


class Viewlet(BaseViewlet):

    martian.baseclass()
