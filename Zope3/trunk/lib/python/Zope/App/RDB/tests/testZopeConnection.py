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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testZopeConnection.py,v 1.1 2002/06/25 15:41:46 k_vertigo Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Transaction import get_transaction
from Zope.App.RDB.ZopeConnection import ZopeConnection
from Zope.App.RDB.IZopeCursor import IZopeCursor
from Stubs import *

class ZopeConnectionTests(TestCase):

    def test_cursor(self):
        "ZopeConnection.cursor() should return an IZopeCursor"
        zc = ZopeConnection(ConnectionStub())
        cursor = zc.cursor()
        
        self.failUnless(IZopeCursor.isImplementedBy(cursor),
                        "cursor is not what we expected")

    def test_connection_txn_registration(self):

        t = get_transaction()
        t.begin()

        zc = ZopeConnection(ConnectionStub())
        cursor = zc.cursor()
        cursor.execute('select * from blah')
        
        self.failUnless(zc._txn_registered == 1,
                        """connection was not registered for txn (conn)""")

        self.failUnless(len(t._objects) == 1,
                        """connection was not registered for txn (txn) """)

    def test_getattr(self):
        "ZopeConnection must reveal Connection's methods"

        zc = ZopeConnection(ConnectionStub())
        cursor = zc.cursor()

        self.failUnless(zc.answer() == 42, "Cannot see the connection")


    def tearDown(self):
        "Abort the transaction"
        get_transaction().abort()
        
def test_suite():
    return TestSuite((
        makeSuite(ZopeConnectionTests),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')




