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

from zope.configuration.xmlconfig import xmlconfig, XMLConfig

import zope.configuration
import zope.app.workflow

from zope.app.workflow import globalimportexport
from zope.app.workflow.tests import directive_helpers

gIE = globalimportexport.globalImportExport


template = """<zopeConfigure
   xmlns:test='http://namespaces.zope.org/workflow'>
   %s
   </zopeConfigure>"""


class Test(PlacelessSetup, unittest.TestCase):


    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.workflow)()

    def testImportHandler(self):

        xmlconfig(StringIO(template % (
            """
            <test:importHandler
             interface="zope.app.workflow.tests.directive_helpers.ITestProcessDefinitionA"
             factory="zope.app.workflow.tests.directive_helpers.TestImportHandlerA"
            />
            """
            )))

        self.assertEqual(directive_helpers.TestImportHandlerA,
                         gIE._importers.get(directive_helpers.ITestProcessDefinitionA))

    def testExportHandler(self):

        xmlconfig(StringIO(template % (
            """
            <test:exportHandler
             interface="zope.app.workflow.tests.directive_helpers.ITestProcessDefinitionA"
             factory="zope.app.workflow.tests.directive_helpers.TestExportHandlerA"
            />
            """
            )))

        self.assertEqual(directive_helpers.TestExportHandlerA,
                         gIE._exporters.get(directive_helpers.ITestProcessDefinitionA))


        

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
