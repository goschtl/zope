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
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.Security.SecurityManagement import newSecurityManager, system_user

import Zope.App.Security
from Zope.App.Security.Exceptions import UndefinedPermissionError

import Zope.App.ContentDirective
from Zope.App.ContentDirective.tests.ExampleClass \
    import ExampleClass, IExample, IExampleContainer

def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'>
      %s
      </zopeConfigure>
      """ % s)

class Test(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)
        newSecurityManager(system_user)
        XMLConfig('meta.zcml', Zope.App.ContentDirective)()
        XMLConfig('meta.zcml', Zope.App.Security)()


    def testFactory(self):
        from Zope.ComponentArchitecture import getService
        from Zope.Proxy.ProxyIntrospection import removeAllProxies
        f = configfile("""
<permission id="Zope.Foo" title="Zope Foo Permission" />
<content class="Zope.App.ContentDirective.tests.ExampleClass.">
    <factory 
      id="Example" 
      permission="Zope.Foo"
      title="Example content"
      description="Example description"
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
    <factory 
      permission="Zope.Foo"
      title="Example content"
      description="Example description"
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



