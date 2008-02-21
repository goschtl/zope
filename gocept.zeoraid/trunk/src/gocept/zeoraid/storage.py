##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and contributors.
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
"""ZEORaid storage implementation."""

import threading
import time
import logging
import tempfile
import os
import os.path

import zope.interface

import ZEO.ClientStorage
import ZEO.interfaces
import ZODB.POSException
import ZODB.interfaces
import ZODB.utils
import persistent.TimeStamp
import transaction
import transaction.interfaces
import ZODB.blob

import gocept.zeoraid.interfaces

logger = logging.getLogger('gocept.zeoraid')


def ensure_open_storage(method):
    def check_open(self, *args, **kw):
        if self.closed:
            raise gocept.zeoraid.interfaces.RAIDClosedError("Storage has been closed.")
        return method(self, *args, **kw)
    return check_open


def ensure_writable(method):
    def check_writable(self, *args, **kw):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        return method(self, *args, **kw)
    return check_writable


class RAIDStorage(object):
    """The RAID storage is a drop-in replacement for the client storages that
    are configured.

    It has few but important tasks: multiplex all communication to the
    storages, coordinate the transactions between the storages and alert the
    RAID controller if a storage fails.

    """

    zope.interface.implements(ZODB.interfaces.IStorage,
                              ZODB.interfaces.IBlobStorage,
                              ZODB.interfaces.IStorageUndoable,
                              ZODB.interfaces.IStorageCurrentRecordIteration,
                              ZEO.interfaces.IServeable,
                              )

    closed = False
    _transaction = None

    # We store the registered database to be able to re-register storages when
    # we bring them back into the pool of optimal storages.
    _db = None

    # The last transaction that we know of. This is used to keep a global
    # knowledge of the current assumed state and verify storages that might
    # have fallen out of sync. It is also used as a point of reference
    # for generating new TIDs.
    _last_tid = None

    def __init__(self, name, openers, read_only=False, blob_dir=None):
        self.__name__ = name
        self.read_only = read_only
        self.storages = {}
        self._threads = set()

        if blob_dir is not None:
            self.blob_fshelper = ZODB.blob.FilesystemHelper(blob_dir)
            self.blob_fshelper.create()
            self.blob_fshelper.checkSecure()

        # Allocate locks
        # The write lock must be acquired when:
        # a) performing write operations on the backends
        # b) writing _transaction
        self._write_lock = threading.RLock()
        # The commit lock must be acquired when setting _transaction, and
        # released when unsetting _transaction.
        self._commit_lock = threading.Lock()

        # Remember the openers so closed storages can be re-opened as needed.
        self.openers = dict((opener.name, opener) for opener in openers)

        for name in self.openers:
            self._open_storage(name)

        # Evaluate the consistency of the opened storages. We compare the last
        # known TIDs of all storages. All storages whose TID equals the newest
        # of these TIDs are considered optimal.
        tids = {}
        for name, storage in self.storages.items():
            try:
                tid = storage.lastTransaction()
            except StorageDegraded:
                continue
            tids.setdefault(tid, [])
            tids[tid].append(name)

        if not tids:
            # No storage is working.
            raise gocept.zeoraid.interfaces.RAIDError(
                "Can't start without at least one working storage.")

        # Set up list of optimal storages
        self._last_tid = max(tids)
        self.storages_optimal = tids.pop(self._last_tid)

        # Set up list of degraded storages
        self.storages_degraded = []
        for degraded_storages in tids.values():
            self.storages_degraded.extend(degraded_storages)

        # XXX Degrade storages that don't have the right max OID.

        # No storages are recovering initially
        self.storages_recovering = []

    # IStorage

    def close(self):
        """Close the storage."""
        if self.closed:
            # Storage may be closed more than once, e.g. by tear-down methods
            # of tests.
            return
        try:
            try:
                self._apply_all_storages('close', expect_connected=False)
            except gocept.zeoraid.interfaces.RAIDError:
                pass
        finally:
            self.closed = True
            del self.storages_optimal[:]

        for thread in self._threads:
            # We give all the threads a chance to get done within one second.
            # This is mostly a convenience for the tests to not annoy.
            thread.join(1)

    def getName(self):
        """The name of the storage."""
        return self.__name__

    def getSize(self):
        """An approximate size of the database, in bytes."""
        return self._apply_single_storage('getSize')

    def history(self, oid, version='', size=1):
        """Return a sequence of history information dictionaries."""
        assert version is ''
        return self._apply_single_storage('history', (oid, size))

    def isReadOnly(self):
        """Test whether a storage allows committing new transactions."""
        return self.read_only

    def lastTransaction(self):
        """Return the id of the last committed transaction."""
        if self.raid_status() == 'failed':
            raise gocept.zeoraid.interfaces.RAIDError('RAID is failed.')
        return self._last_tid

    def __len__(self):
        """The approximate number of objects in the storage."""
        return self._apply_single_storage('__len__')

    def load(self, oid, version=''):
        """Load data for an object id and version."""
        assert version is ''
        return self._apply_single_storage('load', (oid,))

    def loadBefore(self, oid, tid):
        """Load the object data written before a transaction id."""
        return self._apply_single_storage('loadBefore', (oid, tid))

    def loadSerial(self, oid, serial):
        """Load the object record for the give transaction id."""
        return self._apply_single_storage('loadSerial', (oid, serial))

    @ensure_writable
    def new_oid(self):
        """Allocate a new object id."""
        self._write_lock.acquire()
        try:
            oids = []
            for storage in self.storages_optimal[:]:
                reliable, oid = self.__apply_storage(storage, 'new_oid')
                if reliable:
                    oids.append((oid, storage))
            if not oids:
                raise gocept.zeoraid.interfaces.RAIDError(
                    "RAID storage is failed.")

            min_oid = sorted(oids)[0][0]
            for oid, storage in oids:
                if oid > min_oid:
                    self._degrade_storage(storage)
            return min_oid
        finally:
            self._write_lock.release()

    @ensure_writable
    def pack(self, t, referencesf):
        """Pack the storage."""
        # Packing is an interesting problem when talking to multiple storages,
        # especially when doing it in parallel:
        # As packing might take a long time, you can end up with a couple of
        # storages that are packed and others that are still packing.
        # As soon as one storage is packed, you have to prefer reading from
        # this storage.
        #
        # Here, we rely on the following behaviour:
        # a) always read from the first optimal storage
        # b) pack beginning with the first optimal storage, working our way
        #    through the list.
        # This is a simplified implementation of a way to prioritize the list
        # of optimal storages.
        self._apply_all_storages('pack', (t, referencesf))

    def registerDB(self, db, limit=None):
        """Register an IStorageDB."""
        # We can safely register all storages here as it will only cause
        # invalidations to be sent out multiple times. Transaction
        # coordination by the StorageServer and set semantics in ZODB's
        # Connection class make this correct and cheap.
        self._db = db
        self._apply_all_storages('registerDB', (db,))

    def sortKey(self):
        """Sort key used to order distributed transactions."""
        return id(self)

    @ensure_writable
    def store(self, oid, oldserial, data, version, transaction):
        """Store data for the object id, oid."""
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)
        self._write_lock.acquire()
        try:
            self._apply_all_storages('store',
                                     (oid, oldserial, data, version, transaction))
            return self._tid
        finally:
            self._write_lock.release()

    def tpc_abort(self, transaction):
        """Abort the two-phase commit."""
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                self._apply_all_storages('tpc_abort', (transaction,))
                self._transaction = None
            finally:
                self._commit_lock.release()
        finally:
            self._write_lock.release()

    @ensure_writable
    def tpc_begin(self, transaction, tid=None, status=' '):
        """Begin the two-phase commit process."""
        self._write_lock.acquire()
        try:
            if self._transaction is transaction:
                # It is valid that tpc_begin is called multiple times with
                # the same transaction and is silently ignored.
                return

            # Release and re-acquire to avoid dead-locks. commit_lock is a
            # long-term lock whereas write_lock is a short-term lock. Acquire
            # the long-term lock first.
            self._write_lock.release()
            self._commit_lock.acquire()
            self._write_lock.acquire()

            self._transaction = transaction

            if tid is None:
                # No TID was given, so we create a new one.
                tid = self._new_tid(self._last_tid)
            self._tid = tid

            self._apply_all_storages('tpc_begin',
                                     (transaction, self._tid, status))
        finally:
            self._write_lock.release()

    def tpc_finish(self, transaction, callback=None):
        """Finish the transaction, making any transaction changes permanent.
        """
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                self._apply_all_storages('tpc_finish', (transaction,))
                if callback is not None:
                    # This callback is relevant for processing invalidations
                    # at transaction boundaries.
                    # XXX It is somewhat unclear whether this should be done
                    # before or after calling tpc_finish. BaseStorage and
                    # ClientStorage contradict each other and the documentation
                    # is non-existent. We trust ClientStorage here.
                    callback(self._tid)
                self._last_tid = self._tid
                return self._tid
            finally:
                self._transaction = None
                self._commit_lock.release()
        finally:
            self._write_lock.release()

    def tpc_vote(self, transaction):
        """Provide a storage with an opportunity to veto a transaction."""
        self._write_lock.acquire()
        try:
            if transaction is not self._transaction:
                return
            self._apply_all_storages('tpc_vote', (transaction,))
        finally:
            self._write_lock.release()

    def supportsVersions(self):
        return False

    def modifiedInVersion(self, oid):
        return ''

    # IBlobStorage

    @ensure_writable
    def storeBlob(self, oid, oldserial, data, blob, version, transaction):
        """Stores data that has a BLOB attached."""
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        def get_blob_data():
            # Client storages expect to be the only ones operating on the blob
            # file. We need to create individual appearances of the original
            # file so that they can move the file to their cache location.
            yield (oid, oldserial, data, blob, '', transaction)
            base_dir = tempfile.mkdtemp(dir=os.path.dirname(blob))
            copies = 0
            while True:
                # We need to create a new directory to make sure that
                # atomicity of file creation is preserved.
                copies += 1
                new_blob = os.path.join(base_dir, '%i.blob' % copies)
                os.link(blob, new_blob)
                yield (oid, oldserial, data, new_blob, version, transaction)

        self._write_lock.acquire()
        try:
            self._apply_all_storages('storeBlob', get_blob_data)
            return self._tid
        finally:
            self._write_lock.release()

    def loadBlob(self, oid, serial):
        """Return the filename of the Blob data for this OID and serial."""
        return self._apply_single_storage('loadBlob', (oid, serial))

    def temporaryDirectory(self):
        """Return a directory that should be used for uncommitted blob data.
        """
        return self.blob_fshelper.temp_dir

    # IStorageUndoable

    def supportsUndo(self):
        """Return True, indicating that the storage supports undo.
        """
        return True

    @ensure_writable
    def undo(self, transaction_id, transaction):
        """Undo a transaction identified by id."""
        self._write_lock.acquire()
        try:
            return self._apply_all_storages('undo',
                                            (transaction_id, transaction))
        finally:
            self._write_lock.release()

    def undoLog(self, first=0, last=-20, filter=None):
        """Return a sequence of descriptions for undoable transactions."""
        return self._apply_single_storage('undoLog', (first, last, filter))

    def undoInfo(self, first=0, last=-20, specification=None):
        """Return a sequence of descriptions for undoable transactions."""
        return self._apply_single_storage('undoInfo',
                                          (first, last, specification))

    # IStorageCurrentRecordIteration

    def record_iternext(self, next=None):
        """Iterate over the records in a storage."""
        return self._apply_single_storage('record_iternext', (next,))

    # IServeable

    # Note: We opt to not implement lastInvalidations until ClientStorage does.
    # def lastInvalidations(self, size):
    #    """Get recent transaction invalidations."""
    #    return self._apply_single_storage('lastInvalidations', (size,))

    def tpc_transaction(self):
        """The current transaction being committed."""
        return self._transaction

    def getTid(self, oid):
        """The last transaction to change an object."""
        return self._apply_single_storage('getTid', (oid,))

    def getExtensionMethods(self):
        # This method isn't officially part of the interface but it is supported.
        methods = dict.fromkeys(
            ['raid_recover', 'raid_status', 'raid_disable', 'raid_details'])
        return methods

    # IRAIDStorage

    # XXX
    @ensure_open_storage
    def raid_status(self):
        if self.storages_recovering:
            return 'recovering'
        if not self.storages_degraded:
            return 'optimal'
        if not self.storages_optimal:
            return 'failed'
        return 'degraded'

    # XXX
    @ensure_open_storage
    def raid_details(self):
        return [self.storages_optimal, self.storages_recovering, self.storages_degraded]

    # XXX
    @ensure_open_storage
    def raid_disable(self, name):
        self._degrade_storage(name, fail=False)
        return 'disabled %r' % (name,)

    # XXX
    @ensure_open_storage
    def raid_recover(self, name):
        # XXX: Need to sync `max oid` after recovery
        if name not in self.storages_degraded:
            return
        self.storages_degraded.remove(name)
        self.storages_recovering.append(name)
        t = threading.Thread(target=self._recover_impl, args=(name,))
        self._threads.add(t)
        t.setDaemon(True)
        t.start()
        return 'recovering %r' % (name,)

    # internal

    def _open_storage(self, name):
        assert name not in self.storages, "Storage %s already opened" % name
        storage = self.openers[name].open()
        assert hasattr(storage, 'supportsUndo') and storage.supportsUndo()
        self.storages[name] = storage

    def _degrade_storage(self, name, fail=True):
        if name in self.storages_optimal:
            self.storages_optimal.remove(name)
        self.storages_degraded.append(name)
        storage = self.storages[name]
        t = threading.Thread(target=storage.close)
        self._threads.add(t)
        t.setDaemon(True)
        t.start()
        del self.storages[name]
        if not self.storages_optimal and fail:
            raise gocept.zeoraid.interfaces.RAIDError("No storages remain.")

    def __apply_storage(self, name, method_name, args=(), kw={},
                        expect_connected=True):
        # XXX storage might be degraded by now, need to check.
        storage = self.storages[name]
        method = getattr(storage, method_name)
        reliable = True
        result = None
        try:
            result = method(*args, **kw)
        except ZODB.POSException.StorageError:
            # Handle StorageErrors first, otherwise they would be swallowed
            # when POSErrors are.
            reliable = False
            raise
        except (ZODB.POSException.POSError,
                transaction.interfaces.TransactionError), e:
            # These exceptions are valid answers from the storage. They don't
            # indicate storage failure.
            raise
        except Exception:
            reliable = False
        if expect_connected and not storage.is_connected():
            reliable = False

        if not reliable:
            self._degrade_storage(name)
        return (reliable, result)

    @ensure_open_storage
    def _apply_single_storage(self, method_name, args=(), kw={}):
        """Calls the given method on the first optimal storage."""
        # Try to find a storage that we can talk to. Stop after we found a
        # reliable result.
        for name in self.storages_optimal[:]:
            reliable, result = self.__apply_storage(
                name, method_name, args, kw)
            if reliable:
                return result

        # We could not determine a result from any storage.
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")

    @ensure_open_storage
    def _apply_all_storages(self, method_name, args=(), kw={},
                            expect_connected=True):
        """Calls the given method on all optimal backend storages in order.

        `args` can be given as an n-tupel with the positional arguments that
        should be passed to each storage.

        Alternatively `args` can be a callable that returns an iterable. The
        N-th item of the iterable is expected to be a tuple, passed to the
        N-th storage.

        """
        results = []
        exceptions = []

        if callable(args):
            argument_iterable = args()
        else:
            # Provide a fallback if `args` is given as a simple tuple.
            static_arguments = args
            def dummy_generator():
                while True:
                    yield static_arguments
            argument_iterable = dummy_generator()

        for name in self.storages_optimal[:]:
            try:
                args = argument_iterable.next()
                reliable, result = self.__apply_storage(
                    name, method_name, args, kw, expect_connected)
            except Exception, e:
                exceptions.append(e)
                raise
            else:
                if reliable:
                    results.append(result)

        # Analyse result consistency.
        consistent = True
        if exceptions and results:
            consistent = False
        elif exceptions:
            # Since we can only get one kind of exceptions at the moment, they
            # must be consistent anyway.
            pass
        elif results:
            ref = results[0]
            for test in results:
                if test != ref:
                    consistent = False
                    break
        if not consistent:
            self.close()
            raise gocept.zeoraid.interfaces.RAIDError(
                "RAID is inconsistent and was closed.")

        # Select result.
        if exceptions:
            raise exceptions[0]
        if results:
            return results[0]

        # We could not determine a result from any storage because all of them
        # failed.
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")

    def _recover_impl(self, name):
        try:
            # First pass: Transfer all oids without hindering running transactions
            begin = time.time()
            self._recover_first(name)
            end = time.time()

            # Second pass: Start the TPC on a reference storage to block other
            # transactions so we can catch up. The second pass should be
            # significantly faster than the first.
            begin = time.time()
            self._recover_second(name)
            end = time.time()
        except Exception:
            # *something* went wrong. Put the storage back to degraded.
            logger.exception('Failure recovering %r: ' % (name,))
            try:
                self._degrade_storage(name)
            except Exception:
                logger.exception(
                    'Failure degrading %r after failed recovery: ' % (name,))
                raise
            raise

    def _recover_second(self, name):
        storage = self.storages[name]
        reference_storage = self.storages[self.storages_optimal[0]]
        # Start a transation on the reference storage to acquire the
        # commit log # and prevent other people from committing in the second phase.
        # XXX This needs to be optimized in a way that the second phase
        # gets re-run as long as possible, only holding the commit lock if 
        # no transactions remain that need to be replayed and putting the 
        # recovered storage back into the array of optimal storages.
        while 1:
            tm = transaction.TransactionManager()
            t = tm.get()
            last_transaction = storage.lastTransaction()
            reference_storage.tpc_begin(t)
            unrecovered_transactions = self._unrecovered_transactions
            if unrecovered_transactions:
                # We acquired the commit lock and there are transactions that
                # have been committed and were not yet transferred to the 
                # recovering storage. We have to try to replay those and then
                # check again. We can remove the commit lock for now.
                self._unrecovered_transactions = {}
                reference_storage.tpc_abort(t)

                # RRR: Refactor into its own method?
                tm2 = transaction.TransactionManager()
                t2 = tm2.get()

                # Get the unrecovered transactions in the order they were
                # recorded.
                tids = sorted(unrecovered_transactions.keys())
                for tid in tids:
                    oids = unrecovered_transactions[tid]
                    # We create one transaction for all oids that belong to one
                    # transaction.
                    storage.tpc_begin(t2, tid=tid)
                    for oid in oids:
                        data, tid_ = reference_storage.load(oid, '')
                        if tid_ > tid:
                            # If the current tid of the object is newer
                            # than the one we logged, we can ignore it, because
                            # there will be another entry for this oid in a 
                            # later transaction.
                            continue
                        try:
                            oldserial = storage.getTid(oid)
                        except ZODB.POSException.POSKeyError:
                            # This means that the object is new and didn't have an
                            # old transaction yet. 
                            # XXX Might this also happen with non-undoable storages?
                            oldserial = ZODB.utils.z64
                        storage.store(oid, oldserial, data, '', t2)
                    storage.tpc_vote(t2)
                    storage.tpc_finish(t2)
                # /RRR
            else:
                # We acquired the commit lock and no committed transactions
                # are waiting in the log. This means the recovering storage
                # has caught up by now and we can put it into optimal state
                # again.
                self.storages_recovering.remove(name)
                if self._db:
                    # We are registered with a database already. We need to
                    # re-register the recovered storage to make invalidations
                    # pass through.
                    self.storages[name].registerDB(self._db)
                self.storages_optimal.append(name)
                # We can also stop logging stores now.
                self._log_stores = False
                reference_storage.tpc_abort(t)
                break

    def _recover_first(self, name):
        """The inner loop of the recovery code. Does the actual work."""
        # Re-open storage
        storage = self.openers[name].open()
        self.storages[name] = storage
        # XXX Bring the storage to the current stage. This only copies the
        # current data, so RAID currently does support neither undo nor versions.
        next_oid = None
        tm = transaction.TransactionManager()
        t = tm.get()
        # XXX we assume that the last written transaction actually is consistent. We need
        # a consistency check.
        last_transaction = storage.lastTransaction()
        # This flag starts logging all succcessfull stores and updates those oids
        # in the second pass again.
        max_transaction = self.storages[self.storages_optimal[0]].lastTransaction()
        self._unrecovered_transactions = {}
        self._log_stores = True
        # The init flag allows us to phrase the break condition of the 
        # following loop a little bit more elegantly.
        init = True
        while 1:
            if next_oid is None and not init:
                break

            init = False
            oid, tid, data, next_oid = self._apply_single_storage(
                'record_iternext', (next_oid,))

            if tid > max_transaction:
                continue

            if tid <= last_transaction:
                try:
                    old_data = storage.loadSerial(oid, tid)
                except ZODB.POSException.POSKeyError:
                    pass
                else:
                    if old_data == data:
                        continue

            # There is a newer version of the object available or the existing
            # version was incorrect. Overwrite it with the right data.
            try:
                oldserial = storage.getTid(oid)
            except ZODB.POSException.POSKeyError:
                oldserial = ZODB.utils.z64


            assert oldserial <= tid, "last_transaction and oldserial are not in-sync"

            storage.tpc_begin(t, tid=tid)
            storage.store(oid, oldserial, data, '', t)
            storage.tpc_vote(t)
            storage.tpc_finish(t)

    def _new_tid(self, old_tid):
        """Generates a new TID."""
        if old_tid is None:
            old_tid = ZODB.utils.z64
        old_ts = persistent.TimeStamp.TimeStamp(old_tid)
        now = time.time()
        new_ts = persistent.TimeStamp.TimeStamp(
            *(time.gmtime(now)[:5] + (now % 60,)))
        new_ts = new_ts.laterThan(old_ts)
        return repr(new_ts)
