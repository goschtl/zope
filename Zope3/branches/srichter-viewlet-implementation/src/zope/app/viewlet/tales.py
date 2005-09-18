##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Viewlet tales expression registrations

$Id$
"""
__docformat__ = 'restructuredtext'
import sys

from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, directlyProvides
from zope.security import canAccess
from zope.security.interfaces import Unauthorized

from zope.tales.expressions import StringExpr

from zope.app import zapi

from zope.app.viewlet.interfaces import ITALESViewletExpression
from zope.app.viewlet.interfaces import ITALESViewletsExpression
from zope.app.viewlet.interfaces import IViewletRegion
from zope.app.viewlet.interfaces import IViewlet
from zope.app.viewlet.interfaces import ViewletRegionLookupError


def getRegion(str):
    """Get a region from the string.

    This function will create the dummy region implementation as well.
    """
    region = zapi.queryUtility(IViewletRegion, name=str)
    if region is None:
        raise ViewletRegionLookupError(
            'Viewlet region interface not found.', str)

    # Create a dummy region instance for adapter lookup. This is not ultra
    # clean but puts the burden of filtering by region on the adapter
    # registry.
    class DummyRegion(object):
        implements(region)
    return DummyRegion()


class TALESViewletsExpression(StringExpr):
    """Collect viewlets via a TAL namespace called `viewlets`."""

    implements(ITALESViewletsExpression)

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the region from the expression
        region = getRegion(self._s)

        # Find the viewlets
        viewlets = zapi.getAdapters((context, request, view, region), IViewlet)
        viewlets = [viewlet for name, viewlet in viewlets
                    if canAccess(viewlet, '__call__')]
        viewlets.sort(lambda x, y: cmp(x.weight, y.weight))

        return viewlets


class TALESViewletExpression(StringExpr):
    """Collects a single viewlet via a TAL namespace called viewlet."""

    implements(ITALESViewletExpression)

    def __init__(self, name, expr, engine):
        if not '/' in expr:
            raise KeyError('Use `iface/viewletname` for defining the viewlet.')

        parts = expr.split('/')
        if len(parts) > 2:
            raise KeyError("Do not use more then one / for defining iface/key.")

        # get interface from key
        self._iface = parts[0]
        self._name = parts[1]

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the region from the expression
        region = getRegion(self._iface)

        # Find the viewlets
        viewlet = zapi.queryMultiAdapter(
            (context, request, view, region), IViewlet, name=self._name)

        if viewlet is None:
            raise ComponentLookupError(
                'No viewlet with name `%s` found.' %self._name)

        if not canAccess(viewlet, '__call__'):
            raise Unauthorized(
                'You are not authorized to access the viewlet '
                'called `%s`.' %self._name)

        return viewlet()
