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
import unittest

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getView, getService, queryView
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Skins
from zope.interface import Interface
from zope.component.tests.request import Request


class Test(PlacelessSetup, unittest.TestCase):

    def testSkin(self):
        class I1(Interface): pass
        class I2(Interface): pass

        class C1:
            __implements__ = I2
            __used_for__ = I1
            def __init__(self, o, request): self._context=o
        class C2(C1): pass
        class C3(C1): pass

        class O: __implements__ = I1

        getService(None, 'Views').provideView(I1, 'test', I2, [C1])
        self.assertEqual(getView(O(), 'test', Request(I2)).__class__, C1)
        getService(None, Skins).defineSkin('foo', I2, ('foo', 'default'))
        self.assertEqual(getView(O(), 'test', Request(I2, 'foo')).__class__,
                         C1)
        getService(None, 'Views').provideView(None, 'test', I2, [C2])
        self.assertEqual(getView(O(), 'test', Request(I2, 'foo')).__class__,
                         C1)
        getService(None, 'Views').provideView(
            None, 'test', I2, [C2], layer='foo')
        self.assertEqual(getView(O(), 'test', Request(I2, 'foo')).__class__,
                         C2)
        getService(None, 'Views').provideView(
            I1, 'test', I2, [C3], layer='foo')
        self.assertEqual(getView(O(), 'test', Request(I2, 'foo')).__class__,
                         C3)



    def testGetRequestViewMethod(self):

        class I1(Interface): pass
        class I2(Interface): pass

        class C1:
            __implements__ = I2
            __used_for__ = I1
            def __init__(self, o, request): self._context=o
        class C2(C1): pass
        class C3(C1): pass

        class O: __implements__ = I1


        getService(None, 'Views').provideView(I1, 'test', I2, [C1])
        self.assertEqual(getView(O(), 'test',
            Request(I2,'') ).__class__, C1)
        getService(None, Skins).defineSkin('foo', I2, ('foo', 'default'))

        self.assertEqual(getView(O(), 'test',
            Request(I2, 'foo')).__class__, C1)
        getService(None, 'Views').provideView(None, 'test', I2, [C2])

        self.assertEqual(getView(O(), 'test',
            Request(I2, 'foo')).__class__, C1)
        getService(None, 'Views').provideView(
            None, 'test', I2, [C2], layer='foo')

        self.assertEqual(getView(O(), 'test',
            Request(I2, 'foo')).__class__, C2)
        getService(None, 'Views').provideView(
            I1, 'test', I2, [C3], layer='foo')

        self.assertEqual(getView(O(), 'test',
            Request(I2, 'foo')).__class__, C3)

        self.assertRaises(ComponentLookupError,
            getView, O(), 'test2', Request(I2, 'foo'))

        self.assertEqual(queryView(O(), 'test2',
                                   Request(I2, 'foo'), None), None)



def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
