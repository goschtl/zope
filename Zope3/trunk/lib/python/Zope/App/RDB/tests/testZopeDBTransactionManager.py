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
$Id: testZopeDBTransactionManager.py,v 1.5 2002/12/09 16:07:28 alga Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Transaction import get_transaction
from Transaction.tests.abstestIDataManager import IDataManagerTests
from Zope.App.RDB.ZopeDBTransactionManager import ZopeDBTransactionManager
from Zope.App.RDB.ZopeConnection import ZopeConnection
from Stubs import ConnectionStub, CursorStub, TypeInfoStub

class TxnMgrTest(IDataManagerTests, TestCase):

    def setUp(self):
        self.conn = ConnectionStub()
        zc = ZopeConnection(self.conn, TypeInfoStub())
        self.datamgr = ZopeDBTransactionManager(zc)
        zc.registerForTxn()
        self.txn_factory = get_transaction

    def tearDown(self):
        """ make sure the global env is clean"""
        get_transaction().abort()

    def test_abort(self):
        get_transaction().abort()
        self.assertEqual(self.conn._called.get('rollback'), 1)

    def test_commit(self):
        get_transaction().commit()
        self.assertEqual(self.conn._called.get('commit'), 1)

def test_suite():
    return makeSuite(TxnMgrTest)

if __name__=='__main__':
    main(defaultTest='test_suite')

