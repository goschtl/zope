##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
import datetime
import zope.interface
import zope.component
from zope.dublincore.interfaces import IZopeDublinCore
from zope.testing import doctest
from zope.publisher.browser import TestRequest
from zope.security import checker
from zope.app.testing import setup

import z3c.testing
from z3c.table import testing
from z3c.table import interfaces
from z3c.table import table
from z3c.table import column


# table
class TestTable(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.Table

    def getTestPos(self):
        return ({}, TestRequest())


# column
class TestColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.Column

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNoneCell(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.INoneCell

    def getTestClass(self):
        return column.NoneCell

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestNameColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.NameColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestRadioColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.RadioColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


class TestCheckBoxColumn(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IColumn

    def getTestClass(self):
        return column.CheckBoxColumn

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        return ({}, TestRequest(), t)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('column.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestTable),
        unittest.makeSuite(TestColumn),
        unittest.makeSuite(TestNoneCell),
        unittest.makeSuite(TestNameColumn),
        unittest.makeSuite(TestRadioColumn),
        unittest.makeSuite(TestCheckBoxColumn),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
