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
"""Test cases for objects implementing IDataManager.

This is a combo test between Connection and DB, since the two are
rather incestuous and the DB Interface is not defined that I was
able to find.

To do a full test suite one would probably want to write a dummy
storage that will raise errors as needed for testing.

I started this test suite to reproduce a very simple error (tpc_abort
had an error and wouldn't even run if called).  So it is *very*
incomplete, and even the tests that exist do not make sure that
the data actually gets written/not written to the storge.

Obviously this test suite should be expanded.

$Id: abstestIDataManager.py,v 1.3 2002/07/18 17:10:18 jeremy Exp $
"""

import os
from unittest import TestCase

from Transaction import Transaction, get_transaction

class IDataManagerTests(TestCase):
    
    def setUp(self):
        self.datamgr = None # subclass should override
        self.obj = None # subclass should define Persistent object

    def get_transaction(self):
        t = Transaction()
        t.setUser('IDataManagerTests')
        t.note('dummy note')
        return t

    ################################
    # IDataManager interface tests #
    ################################

    def testCommitObj(self):
        tran = self.get_transaction()
        self.datamgr.tpc_begin(tran)
        self.datamgr.commit(self.obj, tran)
        self.datamgr.tpc_vote(tran)
        self.datamgr.tpc_finish(tran)

    def testAbortTran(self):
        tran = self.get_transaction()
        self.datamgr.tpc_begin(tran)
        self.datamgr.commit(self.obj, tran)
        self.datamgr.tpc_abort(tran)

    def testAbortObj(self):
        tran = self.get_transaction()
        self.datamgr.tpc_begin(tran)
        self.datamgr.commit(self.obj, tran)
        self.datamgr.abort(self.obj, tran)
        self.datamgr.tpc_abort(tran)

    def testSubCommit(self):
        tran = self.get_transaction()
        self.datamgr.tpc_begin(tran, 1)
        self.datamgr.commit(self.obj, tran)
        self.datamgr.commit_sub(tran)
        self.datamgr.tpc_vote(tran)
        self.datamgr.tpc_finish(tran)

    #This test may not be semantically correct.  It hangs on FreeBSD.
    #def testSubAbortCommitNull(self):
    #   tran = self.get_transaction()
    #   self.datamgr.tpc_begin(tran,1)
    #   self.datamgr.commit(self.obj,tran)
    #   self.datamgr.abort_sub(tran)
    #   self.datamgr.tpc_vote(tran)
    #   self.datamgr.tpc_finish(tran)

