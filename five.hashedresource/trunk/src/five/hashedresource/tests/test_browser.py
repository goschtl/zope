#############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""tests

$Id$
"""
from five.hashedresource import testing
from z3c.hashedresource import interfaces
import Testing.ZopeTestCase
import unittest
import Products.Five.testbrowser
import zope.component
import zope.publisher.browser


class BrowserTest(Testing.ZopeTestCase.FunctionalTestCase):

    layer = testing.HashedResourcesLayer

    def setUp(self):
        super(BrowserTest, self).setUp()
        self.browser = Products.Five.testbrowser.Browser()
        self.browser.handleErrors = False
        self.directory = zope.component.getAdapter(
            zope.publisher.browser.TestRequest(), name='myresource')

    def test_traverse_resource_by_name(self):
        self.browser.open('http://localhost/++resource++myresource/test.txt')
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_resource_by_hash(self):
        hash = str(
            interfaces.IResourceContentsHash(self.directory))
        self.browser.open(
            'http://localhost/++noop++%s/++resource++myresource/test.txt' % hash)
        self.assertEqual('test\ndata\n', self.browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BrowserTest))
    return suite
