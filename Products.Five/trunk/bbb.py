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
"""Things needed for backward compatibility

$Id
"""
from zope.interface import Interface, implements
from zope.component.interfaces import ComponentLookupError
from zope.app.publisher.browser import getDefaultViewName

import zExceptions
import Products.Five.security
from Products.Five import fivemethod
from Products.Five.interfaces import IBrowserDefault

class BrowserDefault(object):
    implements(IBrowserDefault)

    def __init__(self, context):
        self.context = context

    def defaultView(self, request):
        context = self.context
        try:
            name = getDefaultViewName(context, request)
            return context, [name,]
        except ComponentLookupError:
            return context, None

class Traversable:
    """A mixin to make an object traversable"""
    __five_traversable__ = True

    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into faking the Zope 3 traversal system
        by using an ITraverser adapter.
        """
        try:
            return getattr(self, name)
        except AttributeError:
            pass

        try:
            return self[name]
        except (KeyError, IndexError, TypeError, AttributeError):
            pass

        raise AttributeError(name)
