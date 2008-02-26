##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test harness for online recovery."""

import unittest
import tempfile
import threading
import time

import transaction
import ZODB.FileStorage
import ZODB.utils
import ZODB.tests.MinPO
import ZODB.tests.StorageTestBase

import gocept.zeoraid.recovery


def compare(test, source, target):
    recovery = gocept.zeoraid.recovery.Recovery(
        source, target, lambda target: None)
    protocol = list(recovery())
    test.assertEquals([('verified',), ('recovered',)], protocol[-2:])
    for source_txn, target_txn in zip(source.iterator(),
                                      target.iterator()):
        # We need not compare the transaction metadata because that has
        # already been done by the recovery's verification run.
        source_records = list(source_txn)
        target_records = list(target_txn)
        test.assertEquals(len(source_records), len(target_records))
        for source_record, target_record in zip(source_records,
                                                target_records):
            for name in 'oid', 'tid', 'data', 'version', 'data_txn':
                test.assertEquals(getattr(source_record, name),
                                  getattr(target_record, name))


class ContinuousStorageIterator(ZODB.tests.StorageTestBase.StorageTestBase):

    def setUp(self):
        self._storage = ZODB.FileStorage.FileStorage(tempfile.mktemp())

    def tearDown(self):
        self._storage.close()
        self._storage.cleanup()

    def test_empty_storage(self):
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals([], list(iterator))

    def test_fixed_storage(self):
        self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(1, len(list(iterator)))

    def test_early_growing_storage(self):
        t1 = self._dostore()
        t2 = self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(t1, iterator.next().tid)
        t3 = self._dostore()
        self.assertEquals(t2, iterator.next().tid)
        self.assertEquals(t3, iterator.next().tid)
        self.assertRaises(StopIteration, iterator.next)

    def test_late_growing_storage(self):
        t1 = self._dostore()
        iterator = gocept.zeoraid.recovery.continuous_storage_iterator(
            self._storage)
        self.assertEquals(t1, iterator.next().tid)
        t2 = self._dostore()
        self.assertEquals(t2, iterator.next().tid)
        self.assertRaises(StopIteration, iterator.next)


class OnlineRecovery(unittest.TestCase):

    def store(self, storages, tid=None, status=' ', user=None,
              description=None, extension={}):
        oid = storages[0].new_oid()
        data = ZODB.tests.MinPO.MinPO(7)
        data = ZODB.tests.StorageTestBase.zodb_pickle(data)
        # Begin the transaction
        t = transaction.Transaction()
        if user is not None:
            t.user = user
        if description is not None:
            t.description = description
        for name, value in extension.items():
            t.setExtendedInfo(name, value)
        try:
            for storage in storages:
                storage.tpc_begin(t, tid, status)
                # Store an object
                r1 = storage.store(oid, ZODB.utils.z64, data, '', t)
                # Finish the transaction
                r2 = storage.tpc_vote(t)
                tid = ZODB.tests.StorageTestBase.handle_serials(oid, r1, r2)
            for storage in storages:
                storage.tpc_finish(t)
        except:
            for storage in storages:
                storage.tpc_abort(t)
            raise
        return tid

    def compare(self, source, target):
        compare(self, source, target)

    def setUp(self):
        self.source = ZODB.FileStorage.FileStorage(tempfile.mktemp())
        self.target = ZODB.FileStorage.FileStorage(tempfile.mktemp())
        self.recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, lambda target: None)

    def tearDown(self):
        self.source.close()
        self.source.cleanup()
        self.target.close()
        self.target.cleanup()

    def test_verify_both_empty(self):
        self.assertEquals([('verified',), ('recovered',)],
                          list(self.recovery()))

    def test_verify_empty_target(self):
        self.store([self.source])
        recovery = self.recovery()
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_shorter_target(self):
        self.store([self.source, self.target])
        self.store([self.source])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_equal_length(self):
        self.store([self.source, self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])

    def test_verify_too_long_target(self):
        self.store([self.source, self.target])
        self.store([self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertRaises(ValueError, recovery.next)

    def test_verify_tid_mismatch(self):
        self.store([self.source])
        self.store([self.target])
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_status_mismatch(self):
        tid = self.store([self.source])
        self.store([self.target], tid=tid, status='p')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_user_mismatch(self):
        tid = self.store([self.source])
        self.store([self.target], tid=tid, user='Hans')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_description_mismatch(self):
        tid = self.store([self.source])
        self.store([self.target], tid=tid, description='foo bar')
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_verify_extension_mismatch(self):
        tid = self.store([self.source])
        self.store([self.target], tid=tid, extension=dict(foo=3))
        recovery = self.recovery()
        self.assertRaises(ValueError, recovery.next)

    def test_recover_already_uptodate(self):
        self.store([self.source, self.target])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])

    def test_recover_simple(self):
        self.store([self.source, self.target])
        self.store([self.source])
        recovery = self.recovery()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.compare(self.source, self.target)

    def test_recover_growing(self):
        self.store([self.source, self.target])
        self.store([self.source])
        recovery = self.recovery()
        self.store([self.source])
        self.assertEquals('verify', recovery.next()[0])
        self.store([self.source])
        self.assertEquals('verified', recovery.next()[0])
        for i in xrange(10):
            self.store([self.source])
            self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.compare(self.source, self.target)

    def test_recover_finalize_already_uptodate(self):
        self.store([self.source, self.target])
        self.finalized = False

        def finalize(target):
            self.finalized = True

        recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, finalize)()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.assertEquals(True, self.finalized)

    def test_recover_no_commit_during_finalize(self):
        self.store([self.source, self.target])
        self.store([self.source])
        self.got_commit_lock = None

        def try_commit():
            t = transaction.Transaction()
            self.got_commit_lock = False
            self.source.tpc_begin(t)
            self.got_commit_lock = True
            self.source.tpc_abort(t)

        def finalize_check_no_commit(target):
            self.thread = threading.Thread(target=try_commit)
            self.thread.start()
            time.sleep(1)
            self.assertEquals(False, self.got_commit_lock)

        recovery = gocept.zeoraid.recovery.Recovery(
            self.source, self.target, finalize_check_no_commit)()
        self.assertEquals('verify', recovery.next()[0])
        self.assertEquals('verified', recovery.next()[0])
        self.assertEquals('recover', recovery.next()[0])
        self.assertEquals('recovered', recovery.next()[0])
        self.thread.join()
        self.assertEquals(True, self.got_commit_lock)
        self.compare(self.source, self.target)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContinuousStorageIterator))
    suite.addTest(unittest.makeSuite(OnlineRecovery))
    return suite
