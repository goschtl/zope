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
"""Test the provideFactory method.

$Id: test_providefactory.py,v 1.8 2004/01/08 20:48:22 garrett Exp $
"""


from unittest import TestCase, main, makeSuite
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.servicenames import Factories
from zope.component.exceptions import ComponentLookupError

class ProvideFactoryTestCase(PlacelessSetup, TestCase):

    def test_provide_factory(self):
        from zope.component import getService, createObject
        from zope.component.tests.factory import f, X
        factories=getService(None, Factories)
        factories.provideFactory("Some.Object", f)
        thing = createObject(None,"Some.Object")
        self.assert_(isinstance(thing, X))

    def test_getFactoriesFor(self):
        from zope.component import getService, createObject
        from zope.component.tests.factory import f, X, IX
        factories=getService(None, Factories)
        factories.provideFactory("Some.Object", f)
        fs = factories.getFactoriesFor(IX)
        self.assertEqual(fs, [('Some.Object', f)])

    def test_getFactoriesForUnregistered(self):
        from zope.component import getService, createObject
        from zope.component.tests.factory import f, X, IX, IFoo
        factories=getService(None, Factories)
        factories.provideFactory("Some.Object", f)
        self.assertRaises(ComponentLookupError, factories.getFactoriesFor,
                          IFoo)

    def test_queryFactoriesForUnregistered(self):
        from zope.component import getService, createObject
        from zope.component.tests.factory import f, X, IX, IFoo
        factories=getService(None, Factories)
        factories.provideFactory("Some.Object", f)
        self.assertEqual(factories.queryFactoriesFor(IFoo, None), None)

    def test_getFactoryInfo(self):
        from zope.component import getService
        from zope.component.tests.factory import f
        from zope.component.factory import FactoryInfo
        factories = getService(None, Factories)
        info = FactoryInfo('Some Object', 'An object for testing.')
        factories.provideFactory("Some.Object", f, info)
        info = factories.getFactoryInfo('Some.Object')
        self.assertEquals(info.title, 'Some Object')
        self.assertEquals(info.description, 'An object for testing.')
        self.assert_(factories.getFactoryInfo('Unregistered.Object') is None)

def test_suite():
    return makeSuite(ProvideFactoryTestCase)

if __name__=='__main__':
    main(defaultTest='test_suite')
