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
$Id: test_zopeconnection.py,v 1.4 2004/02/20 16:57:28 fdrake Exp $
"""

from unittest import TestCase, main, makeSuite
from transaction import get_transaction
from zope.app.rdb import ZopeConnection
from zope.app.interfaces.rdb import IZopeCursor
from zope.app.rdb.tests.stubs import ConnectionStub, TypeInfoStub

class ZopeConnectionTests(TestCase):

    def test_cursor(self):
        zc = ZopeConnection(ConnectionStub(), TypeInfoStub())
        cursor = zc.cursor()

        self.failUnless(IZopeCursor.isImplementedBy(cursor),
                        "cursor is not what we expected")

    def test_connection_txn_registration(self):
        t = get_transaction()
        t.begin()

        zc = ZopeConnection(ConnectionStub(), TypeInfoStub())
        cursor = zc.cursor()
        cursor.execute('select * from blah')

        self.assertEqual(zc._txn_registered, True)
        self.assertEqual(len(t._objects), 1)

    def test_commit(self):
        t = get_transaction()
        t.begin()
        zc = ZopeConnection(ConnectionStub(), TypeInfoStub())
        self._txn_registered = True
        zc.commit()
        self.assertEqual(zc._txn_registered, False,
                         "did not forget the transaction")

    def test_rollback(self):
        t = get_transaction()
        t.begin()
        zc = ZopeConnection(ConnectionStub(), TypeInfoStub())
        self._txn_registered = True
        zc.rollback()
        self.assertEqual(zc._txn_registered, False,
                         "did not forget the transaction")

    def test_getattr(self):
        zc = ZopeConnection(ConnectionStub(), TypeInfoStub())
        cursor = zc.cursor()

        self.assertEqual(zc.answer(), 42)

    def tearDown(self):
        "Abort the transaction"
        get_transaction().abort()

def test_suite():
    return makeSuite(ZopeConnectionTests)

if __name__=='__main__':
    main(defaultTest='test_suite')
