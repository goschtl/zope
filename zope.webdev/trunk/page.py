##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Page Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
import zope.security.checker
import zope.app.component.site
import zope.app.component.interfaces.registration
import zope.app.container.contained
import zope.app.module.manager
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app import zapi
from zope.app import publisher
from zope.app.presentation import zpt, registration
from zope.webdev import interfaces


class Page(persistent.Persistent, zope.app.container.contained.Contained):
    """Local page."""
    zope.interface.implements(interfaces.IPage)

    def __init__(self, name,
                 for_=zope.interface.Interface,
                 layer=IDefaultBrowserLayer,
                 permission=zope.security.checker.CheckerPublic,
                 templateSource=None, moduleSource=None, className=None):

        self._template = zpt.ZPTTemplate()


        self.name = name
        self.for_ = for_
        self.layer = layer
        self.permission = permission
        if templateSource is not None:
            self.templateSource = templateSource
        self.moduleSource = moduleSource
        self.className = className

    @apply
    def templateSource():
        def get(self):
            return self._template.source

        def set(self, value):
            self._template.source = value

        return property(get, set)

    @apply
    def moduleSource():
        def get(self):
            return getattr(self,'_moduleSource',u'')

        def set(self, value):
            self._moduleSource=value
            if hasattr(self,'_v_module'):
                del(self._v_module)
        return property(get, set)

    @apply
    def _module():
        def get(self):
            if not hasattr(self,'_v_module'):
                self._v_module = \
                        zope.app.module.manager.ModuleManager(self.moduleSource)
            return self._v_module
        return property(get)

    def getTemplate(self):
        return self._template


class PageRegistration(zope.app.component.site.AdapterRegistration):

    provided = zope.interface.Interface

    def __init__(self, page):

        self.page = page

    @property
    def name(self):
        return zapi.name(self.page)

    @property
    def with(self):
        return (self.page.layer, )

    @property
    def required(self):
        return self.page.for_

    @property
    def component(self):
        makeViewClass = MakeViewClass(self.page)

        return registration.TemplateViewFactory(
            makeViewClass, self.page.getTemplate(), self.page.permission)


class MakeViewClass(object):

    def __init__(self,page):
        self.page = page

    def __call__(self,context,request):
        if self.page._module and self.page.className:
            class_ = getattr(self.page._module.getModule(),
                             self.page.className)
        else:
            class_  = publisher.browser.BrowserView

        if not IBrowserView.implementedBy(class_):
            class_ = type(class_.__name__,
                          (class_, publisher.browser.BrowserView), {})
        return class_(context, request)

def registerPage(page):
    package = zapi.getParent(page)
    reg = PageRegistration(page)
    package.registrationManager.addRegistration(reg)
    reg.status = zope.app.component.interfaces.registration.ActiveStatus
