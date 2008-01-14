import unittest
import tempfile
import os

import zope.interface.verify

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
                                            cache_size=2000000,
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
            self._servers.append(adminaddr)
            self._storages.append(ZEOOpener(zport, storage='1',
                                            cache_size=2000000,
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
        self.assertEquals(32, self._backend(0).getSize())
        self.assertEquals(32, self._backend(1).getSize())
        self.assertEquals(32, self._storage.getSize())
        self._storage.close()
        self.assertRaises(gocept.zeoraid.interfaces.RAIDClosedError,
                          self._storage.getSize)

    def test_getsize_degrading(self):
        self._backend(0).fail('getSize')
        # This doesn't get noticed because ClientStorage already knows
        # the answer and caches it. Therefore calling getSize can never
        # degrade or fail a RAID.
        self.assertEquals(32, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

        self._backend(1).fail('getSize')
        self.assertEquals(32, self._storage.getSize())
        self.assertEquals('optimal', self._storage.raid_status())

    def test_history(self):
        self.assertEquals((), self._backend(0).history(ZODB.utils.z64, ''))
        self.assertEquals((), self._backend(1).history(ZODB.utils.z64, ''))
        self.assertEquals((), self._storage.history(ZODB.utils.z64, ''))

    def test_history_degrading(self):
        self._backend(0).fail('history')
        self.assertEquals((), self._storage.history(ZODB.utils.z64, ''))
        self.assertEquals('degraded', self._storage.raid_status())
        self._backend(0).fail('history')
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.history, ZODB.utils.z64, '')
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
        self._storage.raid_disable(self._storage.storages_optimal[0])
        self.assertEquals(ZODB.utils.z64, self._storage.lastTransaction())
        self._storage.raid_disable(self._storage.storages_optimal[0])
        self.assertEquals('failed', self._storage.raid_status())
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.lastTransaction)

    def test_len_degrading(self):
        # Brrrr. ClientStorage doesn't seem to implement __len__ correctly.
        self.assertEquals(0, len(self._storage))
        self.assertEquals(0, len(self._backend(0)))
        self.assertEquals(0, len(self._backend(1)))
        self.assertEquals
        self._dostore()
        self._dostore()
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(0, len(self._storage))
        self.assertEquals(0, len(self._backend(0)))
        self.assertEquals(0, len(self._backend(1)))

        self._storage.raid_disable(self._storage.storages_optimal[0])
        self._dostore()
        # See above. This shouldn't be 0 if ClientStorage worked correctly.
        self.assertEquals(0, len(self._storage))
        self.assertEquals(0, len(self._backend(0)))

        self._storage.raid_disable(self._storage.storages_optimal[0])
        self.assertRaises(gocept.zeoraid.interfaces.RAIDError,
                          self._storage.__len__)


class ZEOReplicationStorageTests(ZEOStorageBackendTests,
                                 ReplicationStorageTests,
                                 ThreadTests.ThreadTests):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZEOReplicationStorageTests, "check"))
    suite.addTest(unittest.makeSuite(FailingStorageTests2Backends))
    return suite

if __name__=='__main__':
    unittest.main()
