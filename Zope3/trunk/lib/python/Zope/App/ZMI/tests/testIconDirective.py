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
$Id: testIconDirective.py,v 1.1 2002/06/13 23:15:45 jim Exp $
"""
import os
from StringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite

from Zope.Exceptions import Forbidden
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.Configuration.xmlconfig import xmlconfig
from Zope.ComponentArchitecture.tests.Request import Request
from Zope.ComponentArchitecture.tests.TestViews import IC
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.ComponentArchitecture import queryView, getView, getResource
from Zope.Security.Proxy import ProxyFactory

import Zope.App.ZMI as p
defs_path = os.path.join(os.path.split(p.__file__)[0], 'zmi-meta.zcml')

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:zmi='http://namespaces.zope.org/zmi'
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
        xmlconfig(open(defs_path))

    def test(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        package_directory = os.path.split(defs_path)[0]
        path = os.path.join(package_directory, "tests", 'test.gif')
        
        xmlconfig(StringIO(template % (
            """
            <zmi:icon for="Zope.ComponentArchitecture.tests.TestViews.IC"
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
