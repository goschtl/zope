import threading
import time

import zope.interface

import ZODB.interfaces
import ZEO.interfaces
import ZEO.ClientStorage
import ZODB.POSException
import ZODB.utils
import persistent.TimeStamp
import transaction


# XXX
def get_serial(storage, oid):
    if hasattr(storage, 'lastTid'):
        # This is something like a FileStorage
        get_serial = storage.lastTid
    else:
        get_serial = storage.getTid
    return get_serial(oid)


# XXX
def get_last_transaction(storage):
    if hasattr(storage, '_zeoraid_lastTransaction'):
        last_transaction = storage._zeoraid_lastTransaction()
    else:
        last_transaction = storage.lastTransaction()
    return last_transaction


class RAIDError(Exception):
    pass


class RAIDClosedError(RAIDError, ZEO.ClientStorage.ClientStorageError):
    pass


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

    def __init__(self, name, storages, read_only=False):
        self.__name__ = name
        self.read_only = read_only
        self.storages = {}
        self._log_stores = False

        # Allocate locks
        l = threading.RLock()
        self._lock_acquire = l.acquire
        self._lock_release = l.release
        l = threading.Lock()
        self._commit_lock_acquire = l.acquire
        self._commit_lock_release = l.release

        # Remember the openers to for recovering a storage later
        self.openers = {}
        # Open the storages
        for opener in storages:
            self.storages[opener.name] = opener.open()
            self.openers[opener.name] = opener

        self.storages_optimal = []
        self.storages_degraded = []
        self.storages_recovering = []

        tids = {}
        for name, storage in self.storages.items():
            try:
                tid = get_last_transaction(storage)
            except ZEO.ClientStorage.ClientDisconnected:
                self._degrade_storage(name, fail=False)
                continue
            if tid is None:
                # Not connected yet.
                # XXX or empty ...
                self._degrade_storage(name, fail=False)
                continue
            s = tids.setdefault(tid, [])
            s.append(name)
 
        self._unrecovered_transactions = {}
        self._last_tid = None

        # Activate all optimal storages
        if tids:
            self._last_tid = max(tids.keys())
            self.storages_optimal.extend(tids[self._last_tid])
            del tids[self._last_tid]

            # Deactive all degraded storages
            for degraded_storages in tids.values():
                self.storages_degraded.extend(degraded_storages)

        t = time.time()
        self.ts = persistent.TimeStamp.TimeStamp(*(time.gmtime(t)[:5] + (t%60,)))

        if not self.storages_optimal:
            raise RAIDError("Can't start without at least one optimal storage.")

    def _degrade_storage(self, name, fail=True):
        if name in self.storages_optimal:
            self.storages_optimal.remove(name)
        self.storages_degraded.append(name)
        storage = self.storages[name]
        t = threading.Thread(target=storage.close)
        t.start()
        del self.storages[name]
        if not self.storages_optimal and fail:
            raise RAIDError("No storages remain.")

    def _apply_single_storage(self, method_name, *args, **kw):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        storages = self.storages_optimal[:]
        if not storages:
            raise RAIDError("RAID storage is failed.")

        while storages:
            # XXX storage might be degraded by now, need to check.
            name = self.storages_optimal[0]
            storage = self.storages[name]
            try:
                # Make random/hashed selection of read storage
                method = getattr(storage, method_name)
                return method(*args, **kw)
            except ZEO.ClientStorage.ClientDisconnected:
                # XXX find other possible exceptions
                self._degrade_storage(name)

    def _apply_all_storages(self, method_name, *args, **kw):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        results = []
        storages = self.storages_optimal[:]
        if not storages:
            raise RAIDError("RAID storage is failed.")

        for name in self.storages_optimal:
            storage = self.storages[name]
            try:
                method = getattr(storage, method_name)
                results.append(method(*args, **kw))
            except ZEO.ClientStorage.ClientDisconnected:
                self._degrade_storage(name)

        res = results[:]
        for test1 in res:
            for test2 in res:
                assert test1 == test2, "Results not consistent. Asynchronous storage?"
        return results[0]

    # IStorage

    def sortKey(self):
        return id(self)

    def isReadOnly(self):
        """
        XXX Revisit this approach?
        """
        return self.read_only

    def getName(self):
        return self.__name__

    def getSize(self):
        return self._apply_single_storage('getSize')

    def close(self):
        if self.closed:
            # Storage may be closed more than once, e.g. by tear-down methods
            # of tests.
            return
        self._apply_all_storages('close')
        self.storages_optimal = []
        self.closed = True

    def cleanup(self):
        # XXX This is not actually documented, it's not implemented in all
        # storages, it's not even clear when it should be called. Not
        # correctly calling storages' cleanup might leave turds.
        pass

    def load(self, oid, version):
        return self._apply_single_storage('load', oid, version)

    def loadEx(self, oid, version):
        return self._apply_single_storage('loadEx', oid, version)

    def store(self, oid, oldserial, data, version, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        self._lock_acquire()
        try:
            self._apply_all_storages('store', oid, oldserial, data, version, 
                                     transaction)
            if self._log_stores:
                oids = self._unrecovered_transactions.setdefault(self._tid, [])
                oids.append(oid)
            return self._tid
        finally:
            self._lock_release()

    def lastTransaction(self):
        return self._apply_single_storage('lastTransaction')

    def loadSerial(self, oid, serial):
        return self._apply_single_storage('loadSerial', oid, serial)

    def loadBefore(self, oid, tid):
        return self._apply_single_storage('loadBefore', oid, tid)

    #def iterator(self):
    # XXX Dunno

    def history(self, oid, version=None, size=1):
        return self._apply_single_storage('history', oid, version, size)

    def new_oid(self):
        # XXX This is not exactly a read operation, but we only need an answer from one storage
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_single_storage('new_oid')
        finally:
            self._lock_release()

    def registerDB(self, db, limit=None):
        # XXX Is it safe to register a DB with multiple storages or do we need some kind
        # of wrapper here?
        self._apply_all_storages('registerDB', db)

    def supportsUndo(self):
        return True

    def undoLog(self, first=0, last=-20, filter=None):
        return self._apply_single_storage('undoLog', first, last, filter)

    def undoInfo(self, first=0, last=-20, specification=None):
        return self._apply_single_storage('undoInfo', first, last,
                                          specification)

    def undo(self, transaction_id, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_all_storages('undo', transaction_id, transaction)
        finally:
            self._lock_release()

    def supportsTransactionalUndo(self):
        return True

    def pack(self, t, referencesf):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._apply_all_storages('pack', t, referencesf)

    def supportsVersions(self):
        return True

    def commitVersion(self, src, dest, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_all_storages('commitVersion', src, dest, transaction)
        finally:
            self._lock_release()

    def abortVersion(self, src, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._lock_acquire()
        try:
            return self._apply_all_storages('abortVersion', src, transaction)
        finally:
            self._lock_release()

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
                self._apply_all_storages('tpc_abort', transaction)
                self._transaction = None
            finally:
                self._commit_lock_release()
        finally:
            self._lock_release()

    def tpc_transaction(self):
        """The current transaction being committed."""
        return self._transaction

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
                    last_tid = get_last_transaction(storage)
                except ZEO.ClientStorage.ClientDisconnected:
                    self._degrade_storage(name, fail=False)
                    continue
                if last_tid != self._last_tid:
                    self._degrade_storage(name)

            # Create a common tid for all storages if we don't have one yet.
            if tid is None:
                now = time.time()
                t = persistent.TimeStamp.TimeStamp(*(time.gmtime(now)[:5] + (now % 60,)))
                self.ts = t.laterThan(self.ts)
                self._tid = repr(self.ts)
            else:
                self._ts = persistent.TimeStamp.TimeStamp(tid)
                self._tid = tid

            self._apply_all_storages('tpc_begin', transaction, self._tid, status)
        finally:
            self._lock_release()

    def tpc_vote(self, transaction):
        self._lock_acquire()
        try:
            if transaction is not self._transaction:
                return
            self._apply_all_storages('tpc_vote', transaction)
        finally:
            self._lock_release()

    def tpc_finish(self, transaction, callback=None):
        self._lock_acquire()
        try:
            if transaction is not self._transaction:
                return
            try:
                if callback is not None:
                    callback(self._tid)
                self._apply_all_storages('tpc_finish', transaction)
                self._last_tid = self._tid
                return self._tid
            finally:
                self._transaction = None
                self._commit_lock_release()
        finally:
            self._lock_release()

    def getSerial(self, oid):
        self._lock_acquire()
        try:
            return self._apply_single_storage('getSerial', oid)
        finally:
            self._lock_release()

    def getExtensionMethods(self):
        # XXX This is very awkward right now.
        methods = self._apply_single_storage('getExtensionMethods')
        if methods is None:
            # Allow management while status is 'failed'
            methods = {}
        methods['raid_recover'] = None
        methods['raid_status'] = None
        methods['raid_disable'] = None
        methods['raid_details'] = None
        return methods

    def __len__(self):
        return self._apply_single_storage('__len__')

    def versionEmpty(self, version):
        return self._apply_single_storage('versionEmpty', version)

    def versions(self, max=None):
        return self._apply_single_storage('versions', max)

    def modifiedInVersion(self, oid):
        return self._apply_single_storage('modifiedInVersion', oid)

    def getTid(self, oid):
        return self._apply_single_storage('getTid', oid)

    # Extension methods for RAIDStorage
    def raid_recover(self, name):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        if name not in self.storages_degraded:
            return
        self.storages_degraded.remove(name)
        self.storages_recovering.append(name)
        t = threading.Thread(target=self._recover_impl, args=(name,))
        t.start()
        return 'recovering %r' % name

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
        except:
            # *something* went wrong. Put the storage back to degraded.
            self._degrade_storage(name)
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
            last_transaction = get_last_transaction(storage)
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
                            oldserial = get_serial(storage, oid)
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
        last_transaction = get_last_transaction(storage)
        # This flag starts logging all succcessfull stores and updates those oids
        # in the second pass again.
        max_transaction = get_last_transaction(self.storages[self.storages_optimal[0]])
        self._unrecovered_transactions = {}
        self._log_stores = True
        # The init flag allows us to phrase the break condition of the 
        # following loop a little bit more elegantly.
        init = True
        while 1:
            if next_oid is None and not init:
                break

            init = False
            oid, tid, data, next_oid = self._apply_single_storage('record_iternext', next_oid)

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
                oldserial = get_serial(storage, oid)
            except ZODB.POSException.POSKeyError:
                oldserial = ZODB.utils.z64


            assert oldserial <= tid, "last_transaction and oldserial are not in-sync"

            storage.tpc_begin(t, tid=tid)
            storage.store(oid, oldserial, data, '', t)
            storage.tpc_vote(t)
            storage.tpc_finish(t)

    def raid_status(self):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        if self.storages_recovering:
            return 'recovering'
        if not self.storages_degraded:
            return 'optimal'
        if not self.storages_optimal:
            return 'failed'
        return 'degraded'

    def raid_details(self):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        return [self.storages_optimal, self.storages_recovering, self.storages_degraded]

    def raid_disable(self, name):
        if self.closed:
            raise RAIDClosedError("Storage has been closed.")
        self._degrade_storage(name, fail=False)
        return 'disabled %r' % name

    # IBlobStorage

    def storeBlob(self, oid, oldserial, data, blob, version, transaction):
        """Stores data that has a BLOB attached."""
        # XXX

    def loadBlob(self, oid, serial):
        """Return the filename of the Blob data for this OID and serial."""
        # XXX

    def temporaryDirectory(self):
        """Return a directory that should be used for uncommitted blob data.
        """
        # XXX

    # IStorageCurrentRecordIteration

    def record_iternext(self, next=None):
        """Iterate over the records in a storage."""

    # IServeable

    def lastInvalidations(self, size):
        """Get recent transaction invalidations."""
