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

import unittest
import sys
import os
from cStringIO import StringIO

from zope.app.tests.placelesssetup import PlacelessSetup

from zope.app.workflow import globalimportexport
from zope.app.workflow.tests import directive_helpers

gIE = globalimportexport.globalImportExport
dh = directive_helpers

class PDA:

    __implements__ = dh.ITestProcessDefinitionA

class PDB:

    __implements__ = dh.ITestProcessDefinitionB




class Test(PlacelessSetup, unittest.TestCase):


    def setUp(self):
        PlacelessSetup.setUp(self)
        gIE.addImportHandler(dh.ITestProcessDefinitionA,
                             dh.TestImportHandlerA)
        gIE.addImportHandler(dh.ITestProcessDefinitionB,
                             dh.TestImportHandlerB)
        gIE.addExportHandler(dh.ITestProcessDefinitionA,
                             dh.TestExportHandlerA)
        gIE.addExportHandler(dh.ITestProcessDefinitionB,
                             dh.TestExportHandlerB)

    def testImportHandler(self):
        self.assertEqual(gIE.importProcessDefinition(None, 'A'),
                         'Imported A')
        self.assertEqual(gIE.importProcessDefinition(None, 'B'),
                         'Imported B')

        self.assertRaises(ValueError, gIE.importProcessDefinition, None, 'C')

    def testExportHandler(self):
        self.assertEqual(gIE.exportProcessDefinition(None, PDA()),
                         'Exported A')
        self.assertEqual(gIE.exportProcessDefinition(None, PDB()),
                         'Exported B')
        

        

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

