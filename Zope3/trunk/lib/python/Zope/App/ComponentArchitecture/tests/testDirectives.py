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

from Zope.Configuration.xmlconfig import xmlconfig
from Zope.Configuration.Exceptions import ConfigurationError

from Zope.Security.Proxy import getTestProxyItems, getObject as proxiedObject

from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.ComponentArchitecture \
     import getView, queryView, getResource, queryResource, createObject
from Zope.ComponentArchitecture import getDefaultViewName

from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.tests.TestViews import \
     IV, IC, V1, VZMI, R1, RZMI
from Zope.ComponentArchitecture.tests.Request import Request

import Zope.App.ComponentArchitecture
defs_path = os.path.join(
    os.path.split(Zope.App.ComponentArchitecture.__file__)[0],
    'meta.zcml')

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:security='http://namespaces.zope.org/security'>
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""

class Ob:
    __implements__ = IC

class Test(PlacelessSetup, unittest.TestCase):

    # XXX: tests for other directives needed

    def setUp(self):
        PlacelessSetup.setUp(self)
        xmlconfig(open(defs_path))

    def testAdapter(self):
        from Zope.ComponentArchitecture import getAdapter, queryAdapter

        # Full import is critical!
        from Zope.ComponentArchitecture.tests.TestComponents \
             import Content, IApp, Comp
             
        self.assertEqual(queryAdapter(Content(), IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="Zope.ComponentArchitecture.tests.TestComponents.Comp"
              provides="Zope.ComponentArchitecture.tests.TestComponents.IApp"
              for="Zope.ComponentArchitecture.tests.TestComponents.IContent"
              />
            """
            ))) 
        
        self.assertEqual(getAdapter(Content(), IApp).__class__, Comp)

    def testProtectedAdapter(self):
        from Zope.ComponentArchitecture import getAdapter, queryAdapter

        # Full import is critical!
        from Zope.ComponentArchitecture.tests.TestComponents \
             import Content, IApp, Comp
             
        self.assertEqual(queryAdapter(Content(), IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <adapter
              factory="Zope.ComponentArchitecture.tests.TestComponents.Comp"
              provides="Zope.ComponentArchitecture.tests.TestComponents.IApp"
              for="Zope.ComponentArchitecture.tests.TestComponents.IContent"
              permission="Zope.Public"
              />
            """
            ))) 
        
        adapter = getAdapter(Content(), IApp)
        items = [item[0] for item in getTestProxyItems(adapter)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(proxiedObject(adapter).__class__, Comp)

    def testUtility(self):
        from Zope.ComponentArchitecture import getUtility, queryUtility

        # Full import is critical!
        from Zope.ComponentArchitecture.tests.TestComponents \
             import IApp, comp
             
        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="Zope.ComponentArchitecture.tests.TestComponents.comp"
              provides="Zope.ComponentArchitecture.tests.TestComponents.IApp"
              />
            """
            ))) 
        
        self.assertEqual(getUtility(None, IApp), comp)

    def testUtilityFactory(self):
        from Zope.ComponentArchitecture import getUtility, queryUtility

        # Full import is critical!
        from Zope.ComponentArchitecture.tests.TestComponents \
             import IApp, Comp
             
        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              factory="Zope.ComponentArchitecture.tests.TestComponents.Comp"
              provides="Zope.ComponentArchitecture.tests.TestComponents.IApp"
              />
            """
            ))) 
        
        self.assertEqual(getUtility(None, IApp).__class__, Comp)

    def testProtectedUtility(self):
        from Zope.ComponentArchitecture import getUtility, queryUtility

        # Full import is critical!
        from Zope.ComponentArchitecture.tests.TestComponents \
             import IApp, comp
             
        self.assertEqual(queryUtility(None, IV, None), None)

        xmlconfig(StringIO(template % (
            """
            <utility
              component="Zope.ComponentArchitecture.tests.TestComponents.comp"
              provides="Zope.ComponentArchitecture.tests.TestComponents.IApp"
              permission="Zope.Public"
              />
            """
            ))) 
        
        utility = getUtility(None, IApp)
        items = [item[0] for item in getTestProxyItems(utility)]
        self.assertEqual(items, ['a', 'f'])
        self.assertEqual(proxiedObject(utility), comp)
        

    def testView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            """
            ))
        
        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)

    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"
                  permission="Zope.Public"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"
                  permission="Zope.Public"
                  allowed_attributes="action"
                  /> 
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"
                  permission="Zope.Public"
                  allowed_attributes="action"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"
                  permission="Zope.Public"
                  allowed_attributes="action index"
              allowed_interface="Zope.ComponentArchitecture.tests.TestViews.IV"
                  /> 
            """
            ))

        v = getView(Ob(), 'test', Request(IV))
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"
                  allowed_attributes="action index"
                  /> 
            """
            ))
        
    def testDefaultView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <defaultView name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            """
            ))) 
        
        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)
        self.assertEqual(getDefaultViewName(ob, Request(IV)), 'test')
        
    def testDefaultViewOnly(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <defaultView name="test"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            """
            ))) 
        
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)
        self.assertEqual(getDefaultViewName(ob, Request(IV)), 'test')
         
    def testSKinView(self):

        ob = Ob()
        self.assertEqual(queryView(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <skin name="zmi" layers="zmi default"
                  type="Zope.ComponentArchitecture.tests.TestViews.IV" />
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.VZMI"
                  layer="zmi" 
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            <view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/>
            """
            ))) 
        
        self.assertEqual(queryView(ob, 'test', Request(IV), None).__class__,
                         V1)
        self.assertEqual(
            queryView(ob, 'test', Request(IV, 'zmi'), None).__class__,
            VZMI)

    def testResource(self):

        ob = Ob()
        self.assertEqual(queryResource(ob, 'test', Request(IV), None), None)
        xmlconfig(StringIO(template % (
            """
            <resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.R1"
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            """
            ))) 
        
        self.assertEqual(queryResource(ob, 'test', Request(IV), None
                                       ).__class__,
                         R1)
         
    def testSkinResource(self):

        ob = Ob()
        self.assertEqual(queryResource(ob, 'test', Request(IV), None), None)

        xmlconfig(StringIO(template % (
            """
            <skin name="zmi" layers="zmi default"
                  type="Zope.ComponentArchitecture.tests.TestViews.IV" />
            <resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.RZMI"
                  layer="zmi" 
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/> 
            <resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.R1"
                  type="Zope.ComponentArchitecture.tests.TestViews.IV"/>
            """
            ))) 
        
        self.assertEqual(
            queryResource(ob, 'test', Request(IV), None).__class__,
            R1)
        self.assertEqual(
            queryResource(ob, 'test', Request(IV, 'zmi'), None).__class__,
            RZMI)

    def testFactory(self):

        self.assertRaises(ComponentLookupError, createObject, None, 'foo')

        xmlconfig(StringIO(template % (
            """
            <factory 
               id="foo"
               component="Zope.ComponentArchitecture.tests.TestFactory.f"
               />
            <factory 
               component="Zope.ComponentArchitecture.tests.TestFactory.f"
               />
            """
            ))) 

        from Zope.ComponentArchitecture.tests.TestFactory import X
        self.assertEqual(createObject(None, 'foo').__class__, X)
        self.assertEqual(createObject(
            None,
            'Zope.ComponentArchitecture.tests.TestFactory.f').__class__, X)
    
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)
if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

