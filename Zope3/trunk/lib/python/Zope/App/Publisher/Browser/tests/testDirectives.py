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

import os
import unittest
import sys

from Zope.Configuration.xmlconfig import xmlconfig
from Zope.Configuration.Exceptions import ConfigurationError
from Zope.ComponentArchitecture.tests.TestViews import IC, V1, VZMI, R1, RZMI
from Zope.ComponentArchitecture import getView, queryView, queryResource
from Zope.ComponentArchitecture import getDefaultViewName, getResource
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Security.Proxy import ProxyFactory
from cStringIO import StringIO

from Zope.ComponentArchitecture.tests.Request import Request

from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation

import Zope.App.Publisher.Browser

defs_path = os.path.join(
    os.path.split(Zope.App.Publisher.Browser.__file__)[0],
    'meta.zcml')

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:security='http://namespaces.zope.org/security'
   xmlns:browser='http://namespaces.zope.org/browser'>
   %s
   </zopeConfigure>"""

request = Request(IBrowserPresentation)

class Ob:
    __implements__ = IC

ob = Ob()

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        xmlconfig(open(defs_path))

        from Zope.ComponentArchitecture.GlobalAdapterService \
             import provideAdapter
        from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
        from Zope.App.Traversing.ITraversable import ITraversable

        provideAdapter(None, ITraversable, DefaultTraversable)

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template % (
            """
            <browser:view name="test"
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
            <browser:defaultView name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" /> 
            """
            ))) 

        self.assertEqual(queryView(ob, 'test',
                                   request, None
                                 ).__class__, V1)
        self.assertEqual(getDefaultViewName(ob, request
                                 ), 'test')
                                 
      
    def testSKinView(self):
        self.assertEqual(queryView(ob, 'test', request,
                                   None), None)

        xmlconfig(StringIO(template % (
            """
            <browser:skin name="zmi" layers="zmi default" />
            <browser:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.VZMI"
                  layer="zmi" 
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" /> 
            <browser:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" />
            """
            ))) 
        
        self.assertEqual(
            queryView(ob, 'test', request).__class__,
            V1)
        self.assertEqual(
            queryView(ob, 'test',
                      Request(IBrowserPresentation, 'zmi')).__class__,
            VZMI)

    def testResource(self):
        self.assertEqual(queryResource(ob, 'test', request,
                                       None),
                         None)

        xmlconfig(StringIO(template % (
            """
            <browser:resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.R1" /> 
            """
            ))) 

        self.assertEqual(
            queryResource(ob, 'test', request).__class__,
            R1)
         
    def testSkinResource(self):
        self.assertEqual(
            queryResource(ob, 'test', request, None),
            None)

        xmlconfig(StringIO(template % (
            """
            <browser:skin name="zmi" layers="zmi default" />
            <browser:resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.RZMI"
                  layer="zmi" /> 
            <browser:resource name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.R1" />
            """
            ))) 
        
        self.assertEqual(
            queryResource(ob, 'test', request).__class__,
            R1)
        self.assertEqual(
            queryResource(ob, 'test',
                          Request(IBrowserPresentation, 'zmi')).__class__,
            RZMI)


    def testInterfaceProtectedView(self):
        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
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
            <browser:view name="test"
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
            <browser:view name="test"
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
            <browser:view name="test"
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
            <browser:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  allowed_attributes="action index"
                  /> 
            """
            ))


    def testPageViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)
        test3 = os.path.join(os.path.split(defs_path)[0], 'tests', 'test3.pt')

        xmlconfig(StringIO(template %
            """
            <browser:view
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC">

                <browser:page name="index.html" attribute="index" /> 
                <browser:page name="action.html" attribute="action" /> 
                <browser:page name="test.html" template="%s" /> 
            </browser:view>
            """ % test3
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = getView(ob, 'test.html', request)
        self.assertEqual(str(v()), '<html><body><p>done</p></body></html>\n')

    def testPageViewsWithName(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:view name="test"
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC">

                <browser:page name="index.html" attribute="index" /> 
                <browser:page name="action.html" attribute="action" /> 
            </browser:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')
        v = getView(ob, 'test', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')
    

    def testProtectedPageViews(self):
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/security">
              <directive name="permission"
                 attributes="id title description"
                 handler="Zope.App.Security.metaConfigure.definePermission" />
            </directives>

            <security:permission id="XXX" title="xxx" />

            <browser:view
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  permission="XXX">

                <browser:page name="index.html" attribute="index" /> 
                <browser:page name="action.html" attribute="action"
                              permission="Zope.Public" /> 
            </browser:view>
            """
            ))

        # Need to "log someone in" to turn on checks
        from Zope.Security.SecurityManagement import newSecurityManager
        newSecurityManager('someuser')

        v = getView(ob, 'index.html', request)
        self.assertRaises(Exception, v)
        v = getView(ob, 'action.html', request)
        self.assertEqual(v(), 'done')

    def testSkinnedPageView(self):
        self.assertEqual(queryView(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:skin name="skinny" layers="layer default" />
            <browser:view
                  factory="Zope.ComponentArchitecture.tests.TestViews.V1">

                <browser:page name="index.html" attribute="index" /> 
                <browser:page name="index.html" attribute="action"
                              layer="layer"/> 
            </browser:view>
            """
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'index.html',
                    Request(IBrowserPresentation, "skinny"))
        self.assertEqual(v(), 'done')

    def testPageResource(self):
        self.assertEqual(queryResource(ob, 'test', request), None)

        xmlconfig(StringIO(template %
            """
            <browser:resource
                  factory="Zope.ComponentArchitecture.tests.TestViews.R1">

                <browser:page name="index.html" attribute="index" /> 
                <browser:page name="action.html" attribute="action" /> 
            </browser:resource>
            """
            ))

        v = getResource(ob, 'index.html', request)
        self.assertEqual(v(), 'R1 here')
        v = getResource(ob, 'action.html', request)
        self.assertEqual(v(), 'R done')


    def testFile(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test.pt')
        
        self.assertEqual(queryResource(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:resource
                  name="index.html"
                  file="%s"
                  />
            """ % path
            ))

        v = getResource(ob, 'index.html', request)
        self.assertEqual(v._testData(), open(path, 'rb').read())


    def testtemplate(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test.pt')
        
        self.assertEqual(queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" />
            """ % path
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')

    def testtemplateWClass(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test2.pt')
        
        self.assertEqual(queryView(ob, 'index.html', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  class="Zope.App.Publisher.Browser.tests.templateclass."
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" />
            """ % path
            ))

        v = getView(ob, 'index.html', request)
        self.assertEqual(v().strip(), '<html><body><p>42</p></body></html>')

    def testProtectedtemplate(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test.pt')
        
        self.assertEqual(queryView(ob, 'test', request),
                         None)

        xmlconfig(StringIO(template %
            """
            <directives namespace="http://namespaces.zope.org/security">
              <directive name="permission"
                 attributes="id title description"
                 handler="Zope.App.Security.metaConfigure.definePermission" />
            </directives>

            <security:permission id="XXX" title="xxx" />

            <browser:view
                  name="xxx.html"
                  template="%s"
                  permission="XXX"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" />
            """ % path
            ))

        xmlconfig(StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  permission="Zope.Public"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" />
            """ % path
            ))

        # Need to "log someone in" to turn on checks
        from Zope.Security.SecurityManagement import newSecurityManager
        newSecurityManager('someuser')
        
        v = getView(ob, 'xxx.html', request)
        v = ProxyFactory(v)
        self.assertRaises(Exception, v)

        v = getView(ob, 'index.html', request)
        v = ProxyFactory(v)
        self.assertEqual(v().strip(), '<html><body><p>test</p></body></html>')
        

    def testtemplateNoName(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:view
                  template="%s"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  /> 
            """ % path
            ))

    def testtemplateAndPage(self):
        path = os.path.join(os.path.split(defs_path)[0], 'tests', 'test.pt')
        self.assertRaises(
            ConfigurationError,
            xmlconfig,
            StringIO(template %
            """
            <browser:view
                  name="index.html"
                  template="%s"
                  for="Zope.ComponentArchitecture.tests.TestViews.IC" 
                  >
               <browser:page name="foo.html" attribute="index" />
            </browser:view>
            """ % path
            ))


    
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
