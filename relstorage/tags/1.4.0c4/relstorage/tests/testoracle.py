##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Tests of relstorage.adapters.oracle"""

from relstorage.options import Options
from relstorage.tests.hftestbase import HistoryFreeFromFileStorage
from relstorage.tests.hftestbase import HistoryFreeRelStorageTests
from relstorage.tests.hftestbase import HistoryFreeToFileStorage
from relstorage.tests.hptestbase import HistoryPreservingFromFileStorage
from relstorage.tests.hptestbase import HistoryPreservingRelStorageTests
from relstorage.tests.hptestbase import HistoryPreservingToFileStorage
import logging
import os
import unittest

class UseOracleAdapter:
    def make_adapter(self):
        from relstorage.adapters.oracle import OracleAdapter
        dsn = os.environ.get('ORACLE_TEST_DSN', 'XE')
        if self.keep_history:
            db = 'relstoragetest'
        else:
            db = 'relstoragetest_hf'
        return OracleAdapter(
            user=db,
            password='relstoragetest',
            dsn=dsn,
            options=Options(keep_history=self.keep_history),
            )


class ZConfigTests:

    def checkConfigureViaZConfig(self):
        import tempfile
        dsn = os.environ.get('ORACLE_TEST_DSN', 'XE')
        fd, replica_conf = tempfile.mkstemp()
        os.write(fd, dsn)
        os.close(fd)
        try:
            if self.keep_history:
                dbname = 'relstoragetest'
            else:
                dbname = 'relstoragetest_hf'
            conf = """
            %%import relstorage
            <zodb main>
              <relstorage>
                name xyz
                read-only false
                keep-history %s
                replica-conf %s
                <oracle>
                  user %s
                  password relstoragetest
                  dsn %s
                </oracle>
              </relstorage>
            </zodb>
            """ % (
                self.keep_history and 'true' or 'false',
                replica_conf,
                dbname,
                dsn,
                )

            schema_xml = """
            <schema>
            <import package="ZODB"/>
            <section type="ZODB.database" name="main" attribute="database"/>
            </schema>
            """
            import ZConfig
            from StringIO import StringIO
            schema = ZConfig.loadSchemaFile(StringIO(schema_xml))
            config, handler = ZConfig.loadConfigFile(schema, StringIO(conf))

            db = config.database.open()
            try:
                storage = getattr(db, 'storage', None)
                if storage is None:
                    # ZODB < 3.9
                    storage = db._storage
                self.assertEqual(storage.isReadOnly(), False)
                self.assertEqual(storage.getName(), "xyz")
                adapter = storage._adapter
                from relstorage.adapters.oracle import OracleAdapter
                self.assert_(isinstance(adapter, OracleAdapter))
                self.assertEqual(adapter._user, dbname)
                self.assertEqual(adapter._password, 'relstoragetest')
                self.assertEqual(adapter._dsn, dsn)
                self.assertEqual(adapter._twophase, False)
                self.assertEqual(adapter.keep_history, self.keep_history)
                self.assertEqual(
                    adapter.connmanager.replica_selector.replica_conf,
                    replica_conf)
            finally:
                db.close()
        finally:
            os.remove(replica_conf)


class HPOracleTests(UseOracleAdapter, HistoryPreservingRelStorageTests,
        ZConfigTests):
    pass

class HPOracleToFile(UseOracleAdapter, HistoryPreservingToFileStorage):
    pass

class HPOracleFromFile(UseOracleAdapter, HistoryPreservingFromFileStorage):
    pass

class HFOracleTests(UseOracleAdapter, HistoryFreeRelStorageTests,
        ZConfigTests):
    pass

class HFOracleToFile(UseOracleAdapter, HistoryFreeToFileStorage):
    pass

class HFOracleFromFile(UseOracleAdapter, HistoryFreeFromFileStorage):
    pass

db_names = {
    'data': 'relstoragetest',
    '1': 'relstoragetest',
    '2': 'relstoragetest2',
    'dest': 'relstoragetest2',
    }

def test_suite():
    try:
        import cx_Oracle
    except ImportError, e:
        import warnings
        warnings.warn("cx_Oracle is not importable, so Oracle tests disabled")
        return unittest.TestSuite()

    suite = unittest.TestSuite()
    for klass in [
            HPOracleTests,
            HPOracleToFile,
            HPOracleFromFile,
            HFOracleTests,
            HFOracleToFile,
            HFOracleFromFile,
            ]:
        suite.addTest(unittest.makeSuite(klass, "check"))

    try:
        import ZODB.blob
    except ImportError:
        # ZODB < 3.8
        pass
    else:
        from relstorage.tests.blob.testblob import storage_reusable_suite
        dsn = os.environ.get('ORACLE_TEST_DSN', 'XE')
        for keep_history in (False, True):
            def create_storage(name, blob_dir, keep_history=keep_history):
                from relstorage.storage import RelStorage
                from relstorage.adapters.oracle import OracleAdapter
                db = db_names[name]
                if not keep_history:
                    db += '_hf'
                adapter = OracleAdapter(
                    user=db,
                    password='relstoragetest',
                    dsn=dsn,
                    options=Options(keep_history=keep_history),
                    )
                storage = RelStorage(adapter, name=name, create=True,
                    blob_dir=os.path.abspath(blob_dir))
                storage.zap_all()
                return storage

            if keep_history:
                prefix = 'HPOracle'
                pack_test_name = 'blob_packing.txt'
            else:
                prefix = 'HFOracle'
                pack_test_name = 'blob_packing_history_free.txt'

            suite.addTest(storage_reusable_suite(
                prefix, create_storage,
                test_blob_storage_recovery=True,
                test_packing=True,
                test_undo=keep_history,
                pack_test_name=pack_test_name,
                ))

    return suite

if __name__=='__main__':
    logging.basicConfig()
    unittest.main(defaultTest="test_suite")

