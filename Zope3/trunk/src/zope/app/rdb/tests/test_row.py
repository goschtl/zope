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

$Id: test_row.py,v 1.3 2003/05/01 19:35:30 faassen Exp $
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

        self.assertRaises(ForbiddenAttribute,
                          lambda x=proxied: x.__slots__
                          )

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



def test_suite():
    return makeSuite(RowTests)

if __name__=='__main__':
    main(defaultTest='test_suite')
