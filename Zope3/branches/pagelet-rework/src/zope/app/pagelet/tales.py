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
"""Pagelet tales expression registrations

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

from zope.app.pagelet.interfaces import ITALESPageletExpression
from zope.app.pagelet.interfaces import ITALESPageletsExpression
from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IPagelet
from zope.app.pagelet.interfaces import PageletSlotLookupError


def getSlot(str):
    """Get a slot from the string.

    This function will create the dummy slot implementation as well.
    """
    slot = zapi.queryUtility(IPageletSlot, name=str)
    if slot is None:
        raise PageletSlotLookupError(
            _('Pagelet slot interface not found.'), str)

    # Create a dummy slot instance for adapter lookup. This is not ultra
    # clean but puts the burden of filtering by slot on the adapter
    # registry.
    class DummySlot(object):
        implements(slot)
    return DummySlot()


class TALESPageletsExpression(StringExpr):
    """Collect pagelets via a TAL namespace called `pagelets`."""

    implements(ITALESPageletsExpression)

    def __call__(self, econtext):
        context = econtext.vars['context']
        request = econtext.vars['request']
        view = econtext.vars['view']

        # get the slot from the expression
        slot = getSlot(self._s)

        # Find the pagelets
        pagelets = zapi.getAdapters((context, request, view, slot), IPagelet)
        pagelets = [pagelet for name, pagelet in pagelets
                    if canAccess(pagelet, '__call__')]
        pagelets.sort(lambda x, y: cmp(x.weight, y.weight))

        return pagelets


class TALESPageletExpression(StringExpr):
    """Collects a single pagelet via a TAL namespace called pagelet."""

    implements(ITALESPageletExpression)

    def __init__(self, name, expr, engine):
        if not '/' in expr:
            raise KeyError('Use `iface/pageletname` for defining the pagelet.')

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

        # get the slot from the expression
        slot = getSlot(self._iface)

        # Find the pagelets
        pagelet = zapi.queryMultiAdapter(
            (context, request, view, slot), IPagelet, name=self._name)

        if pagelet is None:
            raise ComponentLookupError(
                'No pagelet with name `%s` found.' %self._name)

        if not canAccess(pagelet, '__call__'):
            raise Unauthorized(
                'You are not authorized to access the pagelet '
                'called `%s`.' %self._name)

        return pagelet()
