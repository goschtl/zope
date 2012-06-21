##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
"""Tests for z.c.interface
"""
import unittest


class Test_provideInterface(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.interface import provideInterface
        return provideInterface(*args, **kw)


class Test_getInterface(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.interface import getInterface
        return getInterface(*args, **kw)


class Test_queryInterface(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.interface import queryInterface
        return queryInterface(*args, **kw)


class Test_searchInterface(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.interface import searchInterface
        return searchInterface(*args, **kw)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_provideInterface),
        unittest.makeSuite(Test_getInterface),
        unittest.makeSuite(Test_queryInterface),
        unittest.makeSuite(Test_searchInterface),
    ))

