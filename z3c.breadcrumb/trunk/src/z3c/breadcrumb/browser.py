##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 70825 2006-10-20 01:34:05Z rogerineichen $
"""
__docformat__ = 'reStructuredText'

import zope.component
import zope.interface
import zope.location
import zope.traversing.api
import zope.traversing.browser
from zope.publisher.interfaces import NotFound
from zope.publisher import browser
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import IContainmentRoot
from zope.app.component.interfaces import ISite

from z3c.breadcrumb import interfaces


class Breadcrumbs(zope.location.Location):
    """Breadcrumbs implementation using IBreadcrum adapters."""

    zope.interface.implements(interfaces.IBreadcrumbs)
    zope.component.adapts(zope.interface.Interface, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getParent(self):
        return getattr(self, '_parent', self.context)

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)

    @property
    def crumbs(self):
        objects = []
        for obj in ( [self.context] +
                     list(zope.traversing.api.getParents(self.context)) ):
            objects.append(obj)
            if ISite.providedBy(obj):
                break
        objects.reverse()
        for object in objects:
            info = zope.component.getMultiAdapter((object, self.request),
                                        interfaces.IBreadcrumb)
            yield {'name': info.name,
                   'url': info.url,
                   'activeURL': info.activeURL}


class GenericBreadcrumb(object):
    """A generic breadcrumb adapter."""
    zope.interface.implements(interfaces.IBreadcrumb)
    zope.component.adapts(zope.interface.Interface, IHTTPRequest)

    # See interfaces.IBreadcrumb
    activeURL = True

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def name(self):
        """See interfaces.IBreadcrumb"""
        name = getattr(self.context, 'title', None)
        if name is None:
            name = getattr(self.context, '__name__', None)
        if name is None and IContainmentRoot.providedBy(self.context):
            name = 'top'
        return name

    @property
    def url(self):
        """See interfaces.IBreadcrumb"""
        return zope.traversing.browser.absoluteURL(self.context, self.request)


def CustomNameBreadcrumb(name):
    return type('CustomNameBreadcrumb(%r)' %name,
                (GenericBreadcrumb,), {'name': name})
