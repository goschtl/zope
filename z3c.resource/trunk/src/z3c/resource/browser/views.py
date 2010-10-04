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
$Id$
"""

from zope.interface import implements
from zope.location import locate
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.traversing.interfaces import TraversalError
import zope.component

from z3c.resource import interfaces


class Resources(BrowserView):
    """Provide a URL-accessible resource view."""

    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.browser.IBrowserPublisher"""

        if not interfaces.IResourceTraversable.providedBy(self.context):
            raise TraversalError(self.context,
                'Parameter context: IResourceTraversable required.')

        # get the resource instance
        resource = interfaces.IResource(self.context)

        # first check if we get a name, if not, we return the resource
        # container itself. No fear local resource can't override global
        # resources because we lookup on different context for local resource
        # then for a global resource.
        if name == '':
            return resource

        # first search for a resource in local resource location
        try:
            return resource[name]
        except KeyError, e:
            # no resource item found in local resource, doesn't matter.
            pass

        # query the default site resource and raise not found if there is no
        # resource item found. If you don't like to lookup at global resources
        # then you can override Resources view in your layer and skip this
        # part.
        return self._getSiteResource(name)

    def _getSiteResource(self, name):
        """This will lookup resources on a ISite."""
        resource = zope.component.queryAdapter(self.request, name=name)
        if resource is None:
            raise NotFound(self, name)

        sm = zope.component.getSiteManager()
        locate(resource, sm, name)
        return resource

    def browserDefault(self, request):
        """See zope.publisher.interfaces.browser.IBrowserPublisher"""
        return empty, ()

    def __getitem__(self, name):
        return self.publishTraverse(self.request, name)


def empty():
    return ''
