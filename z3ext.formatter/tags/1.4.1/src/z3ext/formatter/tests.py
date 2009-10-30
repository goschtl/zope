##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
""" z3ext.formatter tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope import interface, schema
from zope.component import provideAdapter
from zope.testing.cleanup import cleanUp
from zope.app.testing import setup

from zope.pagetemplate.pagetemplate import PageTemplate
from zope.app.pagetemplate.engine import Engine, TrustedEngine, TrustedAppPT
from zope.app.pagetemplate.metaconfigure import clear

from z3ext.controlpanel.testing import setUpControlPanel

from z3ext.formatter import \
    dformatter, dtformatter, fancydatetime, timeformatter, humandatetime
from z3ext.formatter.expression import FormatterExpression


class ZPTPage(TrustedAppPT, PageTemplate):

    def render(self, request, *args, **kw):
        namespace = self.pt_getContext(args, kw)
        namespace['request'] = request
        return self.pt_render(namespace)


def setUp(test):
    setup.placefulSetUp(True)
    setup.setUpTraversal()
    setUpControlPanel()

    Engine.registerType(u'formatter', FormatterExpression)
    TrustedEngine.registerType(u'formatter', FormatterExpression)

    provideAdapter(dformatter.DateFormatterFactory, name='date')
    provideAdapter(dtformatter.DatetimeFormatterFactory, name='dateTime')
    provideAdapter(
        fancydatetime.FancyDatetimeFormatterFactory, name='fancyDatetime')
    provideAdapter(
        humandatetime.HumanDatetimeFormatterFactory, name='humanDatetime')
    provideAdapter(timeformatter.TimeFormatterFactory, name='time')


def tearDown(test):
    setup.placelessTearDown()
    clear()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
