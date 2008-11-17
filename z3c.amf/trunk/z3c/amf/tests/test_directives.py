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
Test 'amf' ZCML Namespace directives.

$Id$
"""

from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.tests.views import IC
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.app.testing.placelesssetup import PlacelessSetup
from z3c.amf.interfaces import IAMFRequest
from zope.interface import alsoProvides
from zope.interface import implements
import unittest
import z3c.amf.tests
from zope.publisher.browser import TestRequest

request = TestRequest()
alsoProvides(request, IAMFRequest)


class Ob(object):

    implements(IC)

ob = Ob()


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testView(self):
        self.assertEqual(
            queryMultiAdapter((ob, request), name='test'), None)
        xmlconfig.file("amf.zcml", z3c.amf.tests)
        self.assertEqual(
            str(queryMultiAdapter((ob, request), name='test').__class__),
            "<class 'Products.Five.metaclass.V1'>")

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("amf.zcml", z3c.amf.tests)
        v = getMultiAdapter((ob, request), name='test4')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("amf.zcml", z3c.amf.tests)
        v = getMultiAdapter((ob, request), name='test5')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "amf_error.zcml", z3c.amf.tests)

    def test_no_name(self):
        xmlconfig.file("amf.zcml", z3c.amf.tests)
        v = getMultiAdapter((ob, request), name='index')
        self.assertEqual(v(), 'V1 here')
        v = getMultiAdapter((ob, request), name='action')
        self.assertEqual(v(), 'done')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
