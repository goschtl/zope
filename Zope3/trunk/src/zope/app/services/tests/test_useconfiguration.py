##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""
$Id: test_useconfiguration.py,v 1.2 2003/03/03 23:16:14 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.configuration import UseConfiguration
from zope.app.interfaces.annotation import IAnnotations
from zope.app.tests.placelesssetup import PlacelessSetup

class C(dict):
    __implements__ = IAnnotations

class TestUseConfiguration(PlacelessSetup, TestCase):

    def testVerifyInterface(self):
        from zope.interface.verify import verifyObject
        from zope.app.interfaces.services.configuration import IUseConfiguration
        obj = UseConfiguration(C())
        verifyObject(IUseConfiguration, obj)

    def test(self):
        obj = UseConfiguration(C())
        self.failIf(obj.usages())
        obj.addUsage('/a/b')
        obj.addUsage('/c/d')
        obj.addUsage('/c/e')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/d', '/c/e'])
        obj.removeUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/e'])

def test_suite():
    return TestSuite((
        makeSuite(TestUseConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
