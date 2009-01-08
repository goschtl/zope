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
import shutil
import random

import zc.lockfile
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
from ZEO.runzeo import ZEOOptions

import gocept.zeoraid.interfaces
import gocept.zeoraid.recovery

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


class ThreadedApplyStorage(threading.Thread):

    reliable = None
    result = None
    exception = None

    def __init__(self, storage_name, method_name, args, kw,
	         expect_connected, apply_storage):
        super(ThreadedApplyStorage, self).__init__()
        self.storage_name = storage_name
        self.method_name = method_name
        self.args = args
        self.kw = kw
        self.expect_connected = expect_connected
        self.__apply_storage = apply_storage

    def run(self):
        try:
            self.reliable, self.result = self.__apply_storage(
                self.storage_name, self.method_name, self.args,
                self.kw, self.expect_connected)
        except Exception, e:
            self.exception = e


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
                              ZODB.interfaces.IStorageIteration,
                              ZEO.interfaces.IServeable,
                              )

    blob_fshelper = None

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

    # Timeout for threaded/parallel operations on backend storages.
    timeout = 60

    def __init__(self, name, openers, read_only=False, blob_dir=None,
                 shared_blob_dir=False, zeo=None):
        self.__name__ = name
        self.read_only = read_only
        self.shared_blob_dir = shared_blob_dir
        self.zeo = zeo
        self.storages = {}
        self._threads = set()
        # Temporary files and directories that should be removed at the end of
        # the two-phase commit. The list must only be modified while holding
        # the commit lock.
        self.tmp_paths = []

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

        # No storage is recovering initially
        self.storage_recovering = None

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
            # We give all the threads a chance to get done quickly.
            # This is mostly a convenience for the tests to not annoy.
            thread.join(5)

    def getName(self):
        """The name of the storage."""
        return self.__name__

    def getSize(self):
        """An approximate size of the database, in bytes."""
        try:
            return self._apply_single_storage('getSize')[0]
        except gocept.zeoraid.interfaces.RAIDError:
            return 0

    def history(self, oid, version='', size=1):
        """Return a sequence of history information dictionaries."""
        assert version is ''
        return self._apply_single_storage('history', (oid, size))[0]

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
        try:
            return self._apply_single_storage('__len__')[0]
        except gocept.zeoraid.interfaces.RAIDError:
            return 0

    def load(self, oid, version=''):
        """Load data for an object id and version."""
        assert version is ''
        return self._apply_single_storage('load', (oid,))[0]

    def loadBefore(self, oid, tid):
        """Load the object data written before a transaction id."""
        return self._apply_single_storage('loadBefore', (oid, tid))[0]

    def loadSerial(self, oid, serial):
        """Load the object record for the give transaction id."""
        return self._apply_single_storage('loadSerial', (oid, serial))[0]

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
                self._tpc_cleanup()
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
                self._tpc_cleanup()
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
            base_dir = tempfile.mkdtemp(dir=os.path.dirname(blob))
            self.tmp_paths.append(base_dir)
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
            if self.shared_blob_dir:
                result, storage = self._apply_single_storage(
                    'storeBlob',
                    (oid, oldserial, data, blob, version, transaction))
                self._apply_all_storages(
                    'store', (oid, oldserial, data, version, transaction),
                    exclude=(storage,), ignore_noop=True)
            else:
                # The back end storages receive links to the blob file and
                # take care of them appropriately. We have to remove the
                # original link to the blob file ourselves.
                self.tmp_paths.append(blob)
                self._apply_all_storages('storeBlob', get_blob_data)
            return self._tid
        finally:
            self._write_lock.release()

    def loadBlob(self, oid, serial):
        """Return the filename of the Blob data for this OID and serial."""
        # XXX needs some refactoring
        blob_filename = self.blob_fshelper.getBlobFilename(oid, serial)
        if os.path.exists(blob_filename):
            return blob_filename

        if self.shared_blob_dir:
            # We're using a back end shared directory. If the file isn't here,
            # it's not anywhere.
            raise ZODB.POSException.POSKeyError("No blob file", oid, serial)

        backend_filename = self._apply_single_storage(
            'loadBlob', (oid, serial))[0]
        lock_filename = blob_filename + '.lock'
        self.blob_fshelper.createPathForOID(oid)
        try:
            lock = zc.lockfile.LockFile(lock_filename)
        except zc.lockfile.LockError:
            while True:
                time.sleep(0.1)
                try:
                    lock = zc.lockfile.LockFile(lock_filename)
                except zc.lockfile.LockError:
                    pass
                else:
                    # We have the lock. We should be able to get the file now.
                    lock.close()
                    try:
                        os.remove(lock_filename)
                    except OSError:
                        pass
                    break

            if os.path.exists(blob_filename):
                return blob_filename

            return None # XXX see ClientStorage

        try:
            optimistic_copy(backend_filename, blob_filename)
        finally:
            lock.close()
            try:
                os.remove(lock_filename)
            except OSError:
                pass

        return blob_filename

    def openCommittedBlobFile(self, oid, serial, blob=None):
        """Return a file for committed data for the given object id and serial
        """

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
        return self._apply_single_storage('undoLog', (first, last, filter))[0]

    def undoInfo(self, first=0, last=-20, specification=None):
        """Return a sequence of descriptions for undoable transactions."""
        return self._apply_single_storage(
            'undoInfo', (first, last, specification))[0]

    # IStorageCurrentRecordIteration

    def record_iternext(self, next=None):
        """Iterate over the records in a storage."""
        return self._apply_single_storage('record_iternext', (next,))[0]

    # IStorageIteration

    def iterator(self, start=None, stop=None):
        """Return an IStorageTransactionInformation iterator."""
        # XXX This should really include fail-over for iterators over storages
        # that degrade or recover while this iterator is running.
        return self._apply_single_storage('iterator', (start, stop))[0]

    # IServeable

    # Note: We opt to not implement lastInvalidations until ClientStorage does.
    # def lastInvalidations(self, size):
    #    """Get recent transaction invalidations."""
    #    return self._apply_single_storage('lastInvalidations', (size,))[0]

    def tpc_transaction(self):
        """The current transaction being committed."""
        return self._transaction

    def getTid(self, oid):
        """The last transaction to change an object."""
        return self._apply_single_storage('getTid', (oid,))[0]

    def getExtensionMethods(self):
        # This method isn't officially part of the interface but it is supported.
        methods = dict.fromkeys(
            ['raid_recover', 'raid_status', 'raid_disable', 'raid_details',
            'raid_reload'])
        return methods

    # IRAIDStorage

    @ensure_open_storage
    def raid_status(self):
        if self.storage_recovering:
            return 'recovering'
        if not self.storages_degraded:
            return 'optimal'
        if not self.storages_optimal:
            return 'failed'
        return 'degraded'

    @ensure_open_storage
    def raid_details(self):
        return [self.storages_optimal, self.storage_recovering, self.storages_degraded]

    @ensure_open_storage
    def raid_disable(self, name):
        self._degrade_storage(name, fail=False)
        return 'disabled %r' % (name,)

    @ensure_open_storage
    def raid_recover(self, name):
        if name not in self.storages_degraded:
            return
        t = threading.Thread(target=self._recover_impl, args=(name,))
        self._threads.add(t)
        t.setDaemon(True)
        t.start()
        return 'recovering %r' % (name,)

    @ensure_open_storage
    def raid_reload(self):
        if not self.zeo:
            raise RuntimeError(
                'Cannot reload config without running inside ZEO.')

        options = ZEOOptions()
        options.realize(['-C', self.zeo.options.configfile])
        new_storages = dict([(o.name,o) for o in options.storages[0].config.storages])
        storages_to_add = [(name, opener) for name, opener in new_storages.items() if name not in self.openers]
        storages_to_remove = [(name, opener) for name, opener in self.openers.items() if name not in new_storages]

        s = ""
        for name, opener in storages_to_remove:
            self.raid_disable(name)
            s += "removed %s\n" % name
        for name, opener in storages_to_add:
            self.openers[name] = opener
            self.storages_degraded.append(name)
            s += "added %s\n" % name
        return s

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

    def __apply_storage(self, storage_name, method_name, args=(), kw={},
                        expect_connected=True):
        """Calls a method on a given backend storage.

        Returns a tuple (reliable, result).

        All exceptions raised by this method indicate a user error. Storage
        failure is signalled by declaring the result unreliable.

        """
        # XXX storage might be degraded by now, need to check.
        storage = self.storages[storage_name]
        method = getattr(storage, method_name)
        reliable = True
        result = None
        try:
            result = method(*args, **kw)
        except ZODB.POSException.StorageError:
            # Handle StorageErrors first, otherwise they would be swallowed
            # when POSErrors are handled.
            reliable = False
        except (ZODB.POSException.POSError,
                transaction.interfaces.TransactionError), e:
            # These exceptions are valid answers from the storage. They don't
            # indicate storage failure.
            raise
        except Exception:
            reliable = False

        if (isinstance(storage, ZEO.ClientStorage.ClientStorage) and
            expect_connected and not storage.is_connected()):
            reliable = False

        if not reliable:
            self._degrade_storage(storage_name)
        return (reliable, result)

    @ensure_open_storage
    def _apply_single_storage(self, method_name, args=(), kw={}):
        """Calls the given method on a random optimal storage."""
        # Try to find a storage that we can talk to. Stop after we found a
        # reliable result.
        storages = self.storages_optimal[:]
        reliable = False
        while not reliable:
            if not storages:
                break
            name = random.choice(storages)
            storages.remove(name)
            reliable, result = self.__apply_storage(
                name, method_name, args, kw)
            if reliable:
                return result, name

        # We could not determine a result from any storage.
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")

    @ensure_open_storage
    def _apply_all_storages(self, method_name, args=(), kw={},
                            expect_connected=True, exclude=(),
                            ignore_noop=False):
        """Calls the given method on all optimal backend storages in order.

        `args` can be given as an n-tuple with the positional arguments that
        should be passed to each storage.

        Alternatively `args` can be a callable that returns an iterable. The
        N-th item of the iterable is expected to be a tuple, passed to the
        N-th storage.

        """
        if callable(args):
            argument_iterable = args()
        else:
            # Provide a fallback if `args` is given as a simple tuple.
            static_arguments = args
            def dummy_generator():
                while True:
                    yield static_arguments
            argument_iterable = dummy_generator()

        applicable_storages = self.storages_optimal[:]
        applicable_storages = [storage for storage in applicable_storages
                               if storage not in exclude]

        # Run __apply_storage on all applicable storages in parallel.
        threads = []
        for storage_name in applicable_storages:
            args = argument_iterable.next()
            t = ThreadedApplyStorage(storage_name, method_name, args, kw,
                                     expect_connected, self.__apply_storage)
            threads.append(t)
            t.start()

        # Wait for threads to finish and pick up results.
        results = []
        exceptions = []
        for thread in threads:
            # XXX The timeout should be calculated such that the total time
            # spent in this loop doesn't grow with the number of storages.
            thread.join(self.timeout)
            if thread.isAlive():
                # Storage timed out.
                self._degrade_storage(thread.storage_name)
                self._threads.add(thread)
                continue
            if thread.exception:
                exceptions.append(thread.exception)
            elif thread.reliable:
                results.append(thread.result)

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

        # We did not get any reliable result, making this call effectively a
        # no-op.
        if ignore_noop:
            return
        raise gocept.zeoraid.interfaces.RAIDError("RAID storage is failed.")

    def _recover_impl(self, name):
        self.storages_degraded.remove(name)
        self.storage_recovering = name
        storage = self.openers[name].open()
        self.storages[name] = storage
        recovery = gocept.zeoraid.recovery.Recovery(
            self, storage, self._finalize_recovery,
            recover_blobs=(self.blob_fshelper and not self.shared_blob_dir))
        for msg in recovery():
            logger.debug(str(msg))

    def _finalize_recovery(self, storage):
        self._write_lock.acquire()
        try:
            self.storages_optimal.append(self.storage_recovering)
            self._synchronise_oids()
            self.storage_recovering = None
        finally:
            self._write_lock.release()

    def _synchronise_oids(self):
        # Try allocating the same OID from all storages. This is done by
        # determining the maximum and making all other storages increase
        # their OID until they hit the maximum. While any storage yields
        # an OID above the maximum, we try again with that value.
        max_oid = None
        lagging = self.storages_optimal[:]
        while lagging:
            storage = lagging.pop()
            while True:
                reliable, oid = self.__apply_storage(storage, 'new_oid')
                if not reliable:
                    break
                if oid < max_oid:
                    continue
                if oid > max_oid:
                    max_oid = oid
                    lagging = [s for s in self.storages_optimal
                               if s != storage]
                break

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

    def _tpc_cleanup(self):
        while self.tmp_paths:
            path = self.tmp_paths.pop()
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except OSError:
                pass


def optimistic_copy(source, target):
    """Try creating a hard link to source at target. Fall back to copying the
    file.
    """
    try:
        os.link(source, target)
    except OSError:
        ZODB.blob.copied("Copied blob file %r to %r.", source, target)
        file1 = open(source, 'rb')
        file2 = open(target, 'wb')
        try:
            ZODB.utils.cp(file1, file2)
        finally:
            file1.close()
            file2.close()
