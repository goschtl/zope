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
import sys, os

import ZODB
import ZODB.FileStorage
from ZODB.PersistentMapping import PersistentMapping
from ZODB.tests.StorageTestBase import removefs
import unittest

class ExportImportTests:
    def checkDuplicate(self, abort_it=0, dup_name='test_duplicate'):
        get_transaction().begin()
        get_transaction().note('duplication')
        # Duplicate the 'test' object.
        conn = self._db.open()
        try:
            root = conn.root()
            ob = root['test']
            assert len(ob) > 10, 'Insufficient test data'
            try:
                import tempfile
                f = tempfile.TemporaryFile()
                ob._p_jar.exportFile(ob._p_oid, f)
                assert f.tell() > 0, 'Did not export correctly'
                f.seek(0)
                new_ob = ob._p_jar.importFile(f)
                root[dup_name] = new_ob
                f.close()
                if abort_it:
                    get_transaction().abort()
                else:
                    get_transaction().commit()
            except:
                get_transaction().abort()
                raise
        finally:
            conn.close()
        get_transaction().begin()
        # Verify the duplicate.
        conn = self._db.open()
        try:
            root = conn.root()
            ob = root['test']
            try:
                ob2 = root[dup_name]
            except KeyError:
                if abort_it:
                    # Passed the test.
                    return
                else:
                    raise
            else:
                if abort_it:
                    assert 0, 'Did not abort duplication'
            l1 = list(ob.items())
            l1.sort()
            l2 = list(ob2.items())
            l2.sort()
            l1 = map(lambda (k, v): (k, v[0]), l1)
            l2 = map(lambda (k, v): (k, v[0]), l2)
            assert l1 == l2, 'Duplicate did not match'
            assert ob._p_oid != ob2._p_oid, 'Did not duplicate'
            assert ob._p_jar == ob2._p_jar, 'Not same connection'
            oids = {}
            for v in ob.values():
                oids[v._p_oid] = 1
            for v in ob2.values():
                assert not oids.has_key(v._p_oid), (
                    'Did not fully separate duplicate from original')
            get_transaction().commit()
        finally:
            conn.close()

    def checkDuplicateAborted(self):
        self.checkDuplicate(abort_it=1, dup_name='test_duplicate_aborted')


class ZODBTests(unittest.TestCase, ExportImportTests):

    def setUp(self):
        self._storage = ZODB.FileStorage.FileStorage(
            'ZODBTests.fs', create=1)
        self._db = ZODB.DB(self._storage)
        get_transaction().begin()
        conn = self._db.open()
        root = conn.root()
        root['test'] = pm = PersistentMapping()
        for n in range(100):
            pm[n] = PersistentMapping({0: 100 - n})
        get_transaction().note('created test data')
        get_transaction().commit()
        conn.close()

    def tearDown(self):
        self._storage.close()
        removefs("ZODBTests.fs")

    def checkVersionOnly(self):
        # Make sure the changes to make empty transactions a no-op
        # still allow things like abortVersion().  This should work
        # because abortVersion() calls tpc_begin() itself.
        r = self._db.open("version").root()
        r[1] = 1
        get_transaction().commit()
        self._db.abortVersion("version")
        get_transaction().commit()

    def checkResetCache(self):
        # The cache size after a reset should be 0 and the GC attributes
        # ought to be linked to it rather than the old cache.
        conn = self._db.open()
        try:
            conn.root()
            self.assert_(len(conn._cache) > 0)  # Precondition
            conn._resetCache()
            self.assertEqual(len(conn._cache), 0)
            self.assert_(conn._incrgc == conn._cache.incrgc)
            self.assert_(conn.cacheGC == conn._cache.incrgc)
        finally:
            conn.close()
        

def test_suite():
    return unittest.makeSuite(ZODBTests, 'check')

def main():
    alltests=test_suite()
    runner = unittest.TextTestRunner()
    runner.run(alltests)

def debug():
    test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')

if __name__=='__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        main()
