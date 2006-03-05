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
import os.path

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.component import enableSite, disableSite, findSite
from Products.Five.component.interfaces import IObjectManagerSite
from Products.Five.component.zpt import ZPTViewFactory
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

import zope.interface
import zope.component
from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.component.hooks import clearSite
from zope.app.apidoc.presentation import getViews
from zope.app.traversing.browser.absoluteurl import absoluteURL

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

        #TODO in the future we'll have to walk up to other site
        # managers and put them in the bases
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
        for reg in getViews(zope.interface.providedBy(self.context),
                            IBrowserRequest):
            factory = reg.factory
            while hasattr(factory, 'factory'):
                factory = factory.factory
            #XXX this should really be dealt with using a marker interface
            # on the view factory
            if hasattr(factory, '__name__') and \
                   factory.__name__.startswith('SimpleViewClass'):
                yield reg

    def templateFromViewname(self, viewname):
        view = zope.component.getMultiAdapter((self.context, self.request),
                                              name=viewname)
        return view.index

    def doCustomizeTemplate(self, viewname):
        # find the nearest site
        site = findSite(self.context, IObjectManagerSite)
        if site is None:
            raise TypeError("No site found")  #TODO find right exception

        # we're using the original filename of the template, not the
        # view name to avoid potential conflicts and/or confusion in
        # URLs
        template = self.templateFromViewname(viewname)
        zpt_id = os.path.basename(template.filename)

        viewzpt = ZopePageTemplate(zpt_id, template.read())
        site._setObject(zpt_id, viewzpt) #XXXthere could be a naming conflict
        components = site.getSiteManager()

        # find out the view registration object so we can get at the
        # provided and required interfaces
        for reg in getViews(zope.interface.providedBy(self.context),
                            IBrowserRequest):
            if reg.name == viewname:
                break

        view_factory = ZPTViewFactory(viewzpt, viewname)
        components.registerAdapter(view_factory, required=reg.required,
                                   provided=reg.provided, name=viewname) #XXX info?

        viewzpt = getattr(site, zpt_id)
        return viewzpt

    def customizeTemplate(self, viewname):
        viewzpt = self.doCustomizeTemplate(viewname)
        # to get a "direct" URL we use aq_inner for a straight
        # acquisition chain
        url = absoluteURL(aq_inner(viewzpt), self.request) + "/manage_workspace"
        self.request.RESPONSE.redirect(url)
