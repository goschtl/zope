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
$Id: testIconDirective.py,v 1.2 2002/06/20 15:54:58 jim Exp $
"""
import os
from StringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite

from Zope.Exceptions import Forbidden
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Configuration.xmlconfig import xmlconfig, XMLConfig
from Zope.ComponentArchitecture.tests.Request import Request
from Zope.ComponentArchitecture.tests.TestViews import IC
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.ComponentArchitecture import queryView, getView, getResource
from Zope.Security.Proxy import ProxyFactory

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

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', Zope.App.Publisher.Browser)()

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
        resource = ProxyFactory(resource)

        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeAllProxies(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

        
        
     

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
