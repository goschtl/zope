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
import zope.component
from zope.testing import doctest
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.keyreference.interfaces import IKeyReference

import z3c.testing
from z3c.indexer import interfaces
from z3c.indexer import testing
from z3c.indexer import index
from z3c.indexer import indexer
from z3c.indexer import query
from z3c.indexer import search


class FakeKeyReference(object):
    """Fake keyref for testing"""
    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return id(self.object)

    def __cmp__(self, other):
        return cmp(id(self.object), id(other.object))


class ValueIndexerStub(indexer.ValueIndexer):
    value = u'ignored'

# IIndex
class TestTextIndex(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ITextIndex

    def getTestClass(self):
        return index.TextIndex


class TestFieldIndex(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IFieldIndex

    def getTestClass(self):
        return index.FieldIndex


class TestValueIndex(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IValueIndex

    def getTestClass(self):
        return index.ValueIndex


class TestSetIndex(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISetIndex

    def getTestClass(self):
        return index.SetIndex


# IIndexer
class TestValueIndexer(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        zope.component.provideAdapter(FakeKeyReference, (None,), IKeyReference)
        intids = IntIds()
        zope.component.provideUtility(intids, IIntIds)
        intids.register(None)
        valueIndex = index.ValueIndex()
        zope.component.provideUtility(valueIndex, interfaces.IIndex)

    def getTestInterface(self):
        return interfaces.IValueIndexer

    def getTestClass(self):
        return ValueIndexerStub

    def getTestPos(self):
        return (None,)


class TestMultiIndexer(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IIndexer

    def getTestClass(self):
        return indexer.MultiIndexer

    def getTestPos(self):
        return (None,)


class TestTextQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ITextQuery

    def getTestClass(self):
        return query.TextQuery

    def getTestPos(self):
        return (None, None)


class TestEqQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IEqQuery

    def getTestClass(self):
        return query.Eq

    def getTestPos(self):
        return (None, 'not None')


class TestNotEqQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.INotEqQuery

    def getTestClass(self):
        return query.NotEq

    def getTestPos(self):
        return (None, 'not None')


class TestBetweenQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IBetweenQuery

    def getTestClass(self):
        return query.Between

    def getTestPos(self):
        return (None, None, None)


class TestGeQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IGeQuery

    def getTestClass(self):
        return query.Ge

    def getTestPos(self):
        return (None, None)


class TestLeQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ILeQuery

    def getTestClass(self):
        return query.Le

    def getTestPos(self):
        return (None, None)


class TestInQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IInQuery

    def getTestClass(self):
        return query.In

    def getTestPos(self):
        return (None, None)


class TestAnyOfQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IAnyOfQuery

    def getTestClass(self):
        return query.AnyOf

    def getTestPos(self):
        return (None, None)


class TestAllOfQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IAllOfQuery

    def getTestClass(self):
        return query.AllOf

    def getTestPos(self):
        return (None, None)


class TestExtentAnyQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IExtentAnyQuery

    def getTestClass(self):
        return query.ExtentAny

    def getTestPos(self):
        return (None, None)


class TestExtentNoneQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IExtentNoneQuery

    def getTestClass(self):
        return query.ExtentNone

    def getTestPos(self):
        return (None, None)


class TestSearchQuery(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISearchQuery

    def getTestClass(self):
        return search.SearchQuery


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestTextIndex),
        unittest.makeSuite(TestFieldIndex),
        unittest.makeSuite(TestValueIndex),
        unittest.makeSuite(TestSetIndex),
        unittest.makeSuite(TestValueIndexer),
        unittest.makeSuite(TestMultiIndexer),
        unittest.makeSuite(TestTextQuery),
        unittest.makeSuite(TestEqQuery),
        unittest.makeSuite(TestNotEqQuery),
        unittest.makeSuite(TestBetweenQuery),
        unittest.makeSuite(TestGeQuery),
        unittest.makeSuite(TestLeQuery),
        unittest.makeSuite(TestInQuery),
        unittest.makeSuite(TestAnyOfQuery),
        unittest.makeSuite(TestExtentAnyQuery),
        unittest.makeSuite(TestExtentNoneQuery),
        unittest.makeSuite(TestSearchQuery),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
