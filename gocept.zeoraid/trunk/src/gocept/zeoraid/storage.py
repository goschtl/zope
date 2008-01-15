# vim:fileencoding=utf-8
# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""ZEORaid storage implementation."""

import threading
import time
import logging

import zope.interface

import ZEO.ClientStorage
import ZEO.interfaces
import ZODB.POSException
import ZODB.interfaces
import ZODB.utils
import persistent.TimeStamp
import transaction

import gocept.zeoraid.interfaces
import gocept.zeoraid.compatibility

logger = logging.getLogger('gocept.zeoraid')

def ensure_open_storage(method):
    def check_open(self, *args, **kw):
        if self.closed:
            raise gocept.zeoraid.interfaces.RAIDClosedError("Storage has been closed.")
        return method(self, *args, **kw)
    return check_open

no_transaction_marker = object()

def choose_transaction(version, transaction):
    # In ZODB < 3.9 both version and transaction are required positional
    # arguments.
    # In ZODB >= 3.9 the version argument is gone and transaction takes it
    # place in the positional order.
    if transaction is no_transaction_marker:
        # This looks like a ZODB 3.9 client, so we clean up the order.
        transaction = version
        version = ''
    # XXX For compatibility only version == '  is relevant. The ZODB is still 
    # being changed for removing versions though and the tests might pass in 0
    # for now.
    assert version == '' or version == 0
    return transaction

def store_38_compatible(method):
    def prepare_store(self, oid, oldserial, data, version='',
                      transaction=no_transaction_marker):
        transaction = choose_transaction(version, transaction)
        return method(self, oid, oldserial, data, transaction)
    return prepare_store


def storeBlob_38_compatible(method):
    def prepare_store(self, oid, oldserial, data, blob, version='',
                      transaction=no_transaction_marker):
        transaction = choose_transaction(version, transaction)
        return method(self, oid, oldserial, data, blob, transaction)
    return prepare_store


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

    # This flag signals whether any `store` operation should be logged. This
    # is necessary to support the two-phase recovery process. It is set to
    # `true` when a recovery starts and set back to `false` when it is
    # finished.
    _log_stores = False

    # The last transaction that we know of. This is used to keep a global
    # knowledge of the current assumed state and verify storages that might
    # have fallen out of sync. It is also used as a point of reference
    # for generating new TIDs.
    _last_tid = None

    def __init__(self, name, openers, read_only=False):
        self.__name__ = name
        self.read_only = read_only
        self.storages = {}

        # Allocate locks
        # XXX document locks
        l = threading.RLock()
        self._lock_acquire = l.acquire
        self._lock_release = l.release
        l = threading.Lock()
        self._commit_lock_acquire = l.acquire
        self._commit_lock_release = l.release

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
            self._apply_all_storages('close', expect_connected=False)
        finally:
            self.closed = True
            del self.storages_optimal[:]

    def getName(self):
        """The name of the storage."""
        return self.__name__

    def getSize(self):
        """An approximate size of the database, in bytes."""
        return self._apply_single_storage('getSize')

    def history(self, oid, version='', size=1):
        """Return a sequence of history information dictionaries."""
        assert version is ''
        return self._apply_single_storage(
            'history', (oid, size),
            allowed_exceptions=ZODB.POSException.POSKeyError)

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
        return self._apply_single_storage(
            'load', (oid,), allowed_exceptions=ZODB.POSException.POSKeyError)

    def loadBefore(self, oid, tid):
        """Load the object data written before a transaction id."""
        return self._apply_single_storage(
            'loadBefore', (oid, tid),
            allowed_exceptions=ZODB.POSException.POSKeyError)

    def loadSerial(self, oid, serial):
        """Load the object record for the give transaction id."""
        return self._apply_single_storage('loadSerial', (oid, serial))

    # XXX
    def new_oid(self):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_all_storages('new_oid')
        finally:
            self._lock_release()

    # XXX
    def pack(self, t, referencesf):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._apply_all_storages('pack', (t, referencesf))

    # XXX
    def registerDB(self, db, limit=None):
        # XXX Is it safe to register a DB with multiple storages or do we need some kind
        # of wrapper here?
        self._apply_all_storages('registerDB', (db,))

    # XXX
    def sortKey(self):
        return id(self)

    # XXX
    @store_38_compatible
    def store(self, oid, oldserial, data, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        self._lock_acquire()
        try:
            # XXX ClientStorage doesn't adhere to the interface correctly (yet).
            self._apply_all_storages('store',
                                     (oid, oldserial, data, '', transaction))
            if self._log_stores:
                oids = self._unrecovered_transactions.setdefault(self._tid, [])
                oids.append(oid)
            return self._tid
        finally:
            self._lock_release()

    # XXX
    def tpc_abort(self, transaction):
        self._lock_acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                # XXX Edge cases for the log_store abort ...
                if self._log_stores:
                    # We may have logged some stores within that transaction
                    # which we have to remove again because we aborted it.
                    if self._tid in self._unrecovered_transactions:
                        del self._unrecovered_transactions[self._tid]
                self._apply_all_storages('tpc_abort', (transaction,))
                self._transaction = None
            finally:
                self._commit_lock_release()
        finally:
            self._lock_release()

    # XXX
    def tpc_begin(self, transaction, tid=None, status=' '):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()

        self._lock_acquire()
        try:
            if self._transaction is transaction:
                return
            self._lock_release()
            self._commit_lock_acquire()
            self._lock_acquire()

            # I don't understand the lock that protects _transaction.  The commit
            # lock and status will be deduced by the underlying storages.

            self._transaction = transaction

            # Remove storages that aren't on the same last tid anymore (this happens 
            # if a storage disconnects
            for name in self.storages_optimal:
                storage = self.storages[name]
                try:
                    last_tid = storage.lastTransaction()
                except ZEO.ClientStorage.ClientDisconnected:
                    self._degrade_storage(name, fail=False)
                    continue
                if last_tid != self._last_tid:
                    self._degrade_storage(name)

            if tid is None:
                # No TID was given, so we create a new one.
                tid = self._new_tid(self._last_tid)
            self._tid = tid

            self._apply_all_storages('tpc_begin',
                                     (transaction, self._tid, status))
        finally:
            self._lock_release()

    # XXX
    def tpc_finish(self, transaction, callback=None):
        self._lock_acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                if callback is not None:
                    callback(self._tid)
                self._apply_all_storages('tpc_finish', (transaction,))
                self._last_tid = self._tid
                return self._tid
            finally:
                self._transaction = None
                self._commit_lock_release()
        finally:
            self._lock_release()

    # XXX
    def tpc_vote(self, transaction):
        self._lock_acquire()
        try:
            if transaction is not self._transaction:
                return
            self._apply_all_storages('tpc_vote', (transaction,))
        finally:
            self._lock_release()

    def cleanup(self):
        # XXX This is not actually documented, it's not implemented in all
        # storages, it's not even clear when it should be called. Not
        # correctly calling storages' cleanup might leave turds.
        pass

    def supportsVersions(self):
        return False

    def modifiedInVersion(self, oid):
        return ''

    # IBlobStorage

    @storeBlob_38_compatible
    def storeBlob(self, oid, oldserial, data, blob, transaction):
        """Stores data that has a BLOB attached."""
        # XXX

    def loadBlob(self, oid, serial):
        """Return the filename of the Blob data for this OID and serial."""
        # XXX

    def temporaryDirectory(self):
        """Return a directory that should be used for uncommitted blob data.
        """
        # XXX

    # IStorageUndoable

    # XXX
    def supportsUndo(self):
        return True

    # XXX
    def undo(self, transaction_id, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_all_storages('undo',
                                            (transaction_id, transaction))
        finally:
            self._lock_release()

    # XXX
    def undoLog(self, first=0, last=-20, filter=None):
        return self._apply_single_storage('undoLog', (first, last, filter))

    # XXX
    def undoInfo(self, first=0, last=-20, specification=None):
        return self._apply_single_storage('undoInfo',
                                          (first, last, specification))

    # IStorageCurrentRecordIteration

    # XXX
    def record_iternext(self, next=None):
        """Iterate over the records in a storage."""

    # IServeable

    # XXX
    def lastInvalidations(self, size):
        """Get recent transaction invalidations."""

    # XXX
    def tpc_transaction(self):
        """The current transaction being committed."""
        return self._transaction

    # XXX
    def getTid(self, oid):
        return self._apply_single_storage('getTid', (oid,))

    # XXX
    def getExtensionMethods(self):
        methods = self._apply_single_storage('getExtensionMethods')
        if methods is None:
            # Allow management while status is 'failed'
            methods = {}
        methods['raid_recover'] = None
        methods['raid_status'] = None
        methods['raid_disable'] = None
        methods['raid_details'] = None
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
        t.start()
        return 'recovering %r' % (name,)

    # internal

    def _open_storage(self, name):
        assert name not in self.storages, "Storage %s already opened" % name
        storage = self.openers[name].open()
        storage = gocept.zeoraid.interfaces.IRAIDCompatibleStorage(storage)
        self.storages[name] = storage

    def _degrade_storage(self, name, fail=True):
        if name in self.storages_optimal:
            self.storages_optimal.remove(name)
        self.storages_degraded.append(name)
        storage = self.storages[name]
        t = threading.Thread(target=storage.close)
        t.start()
        del self.storages[name]
        if not self.storages_optimal and fail:
            raise gocept.zeoraid.interfaces.RAIDError("No storages remain.")

    @ensure_open_storage
    def _apply_single_storage(self, method_name, args=(), kw={},
                              allowed_exceptions=()):
        # Try to find a storage that we can talk to. Stop after we found a
        # reliable result.
        failed = 0
        for name in self.storages_optimal[:]:
            # XXX storage might be degraded by now, need to check.
            storage = self.storages[name]
            method = getattr(storage, method_name)
            try:
                result = method(*args, **kw)
            except allowed_exceptions:
                # These exceptions are valid answers from the storage, such as
                # POSKeyError. They don't indicate storage failure.
                raise
            except Exception:
                # XXX Logging
                if failed:
                    raise
                failed += 1
            else:
                if storage.is_connected():
                    # We have a result that is reliable.
                    return result
            # There was no result or it is not reliable, the storage needs to
            # be degraded and we try another storage.
            self._degrade_storage(name)

        # We could not determine a result from any storage.
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")

    @ensure_open_storage
    def _apply_all_storages(self, method_name, args=(), kw={},
                            expect_connected=True):
        results = []
        storages = self.storages_optimal[:]
        if not storages:
            raise gocept.zeoraid.interfaces.RAIDError(
                "RAID storage is failed.")

        for name in self.storages_optimal:
            storage = self.storages[name]
            try:
                method = getattr(storage, method_name)
                results.append(method(*args, **kw))
            except ZEO.ClientStorage.ClientDisconnected:
                self._degrade_storage(name)
            else:
                if expect_connected and not storage.is_connected():
                    self._degrade_storage(name)

        res = results[:]
        for test1 in res:
            for test2 in res:
                assert test1 == test2, "Results not consistent. Asynchronous storage?"
        return results[0]

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
        old_ts = persistent.TimeStamp.TimeStamp(old_tid)
        now = time.time()
        new_ts = persistent.TimeStamp.TimeStamp(
            *(time.gmtime(now)[:5] + (now % 60,)))
        new_ts = new_ts.laterThan(old_ts)
        return repr(new_ts)
