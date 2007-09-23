##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for import/export step zcml module.
"""
import unittest
from Products.GenericSetup.zcml import cleanUpImportSteps
#import Products.GenericSetup
from Products.GenericSetup.registry import _import_step_registry
from Products.GenericSetup.testing import ExportImportZCMLLayer
#from Products.Five import zcml

EMPTY_ZCML = '''<configure xmlns:genericsetup="http://namespaces.zope.org/genericsetup">
</configure>'''


class ImportStepTests(unittest.TestCase):
    layer = ExportImportZCMLLayer

#    def setUp(self):
#        zcml.load_config('meta.zcml', Products.GenericSetup)

    def tearDown(self):
        cleanUpImportSteps()

    def testEmptyImport(self):
        zcml.load_string(EMPTY_ZCML)
        self.assertEqual(_import_step_registry._registry, {})

    def testFail(self):
        self.fail()


def test_suite():
    return unittest.TestSuite((
        unittest.MakeSuite(ImportStepTests),
        ))

if __name__ == '__main__':
    from Products.GenericSetup.testing import run
    run(test_suite())
