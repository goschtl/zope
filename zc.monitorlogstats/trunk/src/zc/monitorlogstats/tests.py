##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import datetime
import unittest
from zope.testing import doctest, setupstack

def setUp(test):

    class FauxDateTime:

        now = datetime.datetime(2008, 9, 5, 21, 10, 13)

        @classmethod
        def utcnow(self):
            self.now += datetime.timedelta(seconds=1)
            return self.now

    datetime_orig = datetime.datetime
    def restore():
        datetime.datetime = datetime_orig

    setupstack.register(test, restore)

    datetime.datetime = FauxDateTime

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=setupstack.tearDown),
        ))

