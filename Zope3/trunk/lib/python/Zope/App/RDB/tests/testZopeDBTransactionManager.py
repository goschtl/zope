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

$Id: testZopeDBTransactionManager.py,v 1.1 2002/06/25 15:41:46 k_vertigo Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Transaction import get_transaction
from Zope.App.RDB.ZopeDBTransactionManager import ZopeDBTransactionManager
from Zope.App.RDB.ZopeConnection import ZopeConnection
from Stubs import *

class TxnMgrTest(TestCase):
    """
    test txn integration.
    """

    def tearDown(self):
        """ make sure the global env is clean"""
        get_transaction().abort()

    def test_abort(self):
	
        conn = ConnectionStub()
        zc = ZopeConnection(conn)
        tm = ZopeDBTransactionManager(zc)

        zc.registerForTxn()
        
        t = get_transaction()
        t.abort()

        self.failUnless(conn._called.get('rollback')==1,
                        """ abort failed """)

    def test_commit(self):
        
        conn = ConnectionStub()
        zc = ZopeConnection(conn)
        tm = ZopeDBTransactionManager(zc)

        zc.registerForTxn()
        
        t = get_transaction()
        t.commit()

        self.failUnless(conn._called.get('commit')==1,
                        """ commit failed """)

def test_suite():
    return TestSuite((
        makeSuite(TxnMgrTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

