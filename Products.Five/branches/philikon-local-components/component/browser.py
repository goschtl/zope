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
from Products.Five.component.zpt import ZPTViewFactory, IRegisteredViewPageTemplate
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

import zope.interface
import zope.component
import zope.dottedname.resolve
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

def mangleAbsoluteFilename(filename):
    """
    Mangle an absolute filename when the file happens to be in a
    package.  The mangled name will then be of the form::

      <dotted package name>/<base filename>.

    For example, let's take Five's configure.zcml as an example.  We
    assemble it in an OS-independent way so this test works on all
    platforms:
    
      >>> def filesystemPath(*elements):
      ...     return os.path.sep.join(elements)

    We see that the filename is now mangled:

      >>> mangleAbsoluteFilename(filesystemPath(
      ...     '', 'path', 'to', 'Products', 'Five', 'configure.zcml'))
      'Products.Five/configure.zcml'

    The name of a file that's not in a package is returned unchanged:

      >>> not_in_a_package = filesystemPath('', 'path', 'to', 'configure.zcml')
      >>> mangleAbsoluteFilename(not_in_a_package) == not_in_a_package
      True
    """
    if not os.path.isabs(filename):
        raise ValueError("Can only determine package for absolute filenames")
    dir, basename = os.path.split(filename)
    pieces = dir.split(os.path.sep)
    if pieces[0] == '':
        pieces = pieces[1:]
    while pieces:
        try:
            zope.dottedname.resolve.resolve('.'.join(pieces))
            break
        except ImportError:
            pieces = pieces[1:]
    if not pieces:
        return filename
    return '.'.join(pieces) + '/' + basename

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

    def templateViewRegInfo(self):
        def regkey(reg):
            return reg.name
        for reg in sorted(self.templateViewRegistrations(), key=regkey):
            yield {
                'viewname': reg.name,
                'for': reg.required[0].__identifier__,
                'type': reg.required[1].__identifier__,
                'zptfile': mangleAbsoluteFilename(reg.factory.index.filename),
                'zcmlfile': mangleAbsoluteFilename(reg.info.file)
                }

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
        zope.interface.alsoProvides(viewzpt, IRegisteredViewPageTemplate)
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
