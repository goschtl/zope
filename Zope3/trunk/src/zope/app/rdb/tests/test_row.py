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
"""Row class tests.

$Id: test_row.py,v 1.4 2003/06/09 15:31:57 stevea Exp $
"""

from unittest import TestCase, main, makeSuite

class RowTests(TestCase):

    def test_RowClassFactory(self):
        from zope.app.rdb import RowClassFactory

        columns = ('food', 'name')
        data = ('pizza', 'john')

        klass = RowClassFactory(columns)
        ob = klass(data)

        self.failUnless(ob.food == 'pizza', "bad row class attribute")
        self.failUnless(ob.name == 'john', "bad row class attribute (2)")

    def test_RowClassFactory_Proxied(self):
        from zope.app.rdb import RowClassFactory
        from zope.security.proxy import ProxyFactory
        from zope.exceptions import ForbiddenAttribute

        columns = ('type', 'speed')
        data = ('airplane', '800km')

        klass = RowClassFactory(columns)

        ob = klass(data)

        proxied = ProxyFactory(ob)

        self.failUnless (proxied.type == 'airplane', "security proxy error")
        self.failUnless (proxied.speed == '800km', "security proxy error (2)")

        self.assertRaises(ForbiddenAttribute, getattr, proxied, '__slots__')
        proxied_class = ProxyFactory(klass)
        proxied_class.__bases__

    def test__cmp__(self):
        from zope.app.rdb import RowClassFactory

        columns = ('food', 'name')
        data = ('pizza', 'john')

        klass = RowClassFactory(columns)
        ob = klass(data)
        self.assertEqual(ob, ob, "not equal to self")

        klass2 = RowClassFactory(columns)
        ob2 = klass2(data)
        self.assertEqual(ob, ob2, "not equal to an identical class")

        columns = ('food', 'surname')
        data = ('pizza', 'john')

        klass3 = RowClassFactory(columns)
        ob3 = klass3(data)
        self.assert_(ob < ob3, "cmp with different columns")

        columns = ('food', 'name')
        data = ('pizza', 'mary')

        klass4 = RowClassFactory(columns)
        ob4 = klass4(data)
        self.assert_(ob < ob4, "cmp with different data")

    def test_InstanceOnlyDescriptor(self):
        from zope.app.rdb import InstanceOnlyDescriptor
        inst = object()  # could be anything
        cls = object  # could be any class
        d = InstanceOnlyDescriptor()
        self.assertRaises(AttributeError, d.__get__, inst, cls)
        self.assertRaises(AttributeError, d.__get__, None, cls)
        self.assertRaises(AttributeError, d.__delete__, inst)
        d.__set__(inst, 23)
        self.assertEquals(d.__get__(inst, cls), 23)
        self.assertRaises(AttributeError, d.__get__, None, cls)
        d = InstanceOnlyDescriptor(23)
        self.assertEquals(d.__get__(inst, cls), 23)
        d.__delete__(inst)
        self.assertRaises(AttributeError, d.__get__, inst, cls)
        self.assertRaises(AttributeError, d.__get__, None, cls)
        self.assertRaises(AttributeError, d.__delete__, inst)


def test_suite():
    return makeSuite(RowTests)

if __name__=='__main__':
    main(defaultTest='test_suite')
