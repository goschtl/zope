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
import cStringIO
import logging
import os
import struct
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

def DB(path, blob_dir=None, pack=3*86400,
       read_only=False, create=False,
       detect_deadlocks = True,
       remove_logs = True,
       **kw):
    return ZODB.DB(BSDDBStorage(path, blob_dir, pack, create, read_only,
                                detect_deadlocks, remove_logs),
                   **kw)

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
                 detect_deadlocks = True,
                 remove_logs = True,
                 checkpoint = 60,
                 autopack = 0,
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
        if detect_deadlocks:
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

        self._len_lock = threading.Lock()

        # transactions: {tid ->pickle((status,ext,oids))}
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
        self._len = int(self.misc.get('len', '0'))

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

        if checkpoint > 0:
            self.finish_checkpointing = interval_thread(
                self.env.txn_checkpoint, checkpoint)
        if autopack > 0:
            event = threading.Event()
            self.finish_packing = interval_thread(
                (lambda : self.pack(should_stop=event.is_set)),
                autopack, event)

    def txn(self, flags=0):
        return TransactionContext(self.env.txn_begin(flags=flags))

    def cursor(self, database, txn=None, flags=0):
        return CursorContext(database.cursor(txn, flags))

    def close(self):
        self.finish_packing()
        self.finish_checkpointing()
        self.data.close()
        self.transactions.close()
        self.env.close()
        if not self._read_only:
            self._lock_file.close()

    def finish_checkpointing(self):
        pass
    finish_packing = finish_checkpointing

    def getName(self):
        return self.__name__

    def getSize(self):
        return os.stat(self.datapath).st_size

    def _history_entry(self, record, txn):
        tid = n64(record[:8])
        transaction = cPickle.loads(self.transactions.get(tid, txn=txn))[1]
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

    def iterator(self, start=None, stop=None):
        return StorageIterator(self._iterator(start or z64,
                                              stop or '\f\f\f\f\f\f\f\f'))

    def _iterator(self, start, stop):
        while 1:
            with self.txn(db.DB_TXN_SNAPSHOT) as txn:
                with self.cursor(self.transactions, txn) as transactions:
                    n = 0
                    kv = transactions.get(start, flags=db.DB_SET_RANGE)
                    while 1:
                        if not kv:
                            return
                        tid, info = kv
                        if tid > stop:
                            return
                        yield Records(self, tid, *cPickle.loads(info))
                        kv = transactions.get(tid, flags=db.DB_NEXT)
                        n += 1
                        if n >= 1000:
                            # bail on this trans to avoid using too many
                            # resources.
                            start = p64(u64(tid)+1)
                            break

#     def record_iternext(next=None):
#         pass # XXX

    def lastTransaction(self):
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            with self.cursor(self.transactions, txn) as cursor:
                kv = cursor.get(db.DB_LAST)
                if kv is None:
                    return None
                return kv[0]

    def _inc_len(self, v):
        if not v:
            return

        with self.txn() as txn:
            l = long(self.misc.get('len', '0', txn, db.DB_RMW)) + v
            self.misc.put('len', str(l), txn)

        with self._len_lock:
            self._len += v

    def __len__(self):
        return self._len

    def load(self, oid, version=''):
        with self._current_lock.read():
            with self.txn(db.DB_TXN_SNAPSHOT) as txn:
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

    def pack(self, pack_time=None, referencesf=None, gc=False,
             should_stop=lambda : 0):
        assert not gc, "BSDDBStorage doesn't do garbage collection."
        if pack_time is None:
            pack_time = time.time()-self._pack
        pack_tid = timetime2tid(pack_time)
        while self._pack1(pack_tid) and not should_stop():
            pass
        if self.blob_dir:
            self._remove_empty_notlast_blob_directories(self.blob_dir)

    @retry_on_deadlock
    def _pack1(self, pack_tid):
        # Pack one transaction. Get the next transaction we haven't yet
        # packed and stop if it is > pack_tid.
        # This is done as a transaction.
        removed_blobs = []
        removed_oids = 0
        with self.txn(db.DB_TXN_SNAPSHOT) as txn:
            # Pick a tid just past the last one we packed:
            tid = p64(u64(self.misc.get('pack', z64, txn=txn))+1)
            if tid > pack_tid:
                return None

            with self.cursor(self.transactions, txn) as transactions:
                kv = transactions.get(tid, flags=db.DB_SET_RANGE)
                if kv is None:
                    return None
                tid = kv[0]
                if tid > pack_tid:
                    return None

                ntid = n64(tid)

                ext, oids = cPickle.loads(kv[1])[1:]
                new_oids = []
                for oid in oids:

                    # Find the first record for the oid whos tid is <=
                    # the pack time. (we use negative tids, so >=)
                    # This is the current record as of the pack time
                    with self.cursor(self.data, txn) as data:
                        kr = data.get(oid, ntid, flags=db.DB_GET_BOTH_RANGE)
                        if not kr:
                            kr = data.get(oid, flags=db.DB_SET)
                            if kr[1][:8] < ntid:
                                # the one record found is after
                                # the pack time
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
                            removed_oids += 1
                        else:
                            deleted_oid = False
                            new_oids.append(oid)

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

                if new_oids:
                    # Update the status flag and oids.
                    transactions.put(
                        tid, cPickle.dumps(('p', ext, new_oids)), db.DB_CURRENT)
                else:
                    # transaction is empty. Delete it
                    transactions.delete()

            self.misc.put('pack', tid, txn=txn)

        self._inc_len(-removed_oids)

        if removed_blobs:
            self._remove_blob_files_tagged_for_removal_during_pack(
                removed_blobs)

        return tid

    def _pack_remove_oid_tid(self, tid, oid, txn):
        ext, oids = cPickle.loads(
            self.transactions.get(tid, txn=txn, flags=db.DB_RMW))[1:]
        oids.remove(oid)
        self.transactions.put(tid, cPickle.dumps(('p', ext, oids)), txn)

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
        if committed_tid is None:
            self._new_obs += 1
        else:
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

        self._log(oid, n64(self._tid)+data)
        return result

    def restore(self, oid, serial, data, version, prev_txn, transaction):
        assert not version
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        self._log(oid, n64(serial)+(data or ''))

    def deleteObject(self, oid, oldserial, transaction):
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)
        committed_tid = self.data.get(oid, dlen=8, doff=0)
        if committed_tid is not None and n64(committed_tid) != oldserial:
            raise ZODB.POSException.ConflictError(
                oid=oid, serials=(n64(committed_tid), oldserial))

        self._log(oid, n64(self._tid))

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

        if tid is None:
            now = time.time()
            t = ZODB.TimeStamp.TimeStamp(
                *(time.gmtime(now)[:5] + (now % 60,)))
            self._ts = t = t.laterThan(self._ts)
            self._tid = tid = repr(t)
        else:
            self._ts = ZODB.TimeStamp.TimeStamp(tid)
            self._tid = tid

        self._log = ObjectLog()
        self._log(tid, status, ext)
        self._new_obs = 0

    def _tpc_cleanup(self):
        self._transaction = self._txn = None
        self._log.close()
        self._commit_lock.release()

    def tpc_abort(self, transaction):
        if transaction is not self._transaction:
            return
        if self._txn is not None:
            self._txn.abort()
        self._blob_tpc_abort()
        self._tpc_cleanup()

    def tpc_finish(self, transaction, func = lambda tid: None):
        if transaction is not self._transaction:
            return

        with self._current_lock.write():
            func(self._tid)
            self._txn.commit()
            self._blob_tpc_finish()
            self._tpc_cleanup()

        self._inc_len(self._new_obs)

    _transaction_id_suffix = 'x' * (db.DB_GID_SIZE - 8)
    def tpc_vote(self, transaction):
        log = iter(self._log)
        tid, status, ext = log.next()
        oids = []
        self._txn = txn = self.env.txn_begin()
        for oid, record in log:
            try:
                self.data.put(oid, record, txn=txn)
            except db.DBKeyExistError:
                # If the entire records are dups, we
                # don't want to write them again. That
                # would be silly.
                pass
            else:
                oids.append(oid)
        self.transactions.put(tid, cPickle.dumps((status, ext, oids)), txn=txn)
        txn.prepare(self._tid+self._transaction_id_suffix)

    ##############################################################
    # ZEO support

    def getTid(self, oid):
        """The last transaction to change an object

        Return the transaction id of the last transaction that committed a
        change to an object with the given object id.

        """
        with self._current_lock.read():
            with self.txn(db.DB_TXN_SNAPSHOT) as txn:
                rec = self.data.get(oid, doff=0, dlen=9)
                if not rec or len(rec) == 8:
                    raise ZODB.POSException.POSKeyError(oid)
                return n64(rec[:8])


    def tpc_transaction(self):
        return self._transaction

    #
    ##############################################################

Storage = BSDDBStorage # easier to type alias :)

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

    def __init__(self, storage, tid, status, ext, oids):
        self.storage = storage
        self.tid = tid
        self.user = ext.pop('user_name', '')
        self.description = ext.pop('description', '')
        self.status = status
        self.extension = ext
        self.oids = oids

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
        for oid in self.oids:
            with self.storage.txn(db.DB_TXN_SNAPSHOT) as txn:
                with self.storage.cursor(self.storage.data, txn) as data:
                    kr = data.get(oid, ntid, flags=db.DB_GET_BOTH_RANGE)
                    if kr is None:
                        kr = data.get(oid, flags=db.DB_SET)
                    doid, rec = kr
                    assert doid == oid
                    dntid = rec[:8]
                    assert dntid == ntid, (tid, ntid, dntid)
                    yield Record(oid, tid, rec[8:])

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

def interval_thread(func, interval, event=None):

    if event is None:
        event = threading.Event()
    name = __name__+'.%s' % func.__name__
    logger = logging.getLogger(name)

    def run(func):
        status = None
        while not event.is_set():
            try:
                func()
            except Exception:
                if status != 'failed':
                    logger.critical("failed", exc_info=sys.exc_info)
                    status = 'failed'
            else:
                if status == 'failed':
                    logger.info("succeeded")
                    status = None
            event.wait(interval)

    thread = threading.Thread(target=run, args=(func, ), name=name)
    thread.setDaemon(True)
    thread.start()

    def join(*args):
        event.set()
        thread.join(*args)

    return join


class ObjectLog:
    # Log of pickleable object data.
    # In memory if possible

    max_mem = 1<<20 # Most transactions are a few K or less
    in_memory = True

    def __init__(self):
        self._file = cStringIO.StringIO()
        self.close = self._file.close
        self._size = 0

    def __call__(self, *data):
        data = cPickle.dumps(data, 1)
        ldata = len(data)
        size = self._size + len(data) + 4
        if self.in_memory and size > self.max_mem:
            newfile = tempfile.TemporaryFile()
            self._file.seek(0)
            newfile.write(self._file.read())
            self._file = newfile
            self.close = self._file.close
            self.in_memory = False
        self._file.write(struct.pack(">I", ldata))
        self._file.write(data)

    def __iter__(self):
        file = self._file
        file.seek(0)
        while 1:
            l = file.read(4)
            if not l:
                break
            l = struct.unpack(">I", l)[0]
            yield cPickle.loads(file.read(l))
