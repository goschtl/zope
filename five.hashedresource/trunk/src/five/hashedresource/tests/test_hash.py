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
from z3c.hashedresource import hash
import Products.Five.browser.resource
import Products.Five.zcml
import Testing.ZopeTestCase.layer
import five.hashedresource
import os
import unittest
import zope.component


class ProductionModeLayer(Testing.ZopeTestCase.layer.ZopeLiteLayer):

    @classmethod
    def setUp(cls):
        Products.Five.zcml.load_config(
            'ftesting.zcml', five.hashedresource)


class CachingContentsHashTest(testing.FunctionalTestCase):

    layer = ProductionModeLayer

    def test_production_mode_hash_should_not_change(self):
        zope.component.provideAdapter(
            hash.CachingContentsHash,
            (Products.Five.browser.resource.DirectoryResource,))

        before = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertEqual(self._hash(before), self._hash(after))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CachingContentsHashTest))
    return suite
