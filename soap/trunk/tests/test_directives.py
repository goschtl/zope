##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Test 'soap' ZCML Namespace directives.

$Id: $
"""

from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.tests.views import IC, V1
from zope.component import getView, queryView, getDefaultViewName
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory
from zope.component.tests.request import Request
from soap.interfaces import ISOAPRequest
from zope.interface import implements
import unittest, soap, soap.tests


request = Request(ISOAPRequest)

class Ob(object):
    implements(IC)

ob = Ob()

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testView(self):
        self.assertEqual(queryView(ob, 'test', request), None)
        xmlconfig.file("soap.zcml", soap.tests)
        self.assertEqual(queryView(ob, 'test', request).__class__, V1)

    def testInterfaceProtectedView(self):
        xmlconfig.file("soap.zcml", soap.tests)
        v = getView(ob, 'test2', request)
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig.file("soap.zcml", soap.tests)
        v = getView(ob, 'test3', request)
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("soap.zcml", soap.tests)
        v = getView(ob, 'test4', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("soap.zcml", soap.tests)
        v = getView(ob, 'test5', request)
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "soap_error.zcml", soap.tests)

    def test_no_name(self):
        xmlconfig.file("soap.zcml", soap.tests)
        v = getView(ob, 'index', request)
        self.assertEqual(v(), 'V1 here')
        v = getView(ob, 'action', request)
        self.assertEqual(v(), 'done')

        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
