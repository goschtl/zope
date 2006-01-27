import unittest
import doctest
from zope.testing import module
from ZODB import ConflictResolution, MappingStorage, POSException

from zope.zasync import queue

METHODPICKLE_NAME = 'zope.zasync.methodpickle_txt'

class ConflictResolvingMappingStorage(
    MappingStorage.MappingStorage,
    ConflictResolution.ConflictResolvingStorage):

    def __init__(self, name='ConflictResolvingMappingStorage'):
        MappingStorage.MappingStorage.__init__(self, name)
        self._old = {}

    def loadSerial(self, oid, serial):
        self._lock_acquire()
        try:
            old_info = self._old[oid]
            try:
                return old_info[serial]
            except KeyError:
                raise POSException.POSKeyError(oid)
        finally:
            self._lock_release()

    def store(self, oid, serial, data, version, transaction):
        if transaction is not self._transaction:
            raise POSException.StorageTransactionError(self, transaction)

        if version:
            raise POSException.Unsupported("Versions aren't supported")

        self._lock_acquire()
        try:
            if oid in self._index:
                oserial = self._index[oid][:8]
                if serial != oserial:
                    rdata = self.tryToResolveConflict(
                        oid, oserial, serial, data)
                    if rdata is None:
                        raise POSException.ConflictError(
                            oid=oid, serials=(oserial, serial), data=data)
                    else:
                        data = rdata
            self._tindex[oid] = self._tid + data
            self._old.setdefault(oid, {})[self._tid] = data
        finally:
            self._lock_release()
        return self._tid

    def _finish(self, tid, user, desc, ext):
        self._index.update(self._tindex)
        self._ltid = self._tid

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'queue.txt', globs={'Queue':queue.PersistentQueue}),
        doctest.DocFileSuite(
            'queue.txt',
            globs={'Queue':lambda: queue.CompositePersistentQueue(2)}),
        doctest.DocFileSuite(
            'methodpickle.txt',
            setUp=lambda test: module.setUp(test, METHODPICKLE_NAME),
            tearDown=lambda test: module.tearDown(test, METHODPICKLE_NAME)),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
