##############################################################################
#
# Copyright) 2001, 2002 Zope Corporation and Contributors.
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
"""Test FSRegistry File-system synchronization utilities

$Id$
"""
import unittest

from zope.app.fssync.fsregistry import getSynchronizer
from zope.app.fssync.tests.sampleclass import \
     C1, C2, CDirAdapter, CDefaultAdapter
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationConflictError
from zope.exceptions import NotFoundError
import zope.app.fssync.tests


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testFSDirective(self):
        # Register the adapter for the class
        self.assertRaises(NotFoundError, getSynchronizer, C2())
        self.context = xmlconfig.file("fssync.zcml", zope.app.fssync.tests)
        self.assertEqual(getSynchronizer(C2()).__class__, CDirAdapter)

    def testFSDirectiveDefaultAdapter(self):
        self.context = xmlconfig.file("fssync.zcml", zope.app.fssync.tests)
        self.assertEqual(getSynchronizer(C1()).__class__, CDefaultAdapter)

    def testFSDirectiveDuplicate(self):
        self.assertRaises(ConfigurationConflictError, xmlconfig.file,
                          "fssync_duplicate.zcml", zope.app.fssync.tests)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
