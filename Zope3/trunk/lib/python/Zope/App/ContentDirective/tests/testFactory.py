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

import unittest, sys, os

from cStringIO import StringIO
from Zope.Configuration.xmlconfig import xmlconfig, ZopeXMLConfigurationError
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from Zope.App.Security.Exceptions import UndefinedPermissionError
from Zope.App.OFS.Services.AddableService.tests.AddableSetup \
    import AddableSetup

from Zope.App.ContentDirective.tests.ExampleClass \
    import ExampleClass, IExample, IExampleContainer

import Zope.App.ContentDirective
defs_path = os.path.join(
    os.path.split(Zope.App.ContentDirective.__file__)[0],
    'content-meta.zcml')

import Zope.App.Security
security_defs_path = os.path.join(
    os.path.split(Zope.App.Security.__file__)[0],
    'security-meta.zcml')


def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'
      xmlns:security='http://namespaces.zope.org/security'
      xmlns:zmi='http://namespaces.zope.org/zmi'>
      %s
      </zopeConfigure>
      """ % s)

class Test(AddableSetup, CleanUp, unittest.TestCase):
    def setUp(self):
        AddableSetup.setUp(self)
        xmlconfig(open(defs_path))
        xmlconfig(open(security_defs_path))


    def testFactory(self):
        from Zope.ComponentArchitecture import getService
        from Zope.Proxy.ProxyIntrospection import removeAllProxies
        f = configfile("""
<security:permission id="Zope.Foo" title="Zope Foo Permission" />
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
<security:permission id="Zope.Foo" title="Zope Foo Permission" />
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



