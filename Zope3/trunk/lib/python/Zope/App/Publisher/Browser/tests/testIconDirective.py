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

Revision information:
$Id: testIconDirective.py,v 1.7 2002/11/08 19:56:31 rdmurray Exp $
"""
import os
from StringIO import StringIO
from unittest import TestCase, main, makeSuite

from Zope.Exceptions import Forbidden
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.Configuration.xmlconfig import xmlconfig, XMLConfig
from Zope.ComponentArchitecture.tests.Request import Request
from Zope.ComponentArchitecture.tests.TestViews import IC
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.ComponentArchitecture import queryView, getView, getResource
from Zope.Security.Proxy import ProxyFactory
from Zope.Configuration.Exceptions import ConfigurationError
import Zope.Configuration

import Zope.App.Publisher.Browser

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   >
   %s
   </zopeConfigure>"""


request = Request(IBrowserPresentation)

class Ob:
    __implements__ = IC

ob = Ob()

def defineCheckers():
    # define the appropriate checker for a FileResource for these tests
    from Zope.App.Security.protectClass import protectName
    from Zope.App.Publisher.Browser.FileResource import FileResource
    protectName(FileResource, '__call__', 'Zope.Public')


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('metameta.zcml', Zope.Configuration)()
        XMLConfig('meta.zcml', Zope.App.Publisher.Browser)()
        defineCheckers()

    def test(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import Zope.App.Publisher.Browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'test.gif')
        
        xmlconfig(StringIO(template % (
            """
            <browser:icon name="zmi_icon"
                      for="Zope.ComponentArchitecture.tests.TestViews.IC"
                      file="%s" /> 
            """ % path
            )))

        view = getView(ob, 'zmi_icon', request)
        rname = 'Zope-ComponentArchitecture-tests-TestViews-IC-zmi_icon.gif'
        self.assertEqual(
            view(),
            '<img src="/@@/%s" alt="IC" width="16" height="16" border="0" />'
            % rname)

        resource = getResource(ob, rname, request)
        
        # Resources come ready-wrapped from the factory
        #resource = ProxyFactory(resource)

        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeAllProxies(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResource(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import Zope.App.Publisher.Browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'test.gif')
        
        xmlconfig(StringIO(template % (
            """
            <browser:resource name="zmi_icon_res"
                      image="%s" /> 
            <browser:icon name="zmi_icon"
                      for="Zope.ComponentArchitecture.tests.TestViews.IC"
                      resource="zmi_icon_res" /> 
            """ % path
            )))
 
        view = getView(ob, 'zmi_icon', request)
        rname = "zmi_icon_res"
        self.assertEqual(
            view(),
            '<img src="/@@/%s" alt="IC" width="16" height="16" border="0" />'
            % rname)

        resource = getResource(ob, rname, request)

        # Resources come ready-wrapped from the factory
        #resource = ProxyFactory(resource)

        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeAllProxies(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResourceErrors(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import Zope.App.Publisher.Browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'test.gif')

        config = StringIO(template % (
            """
            <browser:resource name="zmi_icon_res"
                      image="%s" /> 
            <browser:icon name="zmi_icon"
                      for="Zope.ComponentArchitecture.tests.TestViews.IC"
                      file="%s"
                      resource="zmi_icon_res" /> 
            """ % (path, path)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

        config = StringIO(template % (
            """
            <browser:icon name="zmi_icon"
                      for="Zope.ComponentArchitecture.tests.TestViews.IC"
                      /> 
            """
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
