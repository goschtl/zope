##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Machinery for making things viewable through Five views

$Id$
"""
from webdav.NullResource import NullResource
from zope.component import getView, ComponentLookupError
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from monkey import DebugFlags

class FakeRequest:
    implements(IBrowserRequest)

    debug = DebugFlags()

    def getPresentationSkin(self):
        return None

class Viewable:
    """A mixin to make an object viewable using the Zope 3 system.
    """
    __five_viewable__ = True

    def __fallback_traverse__(self, REQUEST, name):
        """Method hook for fallback traversal

        This method is called by __bobo_traverse___ when Zope3-style
        view lookup fails.  By default, we do what Zope 2 would do,
        raise a NotFound error."""
        try:
            REQUEST.RESPONSE.notFoundError("%s " % name)
        except AttributeError:
            raise KeyError, name

    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into publishing Zope 3-style views.
        """
        if not IBrowserRequest.providedBy(REQUEST):
            REQUEST = FakeRequest()
        try:
            return getView(self, name, REQUEST).__of__(self)
        except ComponentLookupError:
            pass
        try:
            return getattr(self, name)
        except AttributeError:
            pass
        try:
            return self[name]
        except (AttributeError, KeyError):
            pass

        return self.__fallback_traverse__(REQUEST, name)
