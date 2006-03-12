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
"""Machinery for making things traversable through adaptation

$Id$
"""
from zope.component import getMultiAdapter, ComponentLookupError
from zope.interface import implements, Interface
from zope.publisher.interfaces import ILayer
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import traversePathElement
from zope.app.publication.browser import setDefaultSkin
from zope.app.interface import queryType

import Products.Five.security
from zExceptions import NotFound
from ZPublisher import xmlrpc

_marker = object

class FakeRequest(dict):
    implements(IBrowserRequest)

    def has_key(self, key):
        return False

    def getURL(self):
        return "http://codespeak.net/z3/five"

class Traversable:
    """A mixin to make an object traversable using an ITraverser adapter.
    """
    __five_traversable__ = True

    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into faking the Zope 3 traversal system
        by using an ITraverser adapter.
        """
        # We are trying to be compatible with Zope 2 and 3 traversal
        # behaviour as much as possible.  Therefore the first part of
        # this method is based on BaseRequest.traverse's behaviour:
        # 1. If an object has __bobo_traverse__, use it
        # 2. Otherwise do attribute look-up (w/o acquisition if necessary)
        # 3. If that doesn't work, try key item lookup.

        if hasattr(self, '__fallback_traverse__'):
            try:
                return self.__fallback_traverse__(REQUEST, name)
            except (AttributeError, KeyError):
                pass
        else:
            # Note - no_acquire_flag is necessary to support things
            # like DAV.  We have to make sure that the target object
            # is not acquired if the request_method is other than GET
            # or POST. Otherwise, you could never use PUT to add a new
            # object named 'test' if an object 'test' existed above it
            # in the heirarchy -- you'd always get the existing object
            # :(
            no_acquire_flag = False
            method = REQUEST.get('REQUEST_METHOD', 'GET').upper()
            if ((method not in ('GET', 'POST') or
                 isinstance(getattr(REQUEST, 'response', {}), xmlrpc.Response))
                and getattr(REQUEST, 'maybe_webdav_client', False)):
                # Probably a WebDAV client.
                no_acquire_flag = True

            try:
                if (no_acquire_flag and
                    len(REQUEST['TraversalRequestNameStack']) == 0 and
                    hasattr(self, 'aq_base')):
                    if hasattr(self.aq_base, name):
                        return getattr(self, name)
                    else:
                        pass # attribute not found
                else:
                    return getattr(self, name)
            except AttributeError:
                try:
                    return self[name]
                except (KeyError, IndexError, TypeError, AttributeError):
                    pass # key not found

        # This is the part Five adds:
        # 4. If neither __bobo_traverse__ nor attribute/key look-up
        # work, we try to find a Zope 3-style view

        # For that we need to make sure we have a good request
        # (sometimes __bobo_traverse__ gets a stub request)
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()

        # Con Zope 3 into using Zope 2's checkPermission
        Products.Five.security.newInteraction()

        # Set the default skin on the request if it doesn't have any
        # layers set on it yet
        if queryType(REQUEST, ILayer) is None:
            setDefaultSkin(REQUEST)

        # Use the ITraverser adapter (which in turn uses ITraversable
        # adapters) to traverse to a view.  Note that we're mixing
        # object-graph and object-publishing traversal here, but Zope
        # 2 has no way to tell us when to use which...
        # TODO Perhaps we can decide on object-graph vs.
        # object-publishing traversal depending on whether REQUEST is
        # a stub or not?
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, LookupError,
                AttributeError, KeyError, NotFound):
            pass

        raise AttributeError(name)

    __bobo_traverse__.__five_method__ = True


class FiveTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        context = self._subject
        __traceback_info__ = (context, name, furtherPath)
        # Find the REQUEST
        REQUEST = getattr(context, 'REQUEST', None)
        if not IBrowserRequest.providedBy(REQUEST):
            REQUEST = FakeRequest()
            setDefaultSkin(REQUEST)
        # Try to lookup a view
        try:
            return getMultiAdapter((context, REQUEST), Interface, name)
        except ComponentLookupError:
            pass
