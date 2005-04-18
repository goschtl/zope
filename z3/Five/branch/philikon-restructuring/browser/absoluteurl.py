##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Absolute URL

$Id$
"""
from zope.interface import implements
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from Products.Five.browser import BrowserView

class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def __init__(self, context, request):
        self.context, self.request = context, request

    implements(IAbsoluteURL)

    def __str__(self):
        context = aq_inner(self.context)
        return context.absolute_url()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context.aq_inner
        container = context.aq_parent
        request = self.request

        name = context.getId()
        
        if container is None or self._isVirtualHostRoot() \
            or not ITraversable.providedBy(container):
            return (
                {'name': name, 'url': context.absolute_url()},)

        view = getViewProviding(container, IAbsoluteURL, request)
        base = tuple(view.breadcrumbs())
        base += (
            {'name': name, 'url': ("%s/%s" % (base[-1]['url'], name))},)

        return base

    def _isVirtualHostRoot(self):
        virtualrootpath = self.request.get('VirtualRootPhysicalPath', None)
        if virtualrootpath is None:
            return False
        context = self.context.aq_inner
        return context.restrictedTraverse(virtualrootpath) == context

class SiteAbsoluteURL(AbsoluteURL):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    This one is just used to stop breadcrumbs from crumbing up
    to the Zope root.

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def breadcrumbs(self):
        context = self.context
        request = self.request

        return ({'name': context.getId(),
                 'url': context.absolute_url()
                 },)
