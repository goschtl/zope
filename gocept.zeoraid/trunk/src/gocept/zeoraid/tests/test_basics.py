# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Test harness for gocept.zeoraid."""

import unittest
import tempfile
import os
import time
import shutil

import zope.interface.verify

import transaction
from ZODB.tests import StorageTestBase, BasicStorage, \
             TransactionalUndoStorage, PackableStorage, \
             Synchronization, ConflictResolution, HistoryStorage, \
             Corruption, RevisionStorage, PersistentStorage, \
             MTStorage, ReadOnlyStorage, RecoveryStorage

import gocept.zeoraid.storage

from ZEO.ClientStorage import ClientStorage
from ZEO.tests import forker, CommitLockTests, ThreadTests
from ZEO.tests.testZEO import get_port

import ZODB.interfaces
import ZEO.interfaces
import ZODB.config

# Uncomment this to get helpful logging from the ZEO servers on the console
#import logging
#logging.getLogger().addHandler(logging.StreamHandler())


class ZEOOpener(object):

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs or {}

    def open(self, **kwargs):
        return ClientStorage(self.name, **self.kwargs)


class ZEOStorageBackendTests(StorageTestBase.StorageTestBase):

    def open(self, **kwargs):
        self._storage = gocept.zeoraid.storage.RAIDStorage('teststorage',
                                                           self._storages, **kwargs)

    def setUp(self):
        # Ensure compatibility
        gocept.zeoraid.compatibility.setup()
        self._server_storage_files = []
        self._servers = []
        self._storages = []
        for i in xrange(5):
            port = get_port()
            zconf = forker.ZEOConfig(('', port))
            zport, adminaddr, pid, path = forker.start_zeo_server(self.getConfig(),
                                                                  zconf, port)
            self._servers.append(adminaddr)
            self._storages.append(ZEOOpener(zport, storage='1',
                                            min_disconnect_poll=0.5, wait=1,
                                            wait_timeout=60))
        self.open()

    def getConfig(self):
        filename = self.__fs_base = tempfile.mktemp()
        self._server_storage_files.append(filename)
        return """\
        <filestorage 1>
        path %s
        </filestorage>
        """ % filename

    def tearDown(self):
        self._storage.close()
        for server in self._servers:
            forker.shutdown_zeo_server(server)
        # XXX wait for servers to come down
        # XXX delete filestorage files

class ReplicationStorageTests(BasicStorage.BasicStorage,
        TransactionalUndoStorage.TransactionalUndoStorage,
        RevisionStorage.RevisionStorage,
        PackableStorage.PackableStorage,
        PackableStorage.PackableUndoStorage,
        Synchronization.SynchronizedStorage,
        ConflictResolution.ConflictResolvingStorage,
        ConflictResolution.ConflictResolvingTransUndoStorage,
        HistoryStorage.HistoryStorage,
        PersistentStorage.PersistentStorage,
        MTStorage.MTStorage,
        ReadOnlyStorage.ReadOnlyStorage,
        ):

    def check_raid_interfaces(self):
        for iface in (ZODB.interfaces.IStorage,
                      ZODB.interfaces.IBlobStorage,
                      ZODB.interfaces.IStorageUndoable,
                      ZODB.interfaces.IStorageCurrentRecordIteration,
                      ZEO.interfaces.IServeable,
                      ):
            self.assert_(zope.interface.verify.verifyObject(iface,
                                                            self._storage))

    def check_getname(self):
        self.assertEquals('teststorage', self._storage.getName())
        self._storage.close()
        self.assertEquals('teststorage', self._storage.getName())


class FailingStorageTestsBase(StorageTestBase.StorageTestBase):

    backend_count = None

    def _backend(self, index):
        return self._storage.storages[
            self._storage.storages_optimal[index]]

    def setUp(self):
        # Ensure compatibility
        gocept.zeoraid.compatibility.setup()

        self._blob_dirs = []
        self._servers = []
        self._storages = []
        for i in xrange(self.backend_count):
            port = get_port()
            zconf = forker.ZEOConfig(('', port))
            zport, adminaddr, pid, path = forker.start_zeo_server(
                """%import gocept.zeoraid.tests
                <failingstorage 1>
                </failingstorage>""",
                zconf, port)
            blob_dir = tempfile.mkdtemp()
            self._blob_dirs.append(blob_dir)
            self._servers.append(adminaddr)
            self._storages.append(ZEOOpener(zport, storage='1',
                                            cache_size=12,
                                            blob_dir=blob_dir,
                                            min_disconnect_poll=0.5, wait=1,
                                            wait_timeout=60))
        self._storage = gocept.zeoraid.storage.RAIDStorage('teststorage',
                                                           self._storages)

    def tearDown(self):
        try:
            self._storage.close()
        except:
            pass
        for server in self._servers:
            forker.shutdown_zeo_server(server)
        # XXX wait for servers to come down


class FailingStorageTests2Backends(FailingStorageTestsBase):

    backend_count = 2

    def _disable_storage(self, index):
        self._storage.raid_disable(self._storage.storages_optimal[index])

    def test_close(self):
        self._storage.close()
        self.assertEquals(self._storage.closed, True)
        # Calling close() multiple times is allowed (and a no-op):
        self._storage.close()
        self.assertEquals(self._storage.closed, True)

    def test_close_degrading(self):
        # See the comment on `test_close_failing`.
        self._storage.storages[self._storage.storages_optimal[0]].fail('close')
        self._storage.close()
        self.assertEquals([], self._storage.storages_degraded)
        self.assertEquals(True, self._storage.closed)

    def test_close_failing(self):
        # Even though we make the server-side storage fail, we do not get
        # receive an error or a degradation because the result of the failure
        # is that the connection is closed. This is actually what we wanted.
        # Unfortunately that means that an error can be hidden while closing.
        self._backend(0).fail('close')
        self._backend(1).fail('close')
        self._storage.close()
        self.assertEquals(True, self._storage.closed)

    def test_close_server_missing(self):
        # See the comment on `test_close_failing`.
        forker.shutdown_zeo_server(self._servers[0])
        del self._servers[0]
        self._storage.close()
        self.assertEquals([], self._storage.storages_degraded)
        self.assertEquals(True, self._storage.closed)

    def test_getsize(self):
        self.assertEquals(4, self._backend(0).getSize())
        self.assertEquals(4, self._backend(1).getSize())
        self.assertEquals(4, self._storage.getSize())
        self._storage.close()
        self.assertRaises(gocept.zeoraid.interfaces.RAIDClosedError,
                          self._storage.getSize)

    def test_getsize_degrading(self):
        self._backend(0).fail('getSize')
        # This doesn't get noticed because ClientStorage already knows
        # the answer and caches it. Therefore calling getSize can never
        # degrade or fail a RAID.
        self.assertEquals(4, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(1).fail('getSize')
        self.assertEquals(4, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

    def test_history(self):
        oid = self._storage.new_oid()
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(0).history, oid, '')
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(1).history, oid, '')
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._storage.history, oid, '')
        self.assertEquals('optimal', self._storage.raid_status())

        self._dostore(oid=oid)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._backend(1).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))

        self._disable_storage(0)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.history, oid, '')

    def test_history_degrading(self):
        oid = self._storage.new_oid()
        self._dostore(oid=oid)
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals(1, len(self._backend(1).history(oid, '')))
        self.assertEquals(1, len(self._storage.history(oid, '')))

        self._backend(0).fail('history')
        self.assertEquals(1, len(self._storage.history(oid, '')))
        self.assertEquals(1, len(self._backend(0).history(oid, '')))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('history')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.history, oid, '')
        self.assertEquals('failed', self._storage.raid_status())

    def test_lastTransaction(self):
        self.assertEquals(ZODB.utils.z64, self._storage.lastTransaction())
        self.assertEquals(ZODB.utils.z64, self._backend(0).lastTransaction())
        self.assertEquals(ZODB.utils.z64, self._backend(1).lastTransaction())
        self._dostore()
        lt = self._storage.lastTransaction()
        self.assertNotEquals(ZODB.utils.z64, lt)
        self.assertEquals(lt, self._backend(0).lastTransaction())
        self.assertEquals(lt, self._backend(1).lastTransaction())

    def test_lastTransaction_degrading(self):
        self._disable_storage(0)
        self.assertEquals(ZODB.utils.z64, self._storage.lastTransaction())
        self._disable_storage(0)
        self.assertEquals('failed', self._storage.raid_status())
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.lastTransaction)

    def test_len_degrading(self):
        # Brrrr. ClientStorage doesn't seem to implement __len__ correctly.
        self.assertEquals(0, len(self._storage))
        self.assertEquals(0, len(self._backend(0)))
        self.assertEquals(0, len(self._backend(1)))
        self.assertEquals
        self._dostore(
            revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(1, len(self._storage))
        self.assertEquals(1, len(self._backend(0)))
        self.assertEquals(1, len(self._backend(1)))

        self._disable_storage(0)
        self._dostore(
            revid='\x00\x00\x00\x00\x00\x00\x00\x02')
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(2, len(self._storage))
        self.assertEquals(2, len(self._backend(0)))

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.__len__)

    def test_load_store_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._storage.load, oid)
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(0).load, oid)
        self.assertRaises(ZODB.POSException.POSKeyError,
                          self._backend(1).load, oid)

        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        data_record, serial = self._storage.load(oid)
        self.assertEquals('((U\x10ZODB.tests.MinPOq\x01U\x05MinPOq\x02tq\x03Nt.}q\x04U\x05valueq\x05K\x07s.',
                          data_record)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))
        self.assertEquals((data_record, serial), self._backend(1).load(oid))

        self._disable_storage(0)
        self.assertEquals((data_record, serial), self._storage.load(oid))
        self.assertEquals((data_record, serial), self._backend(0).load(oid))

        oid = self._storage.new_oid()
        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x02')
        data_record, serial = self._storage.load(oid)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.load, oid)

    def test_load_can_be_failed(self):
        # ClientStorage does not directly call `load` but
        # `loadEx` which in turn calls `load` on the storage.
        # Unfortunately `storage.load` is also rebound onto the storage
        # server so in the future the fail() might not work. To avoid
        # hard-to-debug errors in the future, we test that fail('load')
        # actually does make the `load` call fail.
        oid = self._storage.new_oid()
        self._backend(0).fail('load')
        self.assertRaises(Exception, self._backend(0).load, oid)

    def test_load_degrading2(self):
        # If this test fails weirdly, please check that the test above works
        # correctly before losing hair.
        oid = self._storage.new_oid()
        self._dostore(oid=oid, revid='\x00\x00\x00\x00\x00\x00\x00\x01')
        self._backend(0).fail('load')
        data_record, serial = self._storage.load(oid)
        self.assertEquals('((U\x10ZODB.tests.MinPOq\x01U\x05MinPOq\x02tq\x03Nt.}q\x04U\x05valueq\x05K\x07s.',
                          data_record)
        self.assertEquals(self._storage.lastTransaction(), serial)
        self.assertEquals((data_record, serial), self._backend(0).load(oid))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('load')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.load, oid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_loadBefore_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._storage.loadBefore, oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(0).loadBefore,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(1).loadBefore,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertEquals('optimal', self._storage.raid_status())

        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        revid2 = self._dostoreNP(oid=oid, revid=revid, data='bar')
        data_record, serial, end_tid = self._storage.loadBefore(oid, revid2)
        self.assertEquals('foo', data_record)
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(1).loadBefore(oid, revid2))

        self._disable_storage(0)
        self.assertEquals((data_record, serial, end_tid),
                          self._storage.loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadBefore, oid, revid2)

    def test_loadBefore_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        revid2 = self._dostoreNP(oid=oid, revid=revid, data='bar')
        data_record, serial, end_tid = self._storage.loadBefore(oid, revid2)
        self.assertEquals('foo', data_record)
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(1).loadBefore(oid, revid2))

        self._backend(0).fail('loadBefore')
        self.assertEquals((data_record, serial, end_tid),
                          self._storage.loadBefore(oid, revid2))
        self.assertEquals((data_record, serial, end_tid),
                          self._backend(0).loadBefore(oid, revid2))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('loadBefore')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadBefore, oid, revid2)
        self.assertEquals('failed', self._storage.raid_status())

    def test_loadSerial_degrading1(self):
        oid = self._storage.new_oid()
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._storage.loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(0).loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertRaises(
            ZODB.POSException.POSKeyError,
            self._backend(1).loadSerial,
            oid, '\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertEquals('optimal', self._storage.raid_status())

        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self._dostoreNP(oid=oid, revid=revid, data='bar')

        data_record = self._storage.loadSerial(oid, revid)
        self.assertEquals('foo', data_record)
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(1).loadSerial(oid, revid))

        self._disable_storage(0)
        self.assertEquals(data_record,
                          self._storage.loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadSerial, oid, revid)

    def test_loadSerial_degrading2(self):
        oid = self._storage.new_oid()
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self._dostoreNP(oid=oid, revid=revid, data='bar')

        data_record = self._storage.loadSerial(oid, revid)
        self.assertEquals('foo', data_record)
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(1).loadSerial(oid, revid))
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(0).fail('loadSerial')
        self.assertEquals(data_record,
                          self._storage.loadSerial(oid, revid))
        self.assertEquals(data_record,
                          self._backend(0).loadSerial(oid, revid))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('loadSerial')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadSerial, oid, revid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_new_oid_degrading1(self):
        self.assertEquals(8, len(self._storage.new_oid()))
        self._disable_storage(0)
        self.assertEquals(8, len(self._storage.new_oid()))
        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.new_oid)

    def test_new_oid_degrading2(self):
        self.assertEquals(8, len(self._storage.new_oid()))
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(0)._oids = None
        self._backend(0).fail('new_oid')
        self.assertEquals(8, len(self._storage.new_oid()))
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0)._oids = None
        self._backend(0).fail('new_oid')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.new_oid)
        self.assertEquals('failed', self._storage.raid_status())

    def test_pack_degrading1(self):
        # We store differently sized data for each revision so that packing
        # definitely yields different file sizes.
        # We work on the root object to avoid garbage collection
        # kicking in.
        oid = ZODB.utils.z64
        revid = self._dostore(oid=oid, revid=None, data=1)
        revid2 = self._dostore(oid=oid, revid=revid, data=2)

        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._backend(1).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._backend(1).getSize())
        self.assertEquals(130, self._storage.getSize())

        revid3 = self._dostore(oid=oid, revid=revid2, data=3)
        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._backend(1).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._disable_storage(0)
        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._storage.getSize())

        self._dostore(oid=oid, revid=revid3, data=4)
        self.assertEquals(256, self._storage.getSize())
        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.pack,
                          time.time(), ZODB.serialize.referencesf)

    def test_pack_degrading2(self):
        # We store differently sized data for each revision so that packing
        # definitely yields different file sizes.
        # We work on the root object to avoid garbage collection
        # kicking in.
        oid = ZODB.utils.z64
        revid = self._dostore(oid=oid, revid=None, data=1)
        revid2 = self._dostore(oid=oid, revid=revid, data=2)
        self.assertEquals(256, self._storage.getSize())

        self._backend(0).fail('pack')
        self._storage.pack(time.time(), ZODB.serialize.referencesf)
        self.assertEquals(130, self._backend(0).getSize())
        self.assertEquals(130, self._storage.getSize())
        self.assertEquals('degraded', self._storage.raid_status())

        revid3 = self._dostore(oid=oid, revid=revid2, data=3)
        self.assertEquals(256, self._backend(0).getSize())
        self.assertEquals(256, self._storage.getSize())

        self._backend(0).fail('pack')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.pack,
                          time.time(), ZODB.serialize.referencesf)
        self.assertEquals('failed', self._storage.raid_status())

    def test_store_degrading2(self):
        oid = ZODB.utils.z64

        self._backend(0).fail('store')
        revid = self._dostoreNP(oid=oid, revid=None, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        self._backend(0).fail('store')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._dostoreNP,
                          oid=oid, revid=revid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_begin_degrading(self):
        self._backend(0).fail('tpc_begin')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_begin')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._dostoreNP,
                          oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_vote_degrading(self):
        self._backend(0).fail('tpc_vote')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_vote')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._dostoreNP,
                          oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_finish_degrading(self):
        self._backend(0).fail('tpc_finish')
        oid = self._storage.new_oid()
        self._dostoreNP(oid=oid, data='foo')
        self.assertEquals('foo', self._backend(0).load(oid)[0])
        self.assertEquals('foo', self._storage.load(oid)[0])
        self.assertEquals('degraded', self._storage.raid_status())

        oid = self._storage.new_oid()
        self._backend(0).fail('tpc_finish')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._dostoreNP,
                          oid=oid, data='bar')
        self.assertEquals('failed', self._storage.raid_status())

    def test_tpc_abort_not_degrading(self):
        # tpc_abort (in combination with ClientStorage) will never cause
        # degradation, even if it raises an exception.
        # This is because of an asynchronous call made by ClientStorage.
        # For us this is ok. If there really is something wrong with the
        # storage, we'll know in the next synchronous call.
        self._backend(0).fail('tpc_abort')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.tpc_abort(t)
        # tpc_abort is asynchronous. We make another synchronous call to make
        # sure that it was already executed.
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self.assertEquals('optimal', self._storage.raid_status())

    def test_blob_usage(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading1(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading1_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._disable_storage(0)
        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.storeBlob,
                          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)

    def test_storeBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('storeBlob')
        # The server doesn't call its storage's storeBlob right away but only
        # when tpc_vote ist called.
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertEquals('optimal', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading2_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._backend(0).fail('storeBlob')
        self._backend(1).fail('storeBlob')
        # The server doesn't call its storage's storeBlob right away but only
        # when tpc_vote ist called.
        self._storage.storeBlob(
            oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.tpc_vote, t)

    def test_storeBlob_degrading3(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        def fail(*args, **kw):
            raise Exception()
        self._backend(0).storeBlob = fail
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self.assertEquals('degraded', self._storage.raid_status())
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        stored_file_name = self._storage.loadBlob(
            oid, self._storage.lastTransaction())
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

    def test_storeBlob_degrading3_both(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        def fail(*args, **kw):
            raise Exception()
        self._backend(0).storeBlob = fail
        self._backend(1).storeBlob = fail
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.storeBlob,
                          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)

    def test_loadBlob_degrading1(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)

        last_transaction = self._storage.lastTransaction()
        self._disable_storage(0)
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())

        self._disable_storage(0)
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadBlob, oid, last_transaction)

    def test_loadBlob_degrading2(self):
        oid = self._storage.new_oid()
        handle, blob_file_name = tempfile.mkstemp()
        open(blob_file_name, 'w').write('I am a happy blob.')
        t = transaction.Transaction()
        self._storage.tpc_begin(t)
        self._storage.storeBlob(
          oid, ZODB.utils.z64, 'foo', blob_file_name, '', t)
        self._storage.tpc_vote(t)
        self._storage.tpc_finish(t)
        last_transaction = self._storage.lastTransaction()

        # Clear cache.
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        os.unlink(stored_file_name)

        self._backend(0).fail('loadBlob')
        stored_file_name = self._storage.loadBlob(oid, last_transaction)
        self.assertEquals('I am a happy blob.',
                          open(stored_file_name, 'r').read())
        self.assertEquals('degraded', self._storage.raid_status())

        # Clear cache.
        os.unlink(stored_file_name)

        self._backend(0).fail('loadBlob')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.loadBlob, oid, last_transaction)
        self.assertEquals('failed', self._storage.raid_status())

    def test_temporaryDirectory(self):
        working_dir = tempfile.mkdtemp()
        storage = ZODB.config.storageFromString("""
        %%import gocept.zeoraid
        <raidstorage>
          blob-dir %(wd)s/blobs
          <filestorage foo>
            path %(wd)s/Data.fs
          </filestorage>
        </raidstorage>
        """ % {'wd': working_dir})
        self.assertEquals(os.path.join(working_dir, 'blobs', 'tmp'),
                          storage.temporaryDirectory())
        self.assert_(os.path.isdir(storage.temporaryDirectory()))
        self.assert_(storage.blob_fshelper.isSecure(
            storage.temporaryDirectory()))
        shutil.rmtree(working_dir)

    def test_supportsUndo_required(self):
        class Opener(object):
            name = 'foo'
            def open(self):
                return ZODB.MappingStorage.MappingStorage()

        self.assertRaises(AssertionError,
                          gocept.zeoraid.storage.RAIDStorage,
                          'name', [Opener()])

    def test_supportsUndo(self):
        self.assertEquals(True, self._storage.supportsUndo())


class ZEOReplicationStorageTests(ZEOStorageBackendTests,
                                 ReplicationStorageTests,
                                 ThreadTests.ThreadTests):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZEOReplicationStorageTests, "check"))
    suite.addTest(unittest.makeSuite(FailingStorageTests2Backends))
    return suite
