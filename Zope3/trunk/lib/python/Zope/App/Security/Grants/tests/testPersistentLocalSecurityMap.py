##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################
import unittest
from Interface.Verify import verifyClass
from Zope.App.Security.Grants.ILocalSecurityMap import ILocalSecurityMap
from Zope.App.Security.Grants.PersistentLocalSecurityMap import PersistentLocalSecurityMap
from Zope.App.Security.Grants.tests.testLocalSecurityMap import \
     TestLocalSecurityMap

class TestPersistentLocalSecurityMap(TestLocalSecurityMap):

    def testInterface(self):
        verifyClass(ILocalSecurityMap, PersistentLocalSecurityMap)

    # XXX test persistence...


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestPersistentLocalSecurityMap)

if __name__ == '__main__':
    unittest.main()
