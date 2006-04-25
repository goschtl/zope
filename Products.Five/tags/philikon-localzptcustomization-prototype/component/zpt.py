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
from Acquisition import aq_inner, aq_acquire
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.Five.browser import BrowserView
from Products.Five.component import findSite

import zope.component
import zope.interface
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.container.interfaces import IObjectRemovedEvent

class IZPTViewFactory(zope.interface.Interface):
    """Marker interface for those view factories that invoke locally
    registered components.

    By finding factories that provide this interface we can find the
    registration object for a locally registered template and, for
    example, unregister the view when the template is deleted."""
    template = zope.interface.Attribute("The ZPT template to invoke.")

class ZPTViewFactory(object):
    """View factory that gets registered with a local component
    registry.

    When this factory is invoked, it returns a view that in turn
    invokes the template upon publishing.  We hold a (potentially
    persistent) reference only to the Page Template, everything else
    needed for the template (e.g. its view class) is constructed by
    the view."""
    zope.interface.implements(IZPTViewFactory)

    def __init__(self, template, name):
        self.template = template
        self.name = name

    def __call__(self, context, request):
        return ZPTView(self.template, self.name, context, request)

class ZPTView(BrowserView):
    """View that invokes a locally placed ZopePageTemplate object.
    """

    def __init__(self, template, name, context, request):
        self.template = template
        self.context = context
        self.request = request

        # this is needed for Zope 2's publication which wants to
        # record some metadata in the transaction, among others the
        # name of published objects
        self.__name__ = name

    def _findViewClass(self):
        #XXX we might want to walk up to the next site instead, not
        # just go to the global one directly
        gsm = zope.component.getGlobalSiteManager()
        view = gsm.queryMultiAdapter((self.context, self.request),
                                     zope.interface.Interface, self.__name__)
        if view is not None:
            return view
        return self

    def _zptNamespace(self):
        root = aq_acquire(self.context, 'getPhysicalRoot')()
        here = aq_inner(self.context)
        return {
            'template':  self.template,
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
        return self.template.pt_render(namespace)

class IRegisteredViewPageTemplate(IPageTemplate):
    """Marker interface for registered view page templates
    """

@zope.component.adapter(IRegisteredViewPageTemplate, IObjectRemovedEvent)
def unregisterViewWhenZPTIsDeleted(zpt, event):
    components = zope.component.getSiteManager(zpt)
    for reg in components.registeredAdapters():
        if (IZPTViewFactory.providedBy(reg.factory) and
            reg.factory.template == zpt):
            break
    components.unregisterAdapter(reg.factory, reg.required, reg.provided,
                                 reg.name)
