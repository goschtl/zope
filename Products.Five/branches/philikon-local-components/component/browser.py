##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Component browser views

$Id$
"""
from Acquisition import aq_parent, aq_acquire, aq_inner
from Products.Five.browser import BrowserView
from Products.Five.component import enableSite, disableSite
from Products.Five.component.interfaces import IObjectManagerSite
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.Expressions import SecureModuleImporter

from zope.interface import Interface, providedBy
from zope.component import getMultiAdapter, getGlobalSiteManager
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.component.hooks import clearSite
from zope.app.apidoc.presentation import getViews, getViewInfoDictionary

class ComponentsView(BrowserView):

    def update(self):
        form = self.request.form
        if form.has_key('MAKESITE'):
            self.makeSite()
        elif form.has_key('UNMAKESITE'):
            self.unmakeSite()

    def isSite(self):
        return IObjectManagerSite.providedBy(self.context)

    def makeSite(self):
        if IObjectManagerSite.providedBy(self.context):
            raise ValueError('This is already a site')

        enableSite(self.context, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        self.context.setSiteManager(components)

    def unmakeSite(self):
        if not self.isSite():
            raise ValueError('This is not a site')

        disableSite(self.context)

        # disableLocalSiteHook circumcised our context so that it's
        # not an ISite anymore.  That can mean that certain things for
        # it can't be found anymore.  So, for the rest of this request
        # (which will be over in about 20 CPU cycles), already clear
        # the local site from the thread local.
        clearSite()

        self.context.setSiteManage(None)

class CustomizationView(BrowserView):

    def templateViewRegistrations(self):
        for reg in getViews(providedBy(self.context), IBrowserRequest):
            factory = reg.factory
            while hasattr(factory, 'factory'):
                factory = factory.factory
            if hasattr(factory, '__name__') and \
                   factory.__name__.startswith('SimpleViewClass'):
                yield reg

    def templateSource(self, viewname):
        view = getMultiAdapter((self.context, self.request),
                               name=viewname)
        return view.index.read()

    def doCustomizeTemplate(self, viewname):
        src = self.templateSource(viewname)

        # find the nearest site
        site = self.context
        while site is not None and not IObjectManagerSite.providedBy(site):
            site = aq_parent(site)
        if site is None:
            raise TypeError("No site found")  #TODO find right exception

        id = str(viewname)  #XXX this could barf
        viewzpt = ZopePageTemplate(id, src)
        site._setObject(id, viewzpt) #XXXthere could be a naming conflict
        components = site.getSiteManager()

        # find out the view registration object so we can get at the
        # provided and required interfaces
        for reg in getViews(providedBy(self.context), IBrowserRequest):
            if reg.name == viewname:
                break

        view_factory = ZPTViewFactory(viewzpt, viewname)
        components.registerAdapter(view_factory, required=reg.required,
                                   provided=reg.provided, name=viewname) #XXX info?
        return viewzpt

    def customizeTemplate(self, viewname):
        viewzpt = self.doCustomizeTemplate(viewname)
        #TODO use @@absolute_url view
        self.request.RESPONSE.redirect(viewzpt.absolute_url() + "/manage_workspace")

class ZPTViewFactory(object):

    def __init__(self, viewzpt, viewname):
        self.viewzpt = viewzpt
        self.viewname = viewname

    def __call__(self, context, request):
        return ZPTView(self.viewzpt, self.viewname, context, request)

class ZPTView(BrowserView):

    def __init__(self, viewzpt, viewname, context, request):
        self.viewzpt = viewzpt
        self.viewname = viewname
        self.context = context
        self.request = request

    def _findViewClass(self):
        #XXX we might want to walk up to the next site instead, not
        # just go to the global one directly
        gsm = getGlobalSiteManager()
        view = gsm.queryMultiAdapter((self.context, self.request), Interface,
                                     name=self.viewname)
        if view is not None:
            return view
        return self

    def _zptNamespace(self):
        root = aq_acquire(self.context, 'getPhysicalRoot')()
        here = aq_inner(self.context)
        return {
            'template':  self.viewzpt,
            'nothing':   None,
            'request':   self.request,
            'here':      here,
            'context':   here,
            'container': here,
            'view':      self._findViewClass(),
            'root':      root,
            'modules':   SecureModuleImporter,
            }

    def __call__(self, *args, **kwargs):
        namespace = self._zptNamespace()
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        namespace['options'] = kwargs
        return self.viewzpt.pt_render(namespace)
