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
"""Cache scanner tests

$Id$
"""

import unittest
from time import time

from apelib.zodb3.scanner import PoolScanControl, Scanner


class FakeRepository:

    def poll(self, d):
        res = {}
        for source in d.keys():
            repo, location = source
            if repo is not self:
                raise AssertionError, "repo must be self"
            if str(location) != location:
                raise AssertionError(
                    "location %s is not a string" % repr(location))
            # Always report a change
            res[source] = 1001
        return res


class FakeStorage:

    repo = FakeRepository()

    def get_all_sources(self, oids):
        res = {}
        for oid in oids:
            res[oid] = {(self.repo, str(oid)): 10}
        return res


class ScanControlTests(unittest.TestCase):

    def setUp(self):
        storage = self.storage = FakeStorage()
        scanner = self.scanner = Scanner()
        storage.scanner = scanner
        scanner.storage = storage
        ctl = self.ctl = PoolScanControl(storage)
        self.conn1 = ctl.new_connection()
        self.conn2 = ctl.new_connection()

    def test_set_new_oids(self):
        self.conn1.set_oids([5, 8])
        oids = list(self.ctl.oids.keys())
        self.assertEqual(oids, [5, 8])
        self.assertEqual(list(self.ctl.conn_oids.keys()), [self.conn1.conn_id])

    def test_set_multiple_connection_oids(self):
        self.conn1.set_oids([5, 8])
        self.conn2.set_oids([8, 9])
        oids = list(self.ctl.oids.keys())
        self.assertEqual(oids, [5,8,9])
        conns = list(self.ctl.conn_oids.keys())
        self.assertEqual(conns, [self.conn1.conn_id, self.conn2.conn_id])

    def test_remove_oids(self):
        self.conn1.set_oids([5, 8])
        self.conn2.set_oids([8, 9])
        self.conn1.set_oids([8])
        oids = list(self.ctl.oids.keys())
        self.assertEqual(oids, [8,9])
        conns = list(self.ctl.conn_oids.keys())
        self.assertEqual(conns, [self.conn1.conn_id, self.conn2.conn_id])

        self.conn1.set_oids([])
        oids = list(self.ctl.oids.keys())
        self.assertEqual(oids, [8,9])
        self.assertEqual(list(self.ctl.conn_oids.keys()), [self.conn2.conn_id])


class ScannerTests(unittest.TestCase):

    def setUp(self):
        storage = self.storage = FakeStorage()
        scanner = self.scanner = Scanner()
        storage.scanner = scanner
        scanner.storage = storage
        ctl = self.ctl = PoolScanControl(storage)
        self.conn1 = ctl.new_connection()
        self.conn2 = ctl.new_connection()
        self.repo = FakeRepository()

    def test_add_source(self):
        new_sources = {(self.repo, '5'): 0}
        self.scanner.after_load(5, new_sources)
        self.assertEqual(len(self.scanner.future), 1)
        self.assertEqual(self.scanner.future[5][0], new_sources)

    def test_no_updates_when_not_invalidating(self):
        # Don't change current except in scan(), where invalidation
        # messages are possible.
        self.conn1.set_oids([5])

        sources = {(self.repo, '5'): 0}
        self.scanner.after_load(5, sources)
        self.assertNotEqual(self.scanner.current[5], sources)

    def test_remove_oid(self):
        self.conn1.set_oids([5])
        self.assertEqual(len(self.scanner.current), 1)
        self.conn1.set_oids([])
        self.assertEqual(len(self.scanner.current), 0)

    def test_scan(self):
        self.conn1.set_oids([5])
        new_sources = {(self.repo, '6'): 0, (self.repo, '7'): 0, }
        self.scanner.after_load(5, new_sources)
        to_invalidate = self.scanner.scan()
        self.assertEqual(len(to_invalidate), 1)

    def test_pool_scan(self):
        self.conn1.set_oids([5])
        new_sources = {(self.repo, '6'): 0, (self.repo, '7'): 0, }
        self.scanner.after_load(5, new_sources)
        # Just test that ctl.scan() executes without error.
        self.ctl.scan()

    def test_prune_future(self):
        # Simulate some data.
        self.scanner.future[5] = ([], time())  # Should not be pruned
        self.scanner.future[900] = ([], time() - 100000)  # Should be pruned
        self.scanner.prune_future()
        self.assertEqual(len(self.scanner.future), 1)
        self.assert_(self.scanner.future.has_key(5))

    def test_find_new_sources(self):
        # Verify the scanner calls storage.getSources() and saves the result.
        self.conn1.set_oids([5])
        expect_sources = self.storage.get_all_sources([5])[5]
        self.assertEqual(self.scanner.current[5], expect_sources)

    def test_use_cached_sources(self):
        # Verify the scanner uses previously cached sources when available.
        repo = FakeRepository()
        sources = {(repo, '999'): -1}
        self.scanner.after_load(5, sources)
        self.conn1.set_oids([5])
        self.assertEqual(self.scanner.current[5], sources)

    def test_use_committed_sources(self):
        # Verify the scanner updates sources according to transactions.
        repo = FakeRepository()
        sources = {(repo, '999'): -1}
        self.scanner.after_load(5, sources)
        self.conn1.set_oids([5])
        sources_2 = {(repo, '999'): -2}
        self.scanner.changed_sources(5, sources_2)
        final_sources = self.scanner.current[5]
        self.assertEqual(len(final_sources), 1)
        self.assertEqual(final_sources.keys()[0], (repo, '999'))
        self.assertEqual(final_sources.values()[0], -2)


if __name__ == '__main__':
    unittest.main()

