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
import doctest

from zope.interface import Interface
from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import z3c.testing
from z3c.batching.batch import Batch
from z3c.table import testing
from z3c.table import interfaces
from z3c.table import table
from z3c.table import column
from z3c.table import batch
from z3c.table import value


class FakeContainer(object):

    def values(self):
        pass

    def __len__(self):
        return 0


# table
class TestTable(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.Table

    def getTestPos(self):
        return (FakeContainer(), TestRequest())


class TestSequenceTable(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.ITable

    def getTestClass(self):
        return table.SequenceTable

    def getTestPos(self):
        return ([], TestRequest())


# values
class TestValuesForContainer(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.IValues

    def getTestClass(self):
        return value.ValuesForContainer

    def getTestPos(self):
        container = FakeContainer()
        request = TestRequest()
        tableInstance = table.Table(container, request)
        return (container, request, tableInstance)


class TestValuesForSequence(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        testing.setUpAdapters()

    def getTestInterface(self):
        return interfaces.IValues

    def getTestClass(self):
        return value.ValuesForSequence

    def getTestPos(self):
        container = FakeContainer()
        request = TestRequest()
        tableInstance = table.Table(container, request)
        return (container, request, tableInstance)


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
        return ()


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


# batch
class TestBatchProvider(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IBatchProvider

    def getTestClass(self):
        return batch.BatchProvider

    def getTestPos(self):
        t = table.Table(None, TestRequest())
        t.rows = Batch([])
        return ({}, TestRequest(), t)


class NumberColumn(column.Column):

    weight = 10
    header = u'Number'

    def renderCell(self, item):
        return item


SORT_ON_ID = "table-number-1"


def sortedValues(valuesAreSorted):

    class SortedValues(value.ValuesForSequence):

        sortOn = SORT_ON_ID
        isSorted = valuesAreSorted

    return SortedValues


def withIValuesAdapter(klass):

    def decorator(func):

        def decorated(self):
            self.sm.registerAdapter(klass,
                (Interface, IBrowserRequest, interfaces.ISequenceTable),
                interfaces.IValues)
            func(self)
            self.sm.unregisterAdapter(klass,
                (Interface, IBrowserRequest, interfaces.ISequenceTable),
                interfaces.IValues)
        return decorated
    return decorator


class TestSortedValues(unittest.TestCase):

    def setUp(self):
        self.sm = sm = getSiteManager()
        sm.registerAdapter(table.RowsSetUp,
            (interfaces.ITable, None),
            interfaces.IRowsSetUp)
        sm.registerAdapter(NumberColumn,
            (None, None, interfaces.ITable),
            interfaces.IColumn, name='number')

    @withIValuesAdapter(sortedValues(True))
    def testHasSortedValuesRightCriteria(self):
        request = TestRequest(form={'table-sortOn': 'table-number-1'})
        tableInstance = table.SequenceTable([1], request)
        tableInstance.update()
        self.failUnless(tableInstance.hasSortedValues)
        self.assertEquals(tableInstance.valuesSortedOn, SORT_ON_ID)
        self.failIf(tableInstance._mustSort())

    @withIValuesAdapter(sortedValues(True))
    def testHasSortedValuesWrongCriteria(self):
        request = TestRequest(form={'table-sortOn': 'table-number-2'})
        tableInstance = table.SequenceTable([1], request)
        tableInstance.update()
        self.failUnless(tableInstance.hasSortedValues)
        self.assertNotEquals(tableInstance.sortOn, SORT_ON_ID)
        self.assertEquals(tableInstance.valuesSortedOn, SORT_ON_ID)
        self.failUnless(tableInstance._mustSort())

    @withIValuesAdapter(sortedValues(False))
    def testHasNoSortedValues(self):
        request = TestRequest(form={'table-sortOn': 'table-number-2'})
        tableInstance = table.SequenceTable([1], request)
        tableInstance.update()
        self.failIf(tableInstance.hasSortedValues)
        self.failUnless(tableInstance._mustSort())


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('sequence.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('sort.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('batch.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS |
                doctest.REPORT_UDIFF),
            ),
        doctest.DocFileSuite('miscellaneous.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('column.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestTable),
        unittest.makeSuite(TestSequenceTable),
        unittest.makeSuite(TestValuesForContainer),
        unittest.makeSuite(TestValuesForSequence),
        unittest.makeSuite(TestSortedValues),
        unittest.makeSuite(TestColumn),
        unittest.makeSuite(TestNoneCell),
        unittest.makeSuite(TestNameColumn),
        unittest.makeSuite(TestRadioColumn),
        unittest.makeSuite(TestCheckBoxColumn),
        unittest.makeSuite(TestBatchProvider),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
