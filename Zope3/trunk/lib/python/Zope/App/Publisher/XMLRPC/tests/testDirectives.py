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

$Id: testDirectives.py,v 1.3 2002/06/20 15:54:58 jim Exp $
"""

import unittest

from Zope.Configuration.xmlconfig import xmlconfig, XMLConfig
from Zope.Configuration.Exceptions import ConfigurationError
from Zope.ComponentArchitecture.tests.TestViews import IC, V1, VZMI, R1, RZMI
from Zope.ComponentArchitecture import getView, queryView
from Zope.ComponentArchitecture import getDefaultViewName
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Security.Proxy import ProxyFactory
from cStringIO import StringIO

from Zope.ComponentArchitecture.tests.Request import Request

from Zope.Publisher.XMLRPC.IXMLRPCPresentation import IXMLRPCPresentation

import Zope.App.Publisher.XMLRPC

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:xmlrpc='http://namespaces.zope.org/xmlrpc'>
   %s
   </zopeConfigure>"""

request = Request(IXMLRPCPresentation)

class Ob:
    __implements__ = IC

ob = Ob()

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', Zope.App.Publisher.XMLRPC)()

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" /> 
            """
            ))) 
        
        self.assertEqual(
            queryView(ob, 'test', request).__class__,
            V1)
         
    def testDefaultView(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <xmlrpc:defaultView name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" /> 
            """
            ))) 

        self.assertEqual(queryView(ob, 'test',
                                   request, None
                                 ).__class__, V1)
        self.assertEqual(getDefaultViewName(ob, request
                                 ), 'test')
                                 

    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="Zope.Public"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')


    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="Zope.Public"
                  allowed_attributes="action"
                  /> 
            """
            ))

        v = getView(ob, 'test', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')


    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="Zope.Public"
                  allowed_attributes="action"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')


    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="Zope.Public"
                  allowed_attributes="action index"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')


    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  allowed_attributes="action index"
                  /> 
            """
            ))


    def testMethodViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <xmlrpc:view
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC">

                <xmlrpc:method name="index.html" attribute="index" /> 
                <xmlrpc:method name="action.html" attribute="action" /> 
            </xmlrpc:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')

    def testMethodViewsWithName(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <xmlrpc:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC">

                <xmlrpc:method name="index.html" attribute="index" /> 
                <xmlrpc:method name="action.html" attribute="action" /> 
            </xmlrpc:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')
    

    def testProtectedMethodViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/zope">
              <directive name="permission"
                 attributes="id title description"
                 handler="
               Zope.App.Security.Registries.metaConfigure.definePermission" />
            </directives>

            <permission id="XXX" title="xxx" />

            <xmlrpc:view
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="XXX">

                <xmlrpc:method name="index.html" attribute="index" /> 
                <xmlrpc:method name="action.html" attribute="action"
                              permission="Zope.Public" /> 
            </xmlrpc:view>
            """
            ))

        # Need to "log someone in" to turn on checks
        from Zope.Security.SecurityManagement import newSecurityManager
        newSecurityManager('someuser')

        v = getView(ob, 'index.html', request)
        self.assertRaises(Exception, v)
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
