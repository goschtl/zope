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
##############################################################################
"""Test the workflow ZCML namespace directives.

$Id: test_directives.py,v 1.4 2003/08/01 20:41:05 srichter Exp $
"""
import unittest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig

from zope.app.workflow import globalimportexport
from zope.app.workflow.tests import directive_helpers

gIE = globalimportexport.globalImportExport


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.context = xmlconfig.file("workflow.zcml", directive_helpers)

    def testImportHandler(self):
        self.assertEqual(
            gIE._importers.get(directive_helpers.ITestProcessDefinitionA),
            directive_helpers.TestImportHandlerA)

    def testExportHandler(self):
        self.assertEqual(
            gIE._exporters.get(directive_helpers.ITestProcessDefinitionA),
            directive_helpers.TestExportHandlerA)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
