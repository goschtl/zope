##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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

from zope.app.pagetemplate.engine import Engine, TrustedEngine
from zope.app.pagetemplate.metaconfigure import clear

from z3ext.controlpanel.testing import setUpControlPanel

from z3ext.formatter import dformatter, dtformatter, fancydatetime
from z3ext.formatter.expression import FormatterExpression


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


def tearDown(test):
    setup.placelessTearDown()
    clear()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'config.txt', setUp=setUp, tearDown=tearDown),
            ))
