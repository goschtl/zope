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
from zExceptions import NotFound

from zope.component import getMultiAdapter, ComponentLookupError
from zope.interface import implements, Interface
from zope.publisher.interfaces import ILayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import setDefaultSkin
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.adapters import traversePathElement
from zope.app.interface import queryType

from AccessControl import getSecurityManager
from Products.Five import fivemethod
from Products.Five.security import newInteraction

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

    @fivemethod
    def __fallback_traverse__(self, REQUEST, name):
        """Method hook for fallback traversal

        This method is called by __bobo_traverse___ when Zope3-style
        ITraverser traversal fails.

        Just raise a AttributeError to indicate traversal has failed
        and let Zope do it's job.
        """
        raise NotImplementedError

    @fivemethod
    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into faking the Zope 3 traversal system
        by using an ITraverser adapter.
        """
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()

        # set the default skin on the request if it doesn't have any
        # layers set on it yet
        if queryType(REQUEST, ILayer) is None:
            setDefaultSkin(REQUEST)

        # con Zope 3 into using Zope 2's checkPermission
        newInteraction()
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, LookupError,
                AttributeError, KeyError, NotFound):
            pass
        try:
            return self.__fallback_traverse__(REQUEST, name)
        except NotImplementedError:
            pass
        # TODO: This should at least make an attempt to deal with
        # potential WebDAV issues, in particular we should not perform
        # acquisition for webdav requests. See BaseRequest.traverse for 
        # details.
        try:
            return getattr(self, name)
        except AttributeError:
            pass
        try:
            return self[name]
        except (AttributeError, KeyError):
            pass
        raise AttributeError, name

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
