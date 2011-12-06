##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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


class DummyDatabaseConnection:

    def __init__(self):
        self.am = DummyActivityMonitor()

    def db(self):
        return self

    def getActivityMonitor(self):
        pass


class DummyDatabaseObject:

    def __init__(self):
        self._p_jar = DummyDatabaseConnection()


class DummyActivityMonitor:

    def getHistoryLength(self):
        pass

    def getActivityAnalysis(start=None, end=None, divisions=None):
        pass


class Tests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _getTargetClass(self):
        from zmi.core.browser.database.activity import View
        return View

    def _makeOne(self):
        root = DummyDatabaseObject()
        view = self._getTargetClass()
        return view(root, {})

    def test_db(self):
        view = self._makeOne()
        return True


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))