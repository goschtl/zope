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
from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from Products.Five.component import enableSite, disableSite
from Products.Five.component.interfaces import IObjectManagerSite

from zope.interface import providedBy
from zope.component import getMultiAdapter
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.component.hooks import clearSite
from zope.app.zptpage import ZPTPage
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
        obj = self.context
        while obj is not None and not IObjectManagerSite.providedBy(obj):
            obj = aq_parent(obj)
        if obj is None:
            raise TypeError("No site found")  #TODO find right exception

        zpt = ZPTPage()
        zpt.source = unicode(src)
        obj._setObject(viewname, zpt) #XXX there could be a naming conflict
        zpt = getattr(obj, viewname)
        components = obj.getSiteManager()

        # find out the view registration object so we can get at the
        # provided and required interfaces
        for reg in getViews(providedBy(self.context), IBrowserRequest):
            if reg.name == viewname:
                break

        components.registerAdapter(ZPTViewFactory(zpt), required=reg.required,
                                   provided=reg.provided, name=viewname) #XXX info?
        return zpt

    def customizeTemplate(self, viewname):
        zpt = self.doCustomizeTemplate(viewname)
        #TODO use @@absolute_url view
        self.request.RESPONSE.redirect(zpt.absolute_url() + "/manage_workspace")

class ZPTViewFactory(object):

    def __init__(self, zptpage):
        self.zptpage = zptpage

    def __call__(self, context, request):
        return ZPTView(self.zptpage, context, request)

class ZPTView(object):

    def __init__(self, zptpage, context, request):
        self.zptpage = zptpage
        self.context = context
        self.request = request

    def __call__(self, **kw):
        namespace = self.zptpage.pt_getContext(self.context, self.request, **kw)
        namespace['view'] = self #XXX get the "real" view class
        return self.zptpage.pt_render(namespace)
