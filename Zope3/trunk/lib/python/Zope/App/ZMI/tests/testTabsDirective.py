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
"""

$Id: testTabsDirective.py,v 1.2 2002/06/10 23:29:19 jim Exp $
"""

import unittest, sys


from StringIO import StringIO

from Zope.App.ZMI.ZMIViewService import ZMIViews
from Zope.Configuration.xmlconfig import xmlconfig
from Zope.Configuration.xmlconfig import ZopeXMLConfigurationError

from Interface import Interface

from Zope.App.ZMI.tests.sampleInterfaces import *

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup
from Zope.ComponentArchitecture import getService

class Test(PlacefulSetup, unittest.TestCase):

    #XXX we should have a test for multiple inheritance interface
    # hierarchies.

    def testZMITabDirective(self):
        xmlconfig( StringIO("""
        <zopeConfigure
          xmlns='http://namespaces.zope.org/zope'
          xmlns:zmi='http://namespaces.zope.org/zmi'>

          <directive name="tabs" attributes="for" 
             namespace="http://namespaces.zope.org/zmi"
             handler="Zope.App.ZMI.TabsDirective.">
            <subdirective name="tab" attributes="label action filter" />
          </directive>
          <zmi:tabs for="Zope.App.ZMI.tests.sampleInterfaces.I1">
            <zmi:tab label="Edit" action="edit" />
            <zmi:tab label="History" action="history" />
          </zmi:tabs>
          <zmi:tabs for="Zope.App.ZMI.tests.sampleInterfaces.I2">
            <zmi:tab label="Update" action="update_magic" />
            <zmi:tab label="Organize" action="organize_magic" />
          </zmi:tabs>

        </zopeConfigure>        
        """))

        getService(None,"Adapters").provideAdapter(
            I1, ITraverser, FakeTraverser)
        
        self.assertEqual(list(ZMIViews.getViews(O2())),
                         [
                          ('Update', 'update_magic'),
                          ('Organize', 'organize_magic'),
                          ('Edit', 'edit'),
                          ('History', 'history')
                          ]
                         )


    def testZMITabDirectiveWithFilters(self):
        
        xmlconfig( StringIO("""
        <zopeConfigure
        xmlns='http://namespaces.zope.org/zope'
        xmlns:zmi='http://namespaces.zope.org/zmi'>
          <directive name="tabs" attributes="for" 
            namespace="http://namespaces.zope.org/zmi"
            handler="Zope.App.ZMI.TabsDirective.">
            <subdirective name="tab" attributes="label action filter" />
          </directive>
          <zmi:tabs for="Zope.App.ZMI.tests.sampleInterfaces.I1">
            <zmi:tab label="Edit" action="edit" />
            <zmi:tab label="History" action="history" filter="python: 1==2" />
          </zmi:tabs>
          <zmi:tabs for="Zope.App.ZMI.tests.sampleInterfaces.I2">
            <zmi:tab label="Update" action="update_magic" />
            <zmi:tab label="Organize" action="organize_magic" />
          </zmi:tabs>
        </zopeConfigure>        
        """))

        getService(None,"Adapters").provideAdapter(
            I1, ITraverser, FakeTraverser)

        self.assertEqual(list(ZMIViews.getViews(O2())),
                         [
                          ('Update', 'update_magic'),
                          ('Organize', 'organize_magic'),
                          ('Edit', 'edit'),
                          ]
                         )
        
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

