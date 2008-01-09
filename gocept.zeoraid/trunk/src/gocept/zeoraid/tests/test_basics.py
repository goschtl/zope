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


class ZEOReplicationStorageTests(ZEOStorageBackendTests,
                                 ReplicationStorageTests,
                                 ThreadTests.ThreadTests):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZEOReplicationStorageTests, "check"))
    return suite

if __name__=='__main__':
    unittest.main()
