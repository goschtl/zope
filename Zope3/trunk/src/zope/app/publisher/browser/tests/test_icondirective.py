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
$Id: test_icondirective.py,v 1.13 2003/09/24 17:22:07 sidnei Exp $
"""
import os
from StringIO import StringIO
from unittest import TestCase, main, makeSuite

from zope.exceptions import Forbidden
from zope.proxy import removeAllProxies
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.publisher.browser import TestRequest
from zope.component.tests.views import IC
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.component import queryView, getView, getResource
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements
from zope.app.interfaces.services.service import ISite
from zope.app.interfaces.traversing import IContainmentRoot
from zope.security.checker import ProxyFactory

import zope.app.publisher.browser

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'
   >
   %s
   </configure>"""


request = TestRequest(IBrowserPresentation)

class Ob:
    implements(IC, ISite, IContainmentRoot)

ob = Ob()
request._vh_root = ob

def defineCheckers():
    # define the appropriate checker for a FileResource for these tests
    from zope.app.security.protectclass import protectName
    from zope.app.publisher.browser.fileresource import FileResource
    protectName(FileResource, '__call__', 'zope.Public')


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', zope.app.publisher.browser)()
        defineCheckers()

    def test(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import zope.app.publisher.browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'testfiles', 'test.gif')

        xmlconfig(StringIO(template % (
            """
            <browser:icon name="zmi_icon"
                      for="zope.component.tests.views.IC"
                      file="%s" />
            """ % path
            )))

        view = getView(ob, 'zmi_icon', request)
        rname = 'zope-component-tests-views-IC-zmi_icon.gif'
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="IC" '
            'width="16" height="16" border="0" />'
            % rname)

        resource = ProxyFactory(getResource(ob, rname, request))
        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeAllProxies(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResource(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import zope.app.publisher.browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'testfiles', 'test.gif')

        xmlconfig(StringIO(template % (
            """
            <browser:resource name="zmi_icon_res"
                      image="%s" />
            <browser:icon name="zmi_icon"
                      for="zope.component.tests.views.IC"
                      resource="zmi_icon_res" />
            """ % path
            )))

        view = getView(ob, 'zmi_icon', request)
        rname = "zmi_icon_res"
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="IC" width="16" '
            'height="16" border="0" />'
            % rname)

        resource = ProxyFactory(getResource(ob, rname, request))

        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeAllProxies(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResourceErrors(self):
        self.assertEqual(queryView(ob, 'zmi_icon', request), None)

        import zope.app.publisher.browser.tests as p
        path = os.path.split(p.__file__)[0]
        path = os.path.join(path, 'testfiles', 'test.gif')

        config = StringIO(template % (
            """
            <browser:resource name="zmi_icon_res"
                      image="%s" />
            <browser:icon name="zmi_icon"
                      for="zope.component.tests.views.IC"
                      file="%s"
                      resource="zmi_icon_res" />
            """ % (path, path)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

        config = StringIO(template % (
            """
            <browser:icon name="zmi_icon"
                      for="zope.component.tests.views.IC"
                      />
            """
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
