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

$Id: test_resources.py,v 1.6 2003/05/01 19:35:39 faassen Exp $
"""

import unittest

from zope.component import getService
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getResource, queryResource
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Skins, Resources
from zope.interface import Interface
from zope.component.tests.request import Request

class Test(PlacelessSetup, unittest.TestCase):

    def testSkin(self):
        class I2(Interface): pass
        class C1:
            def __init__(self, request): pass
            __implements__ = I2
        class C2(C1): pass

        getService(None,Resources).provideResource('test', I2, C1)
        self.assertEqual(getResource(None, 'test', Request(I2)).__class__, C1)
        getService(None,Skins).defineSkin('foo', I2, ('foo', 'default'))
        self.assertEqual(
            getResource(None, 'test', Request(I2, 'foo')).__class__,
            C1)
        getService(None,Resources).provideResource('test', I2, C2,
                                                     layer='foo')
        self.assertEqual(
            getResource(None, 'test', Request(I2, 'foo')).__class__,
            C2)

    def testGetRequestResourceMethod(self):
        class I2(Interface): pass
        class C1:
            def __init__(self, request): pass

            __implements__ = I2
        class C2(C1): pass


        getService(None,Resources).provideResource('test', I2, C1)
        self.assertEqual(
            getResource(None, 'test', Request(I2, 'default') ).__class__,
            C1)
        getService(None,Skins).defineSkin('foo', I2, ('foo', 'default'))
        self.assertEqual(
            getResource(None, 'test', Request(I2, 'foo')).__class__,
            C1)
        getService(None,Resources).provideResource('test', I2, C2,
                                                     layer='foo')
        self.assertEqual(
            getResource(None, 'test', Request(I2, 'foo')).__class__,
            C2)

        self.assertRaises(
            ComponentLookupError,
            getResource, None, 'test2', Request(I2, 'foo'))

        self.assertEqual(
            queryResource(None, 'test2', Request(I2, 'foo'), None),
            None)

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
