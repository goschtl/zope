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
    def __bobo_traverse__(self, REQUEST, name):
        try:
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
            # XXX not sure this is very useful
            #method = REQUEST.get('REQUEST_METHOD', 'GET')
            #if not method in ('GET', 'POST'):
            #    return NullResource(self, name, REQUEST).__of__(self)

            # Waaa. See Application.py
            try:
                REQUEST.RESPONSE.notFoundError("%s " % name)
            except AttributeError:
                raise KeyError, name
        except:
            import traceback
            traceback.print_exc()
            raise
