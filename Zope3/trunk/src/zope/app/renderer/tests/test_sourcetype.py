##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for Global Wiki Source Type Service.

$Id: test_sourcetype.py,v 1.1 2003/07/31 18:48:42 srichter Exp $
"""
import unittest

from zope.interface import Interface, implements
from zope.app.interfaces.renderer import IGlobalSourceTypeService
from zope.app.renderer.sourcetype import GlobalSourceTypeService


class IFoo(Interface):
    pass

class Foo(unicode):
    implements(IFoo)

class IFoo2(Interface):
    pass

class Foo2(unicode):
    implements(IFoo2)


class TestGlobalSourceTypeService(unittest.TestCase):

    def setUp(self):
        self.obj = GlobalSourceTypeService()
        self.obj.provide('Foo', IFoo, Foo)

    def testInterfaceConformity(self):
        self.assert_(IGlobalSourceTypeService.isImplementedBy(self.obj))

    def test_provide(self):
        service = GlobalSourceTypeService()
        service.provide('Foo', IFoo, Foo)
        self.assertEqual(
            {'Foo': (IFoo, Foo)},
            service.__dict__['_GlobalSourceTypeService__types'])

    def test_get(self):
        self.assertEqual(IFoo, self.obj.get('Foo'))
        self.assertEqual(None, self.obj.get('Bar'))
        self.assertEquals(IFoo2, self.obj.get('Bar', IFoo2))

    def test_query(self):
        self.assertEqual(IFoo, self.obj.get('Foo'))
        self.assertRaises(KeyError, self.obj.query, ('Bar',))

    def test_getAllTitles(self):
        self.obj.provide('Foo2', IFoo2, Foo2)
        titles = self.obj.getAllTitles()
        titles.sort()
        self.assertEqual(['Foo', 'Foo2'], titles)
        
    def test_createObject(self):
        obj = self.obj.createObject('Foo', 'Source text')
        self.assertEqual(Foo, obj.__class__)
        self.assert_(IFoo.isImplementedBy(obj))
        self.assertEqual('Source text', str(obj))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestGlobalSourceTypeService),
        ))

if __name__ == '__main__':
    unittest.main()
