##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Absolute URL

$Id$
"""
from Acquisition import aq_inner, aq_parent
from OFS.interfaces import ITraversable

from zope.interface import implements
from zope.component import getView
from zope.app import zapi
from zope.app.traversing.browser.interfaces import IAbsoluteURL

from Products.Five.browser import BrowserView

class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.app.traversing.browser.absoluteurl)
    """
    implements(IAbsoluteURL)

    def __init__(self, context, request):
        self.context, self.request = context, request

    def __str__(self):
        return self._getContextAbsoluteUrl()

    def _getContextAbsoluteUrl(self):
        context = aq_inner(self.context)
        return context.absolute_url()
    
    __call__ = __str__

    def breadcrumbs(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        request = self.request

        name = context.getId()
        
        if container is None or self._isVirtualHostRoot() \
            or not ITraversable.providedBy(container):
            return (
                {'name': name, 'url': self._getContextAbsoluteUrl()},)

        view = zapi.getViewProviding(container, IAbsoluteURL, request)
        base = tuple(view.breadcrumbs())
        base += (
            {'name': name, 'url': ("%s/%s" % (base[-1]['url'], name))},)

        return base

    def _isVirtualHostRoot(self):
        virtualrootpath = self.request.get('VirtualRootPhysicalPath', None)
        if virtualrootpath is None:
            return False
        context = aq_inner(self.context)
        return context.restrictedTraverse(virtualrootpath) == context

class SiteAbsoluteURL(AbsoluteURL):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    This one is just used to stop breadcrumbs from crumbing up
    to the Zope root.

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def _getContextAbsoluteUrl(self):
        return self.context.absolute_url()
    
    def breadcrumbs(self):
        context = self.context
        request = self.request

        return ({'name': context.getId(),
                 'url': self._getContextAbsoluteUrl()
                 },)

class BrowserViewAbsoluteURL(AbsoluteURL):
    """
    views need to access inside the wrapper
    """
    def _getContextAbsoluteUrl(self):
        viewed = self.context.aq_inner.aq_parent
        #import pdb; pdb.set_trace() 
        viewed_url = getView(viewed, 'absolute_url', self.request)()
        return viewed_url + '/' + self.context.__name__
    

