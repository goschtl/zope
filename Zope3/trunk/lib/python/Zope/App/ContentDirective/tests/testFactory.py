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
""" Test handler for 'factory' subdirective of 'content' directive """

import unittest
import sys
import os
from cStringIO import StringIO

from Zope.Configuration.xmlconfig import xmlconfig, ZopeXMLConfigurationError
from Zope.Configuration.xmlconfig import XMLConfig

from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

import Zope.App.Security
from Zope.App.Security.Exceptions import UndefinedPermissionError

from Zope.App.OFS.Services.AddableService.tests.AddableSetup \
    import AddableSetup

import Zope.App.ContentDirective
from Zope.App.ContentDirective.tests.ExampleClass \
    import ExampleClass, IExample, IExampleContainer

def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'
      xmlns:zmi='http://namespaces.zope.org/zmi'>
      %s
      </zopeConfigure>
      """ % s)

class Test(AddableSetup, CleanUp, unittest.TestCase):
    def setUp(self):
        AddableSetup.setUp(self)
        XMLConfig('meta.zcml', Zope.App.ContentDirective)()
        XMLConfig('meta.zcml', Zope.App.Security)()


    def testFactory(self):
        from Zope.ComponentArchitecture import getService
        from Zope.Proxy.ProxyIntrospection import removeAllProxies
        f = configfile("""
<permission id="Zope.Foo" title="Zope Foo Permission" />
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <zmi:factory 
      id="Example" 
      permission="Zope.Foo"
      title="Example content"
      description="Example description"
      for_container="Zope.App.ContentDirective.tests.ExampleClass.IExampleContainer"
      creation_markers="Zope.App.ContentDirective.tests.ExampleClass.IExample"
       />
</content>
                       """)
        xmlconfig(f)
        obj = getService(None, "Factories").createObject('Example')
        obj = removeAllProxies(obj)
        self.failUnless(isinstance(obj, ExampleClass))

    def testFactoryDefaultId(self):
        from Zope.ComponentArchitecture import getService
        from Zope.Proxy.ProxyIntrospection import removeAllProxies
        f = configfile("""
<permission id="Zope.Foo" title="Zope Foo Permission" />
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <zmi:factory 
      permission="Zope.Foo"
      title="Example content"
      description="Example description"
      for_container="Zope.App.ContentDirective.tests.ExampleClass.IExampleContainer"
      creation_markers="Zope.App.ContentDirective.tests.ExampleClass.IExample"
       />
</content>
                       """)
        xmlconfig(f)
        obj = getService(None, "Factories").createObject(
            'Zope.App.ContentDirective.tests.ExampleClass.')
        obj = removeAllProxies(obj)
        self.failUnless(isinstance(obj, ExampleClass))


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())



