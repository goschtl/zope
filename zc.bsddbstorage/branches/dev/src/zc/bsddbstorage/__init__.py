##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

from bsddb3 import db
from ZODB.utils import p64, u64, z64
import cPickle
import marshal
import os
import tempfile
import threading
import time
import zc.lockfile
import ZODB
import ZODB.blob
import ZODB.ConflictResolution
import ZODB.interfaces
import ZODB.POSException
import ZODB.TimeStamp
import zope.interface

def n64(tid):
    return p64(868082074056920076L-u64(tid))

# XXX Still need checkpoint strategy.
# Maybe initial config file when creating env.

def retry_on_deadlock(f):

    def func(*args, **kw):
        while 1:
            try:
                result = f(*args, **kw)
            except db.DBLockDeadlockError:
                pass
            else:
                return result

    return func

class BSDDBStorage(
    ZODB.blob.BlobStorageMixin,
    ZODB.ConflictResolution.ConflictResolvingStorage,
    ):

    zope.interface.implements(
        ZODB.interfaces.IStorage,
        ZODB.interfaces.IStorageRestoreable,
        ZODB.interfaces.IStorageIteration,
# XXX?         ZODB.interfaces.IStorageCurrentRecordIteration,
        ZODB.interfaces.IExternalGC,
        )

    def __init__(self, envpath, blob_dir=None,
                 pack = 3*86400,
                 create = False,
                 read_only = False,
                 detect_locks = True,
                 remove_logs = True,
                 ):
        self.__name__ = envpath
        envpath = os.path.abspath(envpath)
        if create:
            if os.path.isdir(envpath):
                ZODB.blob.remove_committed_dir(envpath)
            if blob_dir and os.path.isdir(blob_dir):
                ZODB.blob.remove_committed_dir(blob_dir)
        self._pack = pack
        self._read_only = read_only
        if not os.path.isdir(envpath):
            os.mkdir(envpath)

        if not read_only:
            # Create the lock file
            self._lock_file = zc.lockfile.LockFile(
                os.path.join(envpath, 'zodb.lock'))

        if blob_dir:
            blob_dir = os.path.abspath(blob_dir)
            self._blob_init(blob_dir)
            zope.interface.alsoProvides(
                self, ZODB.interfaces.IBlobStorageRestoreable)
        else:
            self._blob_init_no_blobs()
        self.blob_dir = blob_dir

        self.env = db.DBEnv()
        if detect_locks:
            self.env.set_lk_detect(db.DB_LOCK_MINWRITE)
        if remove_logs:
            self.env.log_set_config(db.DB_LOG_AUTO_REMOVE, 1)
        flags = (db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_MPOOL |
                 db.DB_INIT_TXN | db.DB_THREAD)
        if not read_only:
            # Running recovery basically breaks any other processes
            # that have the env open, so we only do recover for the "main"
            # non-read-only process.
            flags |=  db.DB_RECOVER | db.DB_CREATE
        self.env.open(envpath, flags)

        # data: {oid -> [tid+data]}
        self.data = db.DB(self.env)
        self.data.set_flags(db.DB_DUPSORT)
        self.data.open('data', dbtype=db.DB_HASH,
                       flags=(db.DB_CREATE | db.DB_THREAD | db.DB_AUTO_COMMIT |
                              db.DB_MULTIVERSION),
                       )
        self.datapath = os.path.abspath(os.path.join(envpath, 'data'))

        # transaction_oids: {tid->[oids]}
        self.transaction_oids = db.DB(self.env)
        self.transaction_oids.set_flags(db.DB_DUPSORT)
        self.transaction_oids.open('transaction_oids', dbtype=db.DB_BTREE,
                                   flags=(db.DB_CREATE | db.DB_THREAD |
                                          db.DB_AUTO_COMMIT |
                                          db.DB_MULTIVERSION),
                                   )

        # transactions: {tid ->status+transaction_pickle}
        self.transactions = db.DB(self.env)
        self.transactions.open('transactions', dbtype=db.DB_BTREE,
                               flags=(db.DB_CREATE | db.DB_THREAD |
                                      db.DB_AUTO_COMMIT | db.DB_MULTIVERSION),
                               )

        # Misc info:
        # pack-trans
        self.misc = db.DB(self.env)
        self.misc.open('misc', dbtype=db.DB_HASH,
                       flags=(db.DB_CREATE | db.DB_THREAD | db.DB_AUTO_COMMIT |
                              db.DB_MULTIVERSION),
                       )

        t = time.time()
        t = self._ts = ZODB.TimeStamp.TimeStamp(
            *(time.gmtime(t)[:5] + (t%60,)))
        self._tid = repr(t)
        self._transaction = self._txn = None

        self._commit_lock = threading.Lock()
        _lock = threading.Lock()

        # BlobStorageMixin requires these. I'm getting annoyed. :)
        self._lock_acquire = _lock.acquire
        self._lock_release = _lock.release

        # The current lock is used to make sure we consistently order
        # information about current data for objects.  In particular,
        # we want to avoid the following scenario:
        # - A thread reads current data via load
        # - another thread updates data via tpc_finish and sends invalidations
        # - The first thread's load returns the old data after the
        #   invalidations have been processed.
        self._current_lock = RWLock() 

    def txn(self, flags=0):
        return TransactionContext(self.env.txn_begin(flags=flags))

    def cursor(self, database, txn=None, flags=0):
        return CursorContext(database.cursor(txn, flags))

    def close(self):
        self.data.close()
        self.transaction_oids.close()
        self.transactions.close()
        self.env.close()
        if not self._read_only:
            self._lock_file.close()

    def getName(self):
        return self.__name__

    def getSize(self):
        return os.stat(self.datapath).st_size

    def _history_entry(self, record, txn):
        tid = n64(record[:8])
        transaction = cPickle.loads(self.transactions.get(tid, txn=txn)[1:])
        transaction.update(
            size = len(record)-8,
            tid = tid,
            serial = tid,
            time = ZODB.TimeStamp.TimeStamp(tid).timeTime(),
            )
        return transaction

    def history(self, oid, size=1):
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                kv = cursor.get(oid, db.DB_SET)
                if kv is None:
                    raise ZODB.POSException.POSKeyError(oid)
                k, record = kv
                if len(record) == 8:
                    raise ZODB.POSException.POSKeyError(oid)
                result = [self._history_entry(record, txn)]
                while len(result) < size:
                    kv = cursor.get(oid, db.DB_NEXT_DUP)
                    if kv is None:
                        break
                    result.append(self._history_entry(kv[1], txn))

            return result

    def isReadOnly(self):
        return self._read_only

    def iterator(self, start=z64, stop='\f'*8):
        return StorageIterator(self._iterator(start, stop))

    def _iterator(self, start, stop):
        with self.txn(db.DB_READ_COMMITTED) as txn:
            with self.cursor(self.transactions, txn) as transactions:
                kv = transactions.get(start, flags=db.DB_SET_RANGE)
                while kv:
                    tid, ext = kv
                    if tid > stop:
                        break
                    yield Records(self, txn, tid, ext[0], ext[1:])
                    kv = transactions.get(tid, flags=db.DB_NEXT)

#     def record_iternext(next=None):
#         pass # XXX

    def lastTransaction(self):
        with self.txn() as txn:
            with self.cursor(self.transactions, txn) as cursor:
                kv = cursor.get(db.DB_LAST)
                if kv is None:
                    return None
                return kv[0]

    def __len__(self):
        # XXX this is probably very expensive, but we need this for the
        # tests. :(  Need to check this out with a big db to decode what the
        # cost is.  Usually, accuracy isn't that important.
        return self.data.stat()['nkeys']
        #return self.data.stat(db.DB_FAST_STAT)['nkeys']

    def load(self, oid, version=''):
        with self._current_lock.read():
            with self.txn() as txn:
                with self.cursor(self.data, txn) as cursor:
                    kv = cursor.get(oid, db.DB_SET)
                    if kv:
                        record = kv[1]
                        data = record[8:]
                        if data:
                            return data, n64(record[:8])

                    raise ZODB.POSException.POSKeyError(oid)

    def loadBefore(self, oid, tid):
        ntid = p64(868082074056920076L-(u64(tid)-1))
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                # Step 1, find the record
                kr = cursor.get(oid, ntid, db.DB_GET_BOTH_RANGE)
                if kr is None:
                    kr = cursor.get(oid, db.DB_SET)
                    if kr is None:
                        raise ZODB.POSException.POSKeyError(oid)

                record = kr[1]
                rtid = n64(record[:8])
                assert kr[0] == oid
                if len(record) == 8: # The object was deleted
                    raise ZODB.POSException.POSKeyError(oid)

                if rtid >= tid:
                    return None

                # Now, get the next tid:
                kr = cursor.get(oid, ntid, db.DB_PREV_DUP, dlen=8, doff=0)
                if kr is None:
                    nexttid = None
                else:
                    assert kr[0] == oid
                    nexttid = n64(kr[1])

                return record[8:], rtid, nexttid

    def loadSerial(self, oid, serial):
        serial = n64(serial)
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.data, txn) as cursor:
                kr = cursor.get(oid, serial, flags=db.DB_GET_BOTH_RANGE)
                if kr is None:
                    kr = cursor.get(oid, flags=db.DB_SET)
                if kr:
                    k, record = kr
                    if k == oid and record[:8] == serial:
                        data = record[8:]
                        if data:
                            return data

                raise ZODB.POSException.POSKeyError(oid, serial)

    def new_oid(self):
        with self.txn() as txn:
            oid = p64(u64(self.misc.get('oid', z64, txn, db.DB_RMW))+1)
            self.misc.put('oid', oid, txn)
            return oid

    def pack(self, pack_time=None, referencesf=None, gc=False):
        assert not gc, "BSDDBStorage doesn't do garbage collection."
        if pack_time is None:
            pack_time = time.time()-self._pack
        pack_tid = timetime2tid(pack_time)
        while self._pack1(pack_tid):
            pass
        if self.blob_dir:
            self._remove_empty_notlast_blob_directories(self.blob_dir)

    @retry_on_deadlock
    def _pack1(self, pack_tid):
        # Pack one transaction. Get the next transaction we haven't yet
        # packed and stop if it is > pack_tid.
        # This is done as a transaction.
        removed_blobs = []
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            # Pick a tid just past the last one we packed:
            tid = p64(u64(self.misc.get('pack', z64, txn=txn))+1)
            if tid > pack_tid:
                return None

            with self.cursor(self.transactions, txn) as transactions:
                kv = transactions.get(
                    tid, flags=db.DB_SET_RANGE, doff=0, dlen=0)
                if kv is None:
                    return None
                tid = kv[0]

                # Set the status flag to indicate that the transaction
                # was packed.
                transactions.put(tid, 'p', db.DB_CURRENT, doff=0, dlen=1)

            ntid = n64(tid)
            
            with self.cursor(self.transaction_oids, txn) as transaction_oids:
                # Find the smallest tid >= the one we picked
                ttid, oid = transaction_oids.get(tid, flags=db.DB_SET_RANGE)
                assert ttid == tid

                # Iterate over the oids for this tid and pack each one.
                # Note that we treat the tid we're looking at as the
                # pack time. That is, as we look at each transaction,
                # we pack to that time.  This way, we can pack
                # *very* incrementally.
                while 1:

                    # Find the first record for the oid whos tid is <=
                    # the pack time. (we use negative tids, so >=)
                    # This is the current record as of the pack time
                    with self.cursor(self.data, txn) as data:
                        kr = data.get(oid, ntid, flags=db.DB_GET_BOTH_RANGE)
                        if not kr:
                            kr = data.get(oid, flags=db.DB_SET)
                            if kr[1][:8] < ntid:
                                # the one record found is after the pack time
                                continue

                        doid, record = kr
                        assert doid == oid
                        ndtid = record[:8]
                        assert ndtid >= ntid
                        if len(record) == 8:
                            # delete record, so we can delete the record,
                            # which with the deletions below, will
                            # delete the oid
                            data.delete()
                            deleted_oid = True
                        else:
                            deleted_oid = False

                        # OK, we have the current record as of the tid,
                        # we can remove later ones

                        while 1:
                            kv = data.get(oid, ntid, flags=db.DB_NEXT_DUP)
                            if kv is None:
                                break
                            doid, record = kv
                            assert doid == oid
                            data.delete()
                            ndtid = record[:8]
                            dtid = n64(ndtid)
                            pickle = record[8:]
                            if (self.blob_dir and
                                ZODB.blob.is_blob_record(pickle)
                                ):
                                if deleted_oid:
                                    if ((not removed_blobs) or
                                        (removed_blobs[-1] != oid)):
                                        removed_blobs.append(oid)
                                else:
                                    removed_blobs.append(oid+dtid)
                            # clean up transaction_oids and
                            # maybe transactions
                            self._pack_remove_oid_tid(dtid, oid, txn)

                    # continue iterating over the oids for this tid
                    kv = transaction_oids.get(tid, flags=db.DB_NEXT_DUP)
                    if kv is None:
                        break
                    assert kv[0] == tid
                    oid = kv[1]

            self.misc.put('pack', tid, txn=txn)

        if removed_blobs:
            self._remove_blob_files_tagged_for_removal_during_pack(
                removed_blobs)

        return tid

    def _pack_remove_oid_tid(self, tid, oid, txn):
        with self.cursor(self.transaction_oids, txn) as transaction_oids:
            kr = transaction_oids.get(tid, oid, flags=db.DB_GET_BOTH_RANGE)
            if not kr:
                kr = transaction_oids.get(tid, flags=db.DB_SET)
            ttid, toid = kr
            if toid != oid or ttid != tid:
                raise AssertionError("Bad oid+tid lookup",
                                     oid, tid, toid, ttid)
            transaction_oids.delete()
            # OK, we deleted the record. Maybe it was the last one. Try to get
            # the first, and, if we can't, then delete the transaction record.
            kv = transaction_oids.get(tid, flags=db.DB_SET)
            if kv is None:
                # OK, no more oids for this tid, remive it from transactions
                self.transactions.delete(tid, txn)

    def _remove_blob_files_tagged_for_removal_during_pack(self, removed):
        for oid in removed:
            if len(oid) == 8:
                # oid is garbage, re/move dir
                path = self.fshelper.getPathForOID(oid)
                if os.path.exists(path):
                    ZODB.blob.remove_committed_dir(path)
            else:
                tid = oid[8:]
                oid = oid[:8]
                path = self.fshelper.getBlobFilename(oid, tid)
                if os.path.exists(path):
                    ZODB.blob.remove_committed(path)

    def _remove_empty_notlast_blob_directories(self, dir):
        # clean up empty blob dirs. This relies on the
        # fact that oids are allocates sequentially
        paths = filter(os.path.isdir,
                       [os.path.join(dir, name)
                        for name in sorted(os.listdir(dir))
                        if name.lower().startswith('0x')])
        if not paths:
            return
        self._remove_empty_notlast_blob_directories(paths.pop())
        for path in paths:
            self._remove_empty_recursively_directory(path)

    def _remove_empty_recursively_directory(self, dir):
        if not os.path.isdir(dir):
            return False
        for name in os.listdir(dir):
            if not self._remove_empty_recursively_directory(
                os.path.join(dir, name)):
                return False
        os.rmdir(dir)
        return True

    def registerDB(self, db):
        pass

    def sortKey(self):
        return self.__name__

    def store(self, oid, oldserial, data, version, transaction):
        assert not version
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        result = self._tid
        committed_tid = self.data.get(oid, dlen=8, doff=0)
        if committed_tid is not None:
            committed_tid = n64(committed_tid)
            if committed_tid != oldserial:
                rdata = self.tryToResolveConflict(oid, committed_tid,
                                                  oldserial, data)
                if rdata is None:
                    raise ZODB.POSException.ConflictError(
                        oid=oid, serials=(committed_tid, oldserial),
                        data=data)
                else:
                    data = rdata
                    result = ZODB.ConflictResolution.ResolvedSerial

        marshal.dump((oid, n64(self._tid)+data), self._log_file)
        return result

    def restore(self, oid, serial, data, version, prev_txn, transaction):
        assert not version
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        marshal.dump((oid, n64(serial)+data), self._log_file)

    def deleteObject(self, oid, oldserial, transaction):
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)
        committed_tid = self.data.get(oid, dlen=8, doff=0)
        if committed_tid is not None and n64(committed_tid) != oldserial:
            raise ZODB.POSException.ConflictError(
                oid=oid, serials=(n64(committed_tid), oldserial))

        marshal.dump((oid, n64(self._tid)), self._log_file)

    def tpc_begin(self, transaction, tid=None, status=' '):
        if self._read_only:
            raise ZODB.POSException.ReadOnlyError()

        if self._transaction is transaction:
            return
        self._commit_lock.acquire()
        self._transaction = transaction

        ext = transaction._extension.copy()
        ext['user_name'] = transaction.user
        ext['description'] = transaction.description
        ext = status+cPickle.dumps(ext, 1)

        if tid is None:
            now = time.time()
            t = ZODB.TimeStamp.TimeStamp(
                *(time.gmtime(now)[:5] + (now % 60,)))
            self._ts = t = t.laterThan(self._ts)
            self._tid = tid = repr(t)
        else:
            self._ts = ZODB.TimeStamp.TimeStamp(tid)
            self._tid = tid

        fd, path = tempfile.mkstemp('bsddb')
        self._log_file = open(path, 'r+b')
        os.close(fd)
        marshal.dump((tid, ext), self._log_file)

    def tpc_abort(self, transaction):
        if transaction is not self._transaction:
            return
        try:
            if self._txn is not None:
                self._txn.abort()
            self._blob_tpc_abort()
            self._transaction = self._txn = None
        finally:
            self._commit_lock.release()

    def tpc_finish(self, transaction, func = lambda tid: None):
        if transaction is not self._transaction:
            return

        with self._current_lock.write():
            func(self._tid)
            self._txn.commit()
            self._blob_tpc_finish()
            self._transaction = self._txn = None
            self._commit_lock.release()

    _transaction_id_suffix = 'x' * (db.DB_GID_SIZE - 8)
    def tpc_vote(self, transaction):
        self._txn = txn = self.env.txn_begin()
        self._log_file.seek(0)
        tid, ext = marshal.load(self._log_file)
        self.transactions.put(tid, ext, txn=txn)
        for oid, record in marhal_iterate(self._log_file):
            self.data.put(oid, record, txn=txn)
            self.transaction_oids.put(tid, oid, txn=txn)
        txn.prepare(self._tid+self._transaction_id_suffix)

def marhal_iterate(f):
    while 1:
        try:
            yield marshal.load(f)
        except EOFError:
            break

class TransactionContext(object):

    def __init__(self, txn):
        self.txn = txn

    def __enter__(self):
        return self.txn

    def __exit__(self, t, v, tb):
        if t is not None:
            self.txn.abort()
        else:
            self.txn.commit()

class CursorContext(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, t, v, tb):
        self.cursor.close()

def timetime2tid(timetime):
    return repr(ZODB.TimeStamp.TimeStamp(
        *time.gmtime(timetime)[:5]
        +(time.gmtime(timetime)[5]+divmod(timetime,1)[1],)
        ))

def DB(path, blob_dir=None, pack=3*86400,
       read_only=False, create=False,
       detect_locks = True,
       remove_logs = True,
       **kw):
    return ZODB.DB(BSDDBStorage(path, blob_dir, pack, create, read_only,
                                detect_locks, remove_logs),
                   **kw)

class StorageIterator(object):

    def __init__(self, it):
        self.it = it

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.it.next()
        except StopIteration:
            raise ZODB.interfaces.StorageStopIteration
            
class Records(object):

    def __init__(self, storage, txn, tid, status, ext):
        self.storage = storage
        self._txn = txn
        self.tid = tid
        ext = cPickle.loads(ext)
        self.user = ext.pop('user_name', '')
        self.description = ext.pop('description', '')
        self.status = status
        self.extension = ext

    @apply
    def _extension():
        def set(self, ext):
            self.extension = ext
        return property((lambda self: self.extension), set)

    def __iter__(self):
        return StorageIterator(self._iter())
        
    def _iter(self):
        tid = self.tid
        ntid = n64(tid)
        with self.storage.cursor(self.storage.transaction_oids, self._txn
                                 ) as transaction_oids:
            kv = transaction_oids.get(tid, flags=db.DB_SET)
            while kv:
                ttid, oid = kv
                assert ttid == tid
                with self.storage.cursor(self.storage.data, self._txn) as data:
                    kr = data.get(oid, ntid, flags=db.DB_GET_BOTH_RANGE)
                    if kr is None:
                        kr = data.get(oid, flags=db.DB_SET)
                    doid, rec = kr
                    assert doid == oid
                    dntid = rec[:8]
                    assert dntid == ntid
                    yield Record(oid, tid, rec[8:])
                kv = transaction_oids.get(tid, flags=db.DB_NEXT_DUP)

class Record:
    def __init__(self, oid, tid, data):
        self.oid = oid
        self.tid = tid
        self.data = data

    version = ''
    data_txn = None

    def __repr__(self):
        return repr((u64(self.oid), str(ZODB.TimeStamp.TimeStamp(self.tid)),
                     self.data))


class RWLock:

    def __init__(self):
        self.readers = self.write_waiting = 0
        self.condition = threading.Condition()

    def read(self):
        return ReadLockContext(self)

    def write(self):
        return WriteLockContext(self)

    def acquire_write(self):
        self.condition.acquire()
        try:
            if not self.readers:
                self.readers = -1
                return
            self.write_waiting += 1
            self.condition.wait()
            while self.readers:
                self.condition.wait()
            self.write_waiting -= 1
            self.readers = -1
        finally:
            self.condition.release()

    def release_write(self):
        self.condition.acquire()
        try:
            assert self.readers == -1
            self.readers = 0
            if self.write_waiting:
                self.condition.notifyAll()
            else:
                self.condition.notify()
        finally:
            self.condition.release()

    def acquire_read(self):
        self.condition.acquire()
        try:
            while self.write_waiting or self.readers < 0:
                self.condition.wait()
            self.readers += 1
        finally:
            self.condition.release()

    def release_read(self):
        self.condition.acquire()
        try:
            assert self.readers > 0
            self.readers -= 1
            if self.readers == 0:
                if self.write_waiting:
                    self.condition.notifyAll()
                else:
                    self.condition.notify()
        finally:
            self.condition.release()

class WriteLockContext(object):

    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire_write()

    def __exit__(self, *args):
        self.lock.release_write()

class ReadLockContext(object):

    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire_read()

    def __exit__(self, *args):
        self.lock.release_read()
        
