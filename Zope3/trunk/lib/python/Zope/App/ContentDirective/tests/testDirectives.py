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

$Id: testDirectives.py,v 1.4 2002/06/20 15:54:46 jim Exp $
"""

import unittest
import sys
import os
from StringIO import StringIO

from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from Zope.Configuration.xmlconfig import xmlconfig, XMLConfig
from Zope.Configuration.xmlconfig import ZopeXMLConfigurationError

import Zope.App.Security

import Zope.App.ContentDirective

# explicitly import ExampleClass and IExample using full paths
# so that they are the same objects as resolve will get.
from Zope.App.ContentDirective.tests.ExampleClass import ExampleClass, IExample


def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'
      xmlns:zmi='http://namespaces.zope.org/zmi'>
      %s
      </zopeConfigure>
      """ % s)

class TestContentDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        XMLConfig('meta.zcml', Zope.App.ContentDirective)()
        XMLConfig('meta.zcml', Zope.App.Security)()
        
        try:
            del ExampleClass.__implements__
        except AttributeError:
            pass
            
    def testEmptyDirective(self):
        f = configfile("""
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
</content>
                       """)
        xmlconfig(f)

            
    def testImplements(self):
        f = configfile("""
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
  <implements interface="Zope.App.ContentDirective.tests.ExampleClass.IExample" />
</content>
                       """)
        xmlconfig(f)
        self.failUnless(IExample.isImplementedByInstancesOf(ExampleClass))
        
        
    def testRequire(self):
        f = configfile("""
<permission id="Zope.View" title="Zope view permission" />
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <require permission="Zope.View"
                      attributes="anAttribute anotherAttribute" />
</content>
                       """)
        xmlconfig(f)

    def testAllow(self):
        f = configfile("""
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <allow attributes="anAttribute anotherAttribute" />
</content>
                       """)
        xmlconfig(f)
        
    def testMimic(self):
        f = configfile("""
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <require like_class="Zope.App.ContentDirective.tests.ExampleClass." />
</content>
                       """)
        xmlconfig(f)
        
        
from Zope.App.OFS.Services.AddableService.tests.AddableSetup \
    import AddableSetup

class TestFactorySubdirective(AddableSetup, CleanUp, unittest.TestCase):
    def setUp(self):
        AddableSetup.setUp(self)
        XMLConfig('meta.zcml', Zope.App.ContentDirective)()
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testFactory(self):
        f = configfile("""
<permission id="Zope.Foo" title="Zope Foo Permission" />

<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <zmi:factory 
      id="Example" 
      permission="Zope.Foo"
      title="Example content"
      description="Example description"
      for_container="Zope.App.ContentDirective.tests.ExampleClass."
      creation_markers="Zope.App.ContentDirective.tests.ExampleClass.IExample"
       />
</content>
                       """)
        xmlconfig(f)

def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestContentDirective))
    suite.addTest(loader.loadTestsFromTestCase(TestFactorySubdirective))
    return suite


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
