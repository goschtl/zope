##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""ZWiki Tests

$Id$
"""
import unittest

from zope.app.container.tests.test_icontainer import \
     BaseTestIContainer, DefaultTestData

from zwiki.wiki import Wiki
from zwiki.interfaces import IWiki


class Test(BaseTestIContainer, unittest.TestCase):

    def makeTestObject(self):
        return Wiki()

    def makeTestData(self):
        return DefaultTestData()

    def test_interface(self):
        self.assert_(IWiki.providedBy(self.makeTestObject()))

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return ['foo'], ('bar',), 20, 12.8

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
