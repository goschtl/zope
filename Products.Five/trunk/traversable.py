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
import warnings
import zope.deprecation

import zope.publisher.interfaces
from zope.interface import implements, Interface
from zope.security.proxy import removeSecurityProxy
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import setDefaultSkin
from zope.app.interface import queryType
from zope.app.publication.publicationtraverse import PublicationTraverse

import zExceptions
import Products.Five.security
from Products.Five import fivemethod

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
    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into faking the Zope 3 traversal system
        by using an ITraverser adapter.
        """
        # We are trying to be compatible with Zope 2 and 3 traversal
        # behaviour as much as possible.  Therefore the first part of
        # this method is based on BaseRequest.traverse's behaviour:
        # 1. If an object has __bobo_traverse__, use it.
        # 2. Otherwise do attribute look-up or, if that doesn't work,
        #    key item lookup.

        if zope.deprecation.__show__():
            warnings.warn("The view lookup done by Traversable." \
                          "__bobo_traverse__ is now done by the standard " \
                          "traversal. This class is no longer needed and "
                          "will be removed in Zope 2.12.",
                          DeprecationWarning, 2)

        if hasattr(self, '__fallback_traverse__'):
            try:
                return self.__fallback_traverse__(REQUEST, name)
            except (AttributeError, KeyError):
                pass
            except zExceptions.NotFound:
                # OFS.Application.__bobo_traverse__ calls
                # REQUEST.RESPONSE.notFoundError which sets the HTTP
                # status code to 404
                try:
                    REQUEST.RESPONSE.setStatus(200)
                except AttributeError:
                    pass
        else:
            try:
                return getattr(self, name)
            except AttributeError:
                pass

            try:
                return self[name]
            except (KeyError, IndexError, TypeError, AttributeError):
                pass

        # This is the part Five adds:
        # 3. If neither __bobo_traverse__ nor attribute/key look-up
        # work, we try to find a Zope 3-style view.

        # For that we need to make sure we have a good request
        # (sometimes __bobo_traverse__ gets a stub request)
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()
                setDefaultSkin(REQUEST)

        # Con Zope 3 into using Zope 2's checkPermission
        Products.Five.security.newInteraction()

        try:
            ob = PublicationTraverse().traverseName(REQUEST, self, name)
            return removeSecurityProxy(ob).__of__(self)
        except zope.publisher.interfaces.NotFound:
            pass

        raise AttributeError(name)

class FiveTraversable(DefaultTraversable):

    def __init__(self, subject):
        if zope.deprecation.__show__():
            warnings.warn("The FiveTraversable class is no longer needed, " \
                          "and will be removed in Zope 2.12.",
                  DeprecationWarning, 2)
        
        self._subject = subject

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
