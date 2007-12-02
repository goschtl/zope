import logging
import weakref
from time import time # we do it this way so tests can monkeypatch stubs

import persistent
import persistent.mapping
import ZODB.Connection
import ZODB
from ZODB.DB import KeyedConnectionPool
import ZODB.interfaces
import ZODB.POSException
import ZODB.utils
import BTrees
import zope.interface

BEGIN = 'BEGIN'
COMMIT = 'COMMIT'
VOTE = 'VOTE'
FINISH = 'FINISH'

logger = logging.getLogger('ZODB.DB.virtual')


class Coordinator(ZODB.Connection.Connection):

    _status = None

    def close(self):
        if not self._needs_to_join:
            # We're currently joined to a transaction.
            raise ConnectionStateError("Cannot close a connection joined to "
                                       "a transaction")
        self._db.closing(self) # let the virtual connections be closed first
        ZODB.Connection.Connection.close(self)

    def member_register(self, connection, obj):
        if self._needs_to_join:
            self.transaction_manager.get().join(self)
            self._needs_to_join = False

    def _coordinate_begin(self, transaction):
        if self._status is None:
            ZODB.Connection.Connection.tpc_begin(self, transaction)
            self._status = BEGIN
            self._virtual_tpc_members = set()
            self._member_modified = []
        else:
            assert self._status == BEGIN

    def member_tpc_begin(self, virtual_storage, transaction):
        self._coordinate_begin(transaction)
        self._virtual_tpc_members.add(virtual_storage)

    def _coordinate_commit(self, transaction):
        if not self._virtual_tpc_members and self._status == COMMIT:
            # everyone has checked in.  Now is the time to do a commit
            # for the coordinator
            ZODB.Connection.Connection.commit(self, transaction)

    def member_committed(self, connection, transaction):
        self._virtual_tpc_members.remove(connection._storage)
        self._coordinate_commit(transaction)

    def _coordinate_vote(self, transaction):
        if self._status == COMMIT:
            try:
                vote = self._storage.tpc_vote
            except AttributeError:
                res = None
            else:
                res = vote(transaction)
            self._vote_result = res
            self._handle_serial(res)
            self._status = VOTE
        else:
            assert self._status == VOTE
        return self._vote_result

    def member_tpc_vote(self, virtual_storage, transaction):
        res = self._coordinate_vote(transaction)
        self._virtual_tpc_members.add(virtual_storage)
        return res

    def _coordinate_finish(self, transaction):
        if not self._virtual_tpc_members and self._status == FINISH:
            # everyone has checked in.  Now is the time to do a tpc_finish
            # for the coordinator, sending in all functions
            def callback(tid):
                d = dict.fromkeys(self._modified)
                for connection, modified in self._member_modified:
                    self._db.invalidate(tid, modified, connection)
                self._db.invalidate(tid, d, self)
            # It's important that the storage calls the passed function while it
            # still has its lock. We don't want another thread to be able to read
            # any updated data until we've had a chance to send an invalidation
            # message to all of the other connections!
            self._storage.tpc_finish(transaction, callback)
            self._tpc_cleanup()

    def member_tpc_finish(self, virtual_storage, transaction, connection,
                          modified):
        self._member_modified.append((connection, modified))
        self._virtual_tpc_members.remove(virtual_storage)
        self._coordinate_finish(transaction)

    def tpc_begin(self, transaction):
        self._coordinate_begin(transaction)

    def commit(self, transaction):
        self._status = COMMIT
        self._coordinate_commit(transaction)

    def tpc_vote(self, transaction):
        self._coordinate_vote(transaction)

    def tpc_finish(self, transaction):
        self._status = FINISH
        self._coordinate_finish(transaction)

    def _tpc_cleanup(self):
        ZODB.Connection.Connection._tpc_cleanup(self)
        self._status = None
        self._member_modified = None
        self._virtual_tpc_members = None
        self._vote_result = None
    
    # no changes to abort needed

    def makeGhost(self, oid, p, serial):
        obj = self._reader.getGhost(p)
        self._pre_cache[oid] = obj
        obj._p_oid = oid
        obj._p_jar = self
        obj._p_changed = None
        obj._p_serial = serial
        self._pre_cache.pop(oid)
        self._cache[oid] = obj
        return obj


class VirtualDB(object):
    def __init__(self, virtual_storage, db):
        self._db = db
        self._storage = virtual_storage
        self.oid = virtual_storage._p_oid

    @property
    def databases(self):
        return self._db.databases

    @property
    def database_name(self):
        return '%s:zc.virtualstorage:%s' % (
            self._db.database_name,
            self._storage._p_oid)

    @property
    def classFactory(self):
        return self._db.classFactory

    def _returnToPool(self, connection):
        assert connection._db is self
        self._db.returnVirtualConnection(connection)


class DB(ZODB.DB):
    klass = Coordinator

    def __init__(self, storage, pool_size=7, cache_size=400,
                 historical_pool_size=3, historical_cache_size=1000,
                 historical_timeout=300, database_name='unnamed',
                 databases=None, virtual_pool_size=3,
                 virtual_cache_size=1000, virtual_timeout=300):
        ZODB.DB.__init__(self, storage, pool_size, cache_size,
                         historical_pool_size, historical_cache_size,
                         historical_timeout, database_name, databases)
        self._virtual_cache_size = virtual_cache_size
        self.virtual_pool = KeyedConnectionPool(
            virtual_pool_size, virtual_timeout)
        self._virtual_connection_map = weakref.WeakKeyDictionary()

    def _connectionMap(self, f):
        self._a()
        try:
            self.pool.map(f)
            self.historical_pool.map(f)
            self.virtual_pool.map(f)
        finally:
            self._r()

    def getVirtualConnection(self, virtual_storage):
        connection = virtual_storage._p_jar
        if connection is None:
            connection = ZODB.interfaces.IConnection(virtual_storage)
        assert virtual_storage._p_oid is not None
        assert isinstance(connection, Coordinator)
        assert connection.db() is self
        assert connection._opened
        key = (virtual_storage._p_oid, connection.before)
        pool = self.virtual_pool
        self._a()
        try:
            map = self._virtual_connection_map.get(connection)
            if map is None:
                map = self._virtual_connection_map[connection] = (
                    weakref.WeakValueDictionary())
            res = map.get(virtual_storage._p_oid)
            if res is None:
                res = pool.pop(key)
                if res is None:
                    res = VirtualConnection(
                        VirtualDB(virtual_storage, self),
                        self.getVirtualConnectionCacheSize(),
                        connection.before)
                    pool.push(res, key)
                    res = pool.pop(key)
                    assert res is not None
                else:
                    res._storage = res._db._storage = virtual_storage
                map[virtual_storage._p_oid] = res
            if not res._opened:
                res.open(connection.transaction_manager)
            pool.availableGC()
            return res
        finally:
            self._r()

    def closing(self, coordinator):
        self._a()
        try:
            map = self._virtual_connection_map.get(coordinator)
            if map is not None:
                for connection in map.values():
                    connection.close()
                    assert connection._storage is connection._db._storage is None
                del self._virtual_connection_map[coordinator]
        finally:
            self._r()

    def returnVirtualConnection(self, connection):
        assert isinstance(connection, VirtualConnection)
        storage = connection._storage
        key = (storage._p_oid, connection.before)
        self._a()
        try:
            coordinator = storage._p_jar
            assert coordinator._db is self
            connection._opened = None
            am = self._activity_monitor
            if am is not None:
                am.closedConnection(connection)
            map = self._virtual_connection_map[coordinator]
            del map[storage._p_oid]
            connection._storage = connection._db._storage = None
            self.virtual_pool.repush(connection, key)
        finally:
            self._r()

    def getVirtualConnectionCacheSize(self):
        return self._virtual_cache_size

    def setVirtualConnectionCacheSize(self, size):
        self._virtual_cache_size = size
        def setsize(c):
            c._cache.cache_size = size
        self._a()
        try:
            self.virtual_pool.map(setsize)
        finally:
            self._r()

    def getVirtualConnectionTimeout(self):
        return self.virtual_pool.timeout

    def setVirtualConnectionTimeout(self, timeout):
        self._a()
        try:
            self.virtual_pool.timeout = timeout
        finally:
            self._r()

    def getVirtualConnectionPoolSize(self):
        return self.virtual_pool.size

    def setVirtualConnectionPoolSize(self, size):
        self._a()
        try:
            self.virtual_pool.size = size
        finally:
            self._r()


class VirtualConnection(ZODB.Connection.Connection):

    def __init__(self, db, cache_size=400, before=None):
        ZODB.Connection.Connection.__init__(self, db, cache_size, before)
        self._raw_invalidated = set()

    def _register(self, obj=None):
        self._normal_storage._p_jar.member_register(self, obj)
        ZODB.Connection.Connection._register(self, obj)

    def commit(self, transaction):
        ZODB.Connection.Connection.commit(self, transaction)
        self._normal_storage._p_jar.member_committed(self, transaction)

    def tpc_finish(self, transaction):
        self._normal_storage.tpc_finish(transaction, self)
        self._tpc_cleanup()

    def invalidate(self, tid, oids):
        if self.before is not None:
            # this is an historical connection.  Invalidations are irrelevant.
            return
        getInvalidatedOID = self._normal_storage.getInvalidatedOID
        self._inv_lock.acquire()
        try:
            if self._txn_time is None:
                self._txn_time = tid
            if self._opened is not None:
                mapped = [oid for oid in
                          (getInvalidatedOID(o) for o in oids)
                          if oid is not None]
                self._invalidated.update(mapped)
            else:
                # invalidations while closed are not mapped (because accessing
                # the virtual storage while its connection is closed will
                # generate an error)
                self._raw_invalidated.update(oids)
        finally:
            self._inv_lock.release()

    # Process pending invalidations.
    def _flush_invalidations(self):
        getInvalidatedOID = self._normal_storage.getInvalidatedOID
        self._inv_lock.acquire()
        try:
            # see comments in ZODB.Connection.Connection._flush_invalidations.
            # we override this to use the _raw_invalidated values from the
            # ``invalidate`` method above.
            if self._invalidatedCache:
                self._invalidatedCache = False
                invalidated = self._cache.cache_data.copy()
            else:
                if self._raw_invalidated:
                    self._invalidated.update(
                        oid for oid in
                        (getInvalidatedOID(o) for o in self._raw_invalidated)
                        if oid is not None)
                invalidated = dict.fromkeys(self._invalidated)
            self._raw_invalidated.clear()
            self._invalidated = set()
            self._txn_time = None
        finally:
            self._inv_lock.release()
        self._cache.invalidate(invalidated)
        # Now is a good time to collect some garbage.
        self._cache.incrgc()


class VirtualStorage(persistent.Persistent):

    zope.interface.implements(ZODB.interfaces.IBlobStorage)

    def __init__(self, base=None):
        if base is not None and not base.isReadOnly():
            raise ValueError('base must be read only')
        self.base = base
        self.local = BTrees.OOBTree.BTree()
        self.reverse_local = BTrees.OOBTree.BTree() # needed for invalidations
        self.new = BTrees.OOBTree.TreeSet()
        self.bucket = BTrees.OOBTree.BTree() # real oid to effective oid, obj
        self._readonly = False
        self._giveRootOID = True

    def temporaryDirectory(self):
        return self._p_jar._storage.temporaryDirectory()

    def getSize(self):
        return self._p_jar._storage.getSize() # shrug.

    def freeze(self):
        if self._readonly:
            raise ValueError('already frozen')
        self._readonly = True

    def sortKey(self):
        return '.'.join((self._p_jar.sortKey(), self._p_oid))
    getName = sortKey

    def getInvalidatedOID(self, oid, default=None):
        if oid in self.new:
            return oid
        return self.reverse_local.get(oid, default)

    def isReadOnly(self):
        return self._readonly or self._p_jar.isReadOnly()

    def load(self, oid, version=''):
        if version != '':
            raise ValueError('no versions allowed')
        real = self.local.get(oid)
        if real is None:
            if oid in self.new:
                real = oid
            elif self.base is not None:
                return self.base.load(oid)
            else:
                raise ZODB.POSException.POSKeyError(oid)
        return self._p_jar._storage.load(real, version)

    def loadBefore(self, oid, serial):
        # note that our views on our data structures are already MVCC.
        real = self.local.get(oid)
        if real is None:
            if oid in self.new:
                real = oid
            elif self.base is not None:
                return self.base.loadBefore(oid, serial)
            else:
                raise ZODB.POSException.POSKeyError(oid)
        return self._p_jar._storage.loadBefore(real, serial)

    def loadBlob(self, oid, serial):
        real = self.local.get(oid)
        if real is None:
            if oid in self.new:
                real = oid
            elif self.base is not None:
                return self.base.loadBlob(oid, serial)
            else:
                raise ZODB.POSException.POSKeyError(oid)
        return self._p_jar._storage.loadBlob(real, serial)

    def new_oid(self):
        if self._giveRootOID and self.base is None and not self.new:
            res = ZODB.utils.z64
            self._giveRootOID = False
        else:
            res = self._p_jar.new_oid()
            self.new.insert(res)
        return res

    def store(self, oid, oldserial, data, version, transaction):
        assert version == ''
        return self._store(
            oid, data,
            lambda real: self._p_jar._storage.store(
                real, oldserial, data, '', transaction))

    def storeBlob(self, oid, oldserial, data, blobfilename, version,
                  transaction):
        assert version == ''
        return self._store(
            oid, data,
            lambda real: self._p_jar._storage.storeBlob(
                real, oldserial, data, blobfilename, '', transaction))

    def _store(self, oid, data, callable):
        if oid in self.local:
            real = self.local[oid]
        elif oid in self.new:
            real = oid
        else:
            real = self._p_jar.new_oid()
            self.local[oid] = real
            self.reverse_local[real] = oid
        serial = callable(real)
        if oid not in self.bucket:
            # prevent packing away
            self.bucket[oid] = self._p_jar.makeGhost(real, data, serial)
        return serial

    def tpc_begin(self, transaction):
        if self.isReadOnly():
            raise ZODB.POSException.ReadOnlyError()
        self._p_jar.member_tpc_begin(self, transaction)

    def tpc_vote(self, transaction):
        res = self._p_jar.member_tpc_vote(self, transaction)
        if res:
            res = [
                (local, serial) for local, serial in (
                    (self.getInvalidatedOID(oid), serial) for oid, serial in
                    res)
                if local is not None]
        return res

    def _getRealOID(self, oid):
        if oid in self.new:
            return oid
        return self.local[oid] # or else it is an error, even if it is in base

    def tpc_finish(self, transaction, connection):
        modified = dict.fromkeys(
            self._getRealOID(oid) for oid in connection._modified)
        self._p_jar.member_tpc_finish(self, transaction, connection, modified)

    def tpc_abort(self, transaction):
        pass # normal invalidations in coordinator of modified objects are
        # sufficient to make `local` `reverse_local` and `bucket` fine.
