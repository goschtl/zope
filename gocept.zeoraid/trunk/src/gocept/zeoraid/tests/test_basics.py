import unittest
import tempfile
import os

from ZODB.tests import StorageTestBase, BasicStorage, \
             TransactionalUndoStorage, VersionStorage, \
             TransactionalUndoVersionStorage, PackableStorage, \
             Synchronization, ConflictResolution, HistoryStorage, \
             Corruption, RevisionStorage, PersistentStorage, \
             MTStorage, ReadOnlyStorage, RecoveryStorage

import gocept.zeoraid.storage

from ZODB.FileStorage.FileStorage import FileStorage

from ZEO.ClientStorage import ClientStorage
from ZEO.tests import forker, CommitLockTests, ThreadTests
from ZEO.tests.testZEO import get_port


class DemoOpener(object):

    class_ = FileStorage

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs or {}

    def open(self, **kwargs):
        return self.class_(self.name, **self.kwargs)


class ZEOOpener(DemoOpener):

    class_ = ClientStorage


class FileStorageBackendTests(StorageTestBase.StorageTestBase):

    def open(self, **kwargs):
        # A RAIDStorage requires openers, not storages.
        s1 = DemoOpener('s1.fs')
        s2 = DemoOpener('s2.fs')

        self._storage = gocept.zeoraid.storage.RAIDStorage('teststorage',
                                                           [s1, s2], **kwargs)

    def setUp(self):
        self.open()

    def tearDown(self):
        self._storage.close()
        self._storage.cleanup()
        os.unlink('s1.fs')
        os.unlink('s2.fs')


class ZEOStorageBackendTests(StorageTestBase.StorageTestBase):

    def open(self, **kwargs):
        self._storage = gocept.zeoraid.storage.RAIDStorage('teststorage',
                                                           self._storages, **kwargs)

    def setUp(self):
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
        VersionStorage.VersionStorage,
        TransactionalUndoVersionStorage.TransactionalUndoVersionStorage,
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
    pass


class FSReplicationStorageTests(FileStorageBackendTests,
                                ReplicationStorageTests):
    pass


class ZEOReplicationStorageTests(ZEOStorageBackendTests,
                                 ReplicationStorageTests,
                                 ThreadTests.ThreadTests):
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FSReplicationStorageTests, "check"))
    suite.addTest(unittest.makeSuite(ZEOReplicationStorageTests, "check"))
    return suite

if __name__=='__main__':
    unittest.main()
