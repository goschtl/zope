##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import unittest
import doctest

import z3c.testing
from z3c.searcher import interfaces
from z3c.searcher import testing
from z3c.searcher import criterium
from z3c.searcher import filter


# ISearchCriterium
class TestSearchCriterium(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISearchCriterium

    def getTestClass(self):
        return criterium.SearchCriterium


class TestSetSearchCriterium(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISearchCriterium

    def getTestClass(self):
        return criterium.SetSearchCriterium


class TestTextCriterium(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ITextCriterium

    def getTestClass(self):
        return criterium.TextCriterium


# ISearchFilter
class TestSearchFilter(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.ISearchFilter

    def getTestClass(self):
        return filter.SearchFilter


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        unittest.makeSuite(TestSearchCriterium),
        unittest.makeSuite(TestSetSearchCriterium),
        unittest.makeSuite(TestTextCriterium),
        unittest.makeSuite(TestSearchFilter),
        ))
