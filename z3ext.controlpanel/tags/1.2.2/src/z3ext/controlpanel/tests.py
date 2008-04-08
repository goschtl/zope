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
""" z3ext Control Panel tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope import interface, schema
from zope.app.testing import setup
from z3ext.controlpanel.configlet import Configlet
from z3ext.controlpanel.testing import setUpControlPanel

def testConfiglet1(configlet):
    return True

def testConfiglet2(configlet):
    return False


class ITestConfiglet1(interface.Interface):
    
    param1 = schema.TextLine(
        title = u'param1',
        default = u'default param1')

    param2 = schema.Int(
        title = u'param2',
        default = 10)


class ITestConfiglet2(interface.Interface):

    param1 = schema.TextLine(
        title = u'param1',
        default = u'default param1')

    param2 = schema.Int(
        title = u'param2',
        default = 10)

    param3 = schema.TextLine(
        title = u'param3',
        default = u'default param3')


class TestConfiglet1(Configlet):
    pass


class TestConfiglet2(object):
    pass


def setUp(test):
    setup.placefulSetUp(True)
    setUpControlPanel()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=setup.placefulTearDown(),
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'z3ext.controlpanel.configlettype',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
