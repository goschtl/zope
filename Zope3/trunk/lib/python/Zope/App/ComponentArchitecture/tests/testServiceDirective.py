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

from Zope.Exceptions import Forbidden, Unauthorized

from Zope.Configuration.xmlconfig import testxmlconfig as xmlconfig, XMLConfig
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Security.Proxy \
     import getTestProxyItems, getObject as proxiedObject, ProxyFactory

from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.App.ComponentArchitecture.tests.TestService \
     import IFooService, FooService

import Zope.App.ComponentArchitecture
from Zope.ComponentArchitecture import getService
from Zope.App.tests.PlacelessSetup import PlacelessSetup


template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""


class Test(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', Zope.App.ComponentArchitecture)()

    def testServiceConfigNoType(self):
        from Zope.ComponentArchitecture.GlobalServiceManager \
             import UndefinedService
        self.assertRaises(
            UndefinedService,
            xmlconfig,
            StringIO(template % (
            """
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.fooService"
              />
            """
            )))

    def testDuplicateServiceConfig(self):
        from Zope.Configuration.xmlconfig \
             import ZopeConflictingConfigurationError
        self.assertRaises(
            ZopeConflictingConfigurationError,
            xmlconfig,
            StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               Zope.App.ComponentArchitecture.tests.TestService.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.fooService"
              />
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.foo2"
              />
            """
            )))

    def testServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")
        
        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               Zope.App.ComponentArchitecture.tests.TestService.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.fooService"
              />
            """
            )))

        service = getService(None, "Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testServiceFactoryConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")
        
        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               Zope.App.ComponentArchitecture.tests.TestService.IFooService"
               />
            <service
              serviceType="Foo"
              factory="
              Zope.App.ComponentArchitecture.tests.TestService.FooService"
              />
            """
            )))

        service = getService(None, "Foo")
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertEqual(service.bar(), "you shouldn't get this")

    def testPublicProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")
        
        xmlconfig(StringIO(template % (
            """
            <serviceType id="Foo"
                         interface="
               Zope.App.ComponentArchitecture.tests.TestService.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.fooService"
              permission="Zope.Public"
              />
            """
            )))

        service = getService(None, "Foo")
        service = ProxyFactory(service) # simulate untrusted code!
        self.assertEqual(service.foo(), "foo here")
        self.assertEqual(service.foobar(), "foobarred")
        self.assertRaises(Forbidden, getattr, service, 'bar')

    def testProtectedServiceConfig(self):
        self.assertRaises(ComponentLookupError, getService, None, "Foo")
        
        xmlconfig(StringIO(template % (
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
              Zope.App.Security.Registries.metaConfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <serviceType id="Foo"
                         interface="
               Zope.App.ComponentArchitecture.tests.TestService.IFooService"
               />
            <service
              serviceType="Foo"
              component="
              Zope.App.ComponentArchitecture.tests.TestService.fooService"
              permission="XXX"
              />
            """
            )))


        # Need to "log someone in" to turn on checks
        from Zope.Security.SecurityManagement import newSecurityManager
        newSecurityManager('someuser')

        service = getService(None, "Foo")
        service = ProxyFactory(service) # simulate untrusted code!

        self.assertRaises(Unauthorized, getattr, service, 'foo')
        self.assertRaises(Unauthorized, getattr, service, 'foobar')
        self.assertRaises(Forbidden, getattr, service, 'bar')


    
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)
if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

