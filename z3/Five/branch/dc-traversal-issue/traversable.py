##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Machinery for making things traversable through adaptation

$Id$
"""
from zExceptions import NotFound
from zope.exceptions import NotFoundError
from zope.component import getView, ComponentLookupError
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import traversePathElement
from monkey import DebugFlags
from Products.PageTemplates.Expressions import SubPathExpr

_marker = object

class FakeRequest:
    implements(IBrowserRequest)

    debug = DebugFlags()

    def getPresentationSkin(self):
        return None

    def has_key(self, key):
        return False

class Traversable:
    """A mixin to make an object traversable using an ITraverser adapter.
    """
    __five_traversable__ = True

    def __fallback_traverse__(self, REQUEST, name):
        """Method hook for fallback traversal

        This method is called by __bobo_traverse___ when Zope3-style
        ITraverser traversal fails.

        Try to look up on the stack to see if we are being called from
        a SubPathExpr, and if so, return None instead of raising a
        NotFoundError.

        Otherwise, raise a Zope2 zExceptions.NotFound error.
        """

        import inspect
        frame = inspect.currentframe()
        try:
            while frame is not None:
                context = frame.f_locals.get('self', _marker)
                if (context is not _marker and
                    isinstance(context, SubPathExpr)):
                    # We are being called from a SubPathExpr.  Return
                    # None instead of raising a NotFoundError, because
                    # no __bobo_traverse__ caller expects an
                    # exception. See more below.
                    return None
                frame = frame.f_back
            # If we got this far, we are being called from something
            # else that isn't a SubPathExpr.  None of the
            # __bobo_traverse__ callers expect to get an
            # exception. Instead, they *always* expect to get an
            # object.  However, for BaseRequest, if we return None,
            # instead of getting a NotFoundError, we will get an
            # exception complaining about a missing docstring. Thus,
            # we raise the NotFoundError ourselves.
            return REQUEST.RESPONSE.notFoundError(name)
        finally:
            del frame
            del context

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
        try:
            kw = dict(path=[name], request=REQUEST)
            return ITraverser(self).traverse(**kw).__of__(self)
        except (ComponentLookupError, NotFoundError,
                AttributeError, KeyError, NotFound):
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
    __bobo_traverse__.__five_method__ = True


class FiveTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        context = self._subject
        __traceback_info__ = (context, name, furtherPath)
        # Find the REQUEST
        REQUEST = getattr(context, 'REQUEST', None)
        if not IBrowserRequest.providedBy(REQUEST):
            REQUEST = FakeRequest()
        # Try to lookup a view first
        try:
            return getView(context, name, REQUEST)
        except ComponentLookupError:
            pass
        # If a view can't be found, then use default traversable
        return super(FiveTraversable, self).traverse(name, furtherPath)

