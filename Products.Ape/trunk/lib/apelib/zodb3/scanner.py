##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Cache scanner.

Keeps a cache up to date by scanning for changes.

$Id$
"""

from thread import allocate_lock
from time import time

from BTrees.OOBTree import OOBTree, OOSet, difference
from BTrees.IOBTree import IOBTree
from zLOG import LOG, DEBUG

# FUTURE_TIMEOUT defines how long to keep source information regarding
# OIDs that might be used soon.
future_timeout = 10 * 60


class PoolScanControl:
    """Scanning for a pool of connections.

    A ScanControl instance is an attribute of an ApeDB instance.  The
    actual scanning is delegated to a Scanner instance attached to an
    ApeStorage.  The delegation theoretically permits scanning to
    occur on a ZEO server while the ScanControl instances run on
    separate ZEO clients.

    Assigns scanner-specific identities to database connections for
    the purpose of tracking which OIDs are still in use.
    """

    def __init__(self, storage, db=None, scan_interval=10):
        self.storage = storage
        self.db = db
        self.next_conn_id = 1
        self.conn_oids = IOBTree()   # IOBTree({ conn_id -> OOSet([oid]) } })
        self.oids = OOSet()          # OOSet([oid])
        self.lock = allocate_lock()
        self.scan_interval = scan_interval
        self.next_scan = time() + scan_interval


    def new_connection(self):
        """Returns a ConnectionScanControl to attach to a new connection.
        """
        self.lock.acquire()
        try:
            conn_id = self.next_conn_id
            self.next_conn_id = conn_id + 1
            return ConnectionScanControl(self, conn_id)
        finally:
            self.lock.release()


    def set_connection_oids(self, conn_id, oids):
        """Records the OIDs a connection is using and periodically scans.
        """
        changed = 0
        new_oids = OOSet()
        self.lock.acquire()
        try:
            if oids:
                self.conn_oids[conn_id] = OOSet(oids)
            else:
                if self.conn_oids.has_key(conn_id):
                    del self.conn_oids[conn_id]
            for set in self.conn_oids.values():
                new_oids.update(set)
            if self.oids != new_oids:
                self.oids = new_oids
                changed = 1
        finally:
            self.lock.release()
        if changed:
            self.storage.scanner.set_oids(new_oids)


    def elapsed(self):
        """Returns true if the scan interval has elapsed.
        """
        now = time()
        if now >= self.next_scan:
            self.next_scan = now + self.scan_interval
            return 1
        return 0


    def scan(self):
        """Runs a scan and sends invalidation messages to the database.
        """
        LOG('Ape', DEBUG, 'Scanning %d objects.' % len(self.oids))
        scanner = self.storage.scanner
        inv = scanner.scan()
        scanner.prune_future()
        LOG('Ape', DEBUG,
            'Finished scanning. %d objects changed.' % len(inv))
        if inv:
            # Some objects changed and the caches need to be invalidated.
            d = {}
            for oid in inv:
                d[oid] = 1
            if self.db is not None:
                self.db.invalidate(d)
            else:
                LOG('Ape', DEBUG, "No database set, so can't invalidate!")


class ConnectionScanControl:
    """Scanning for a database connection (an ApeConnection.)

    Delegates to a ScanControl, which in turn delegates to a Scanner.
    """

    def __init__(self, pool_ctl, conn_id):
        self.pool_ctl = pool_ctl
        self.conn_id = conn_id
        self.next_update = 0

    def elapsed(self):
        """Returns true if the connection-specific scan interval has elapsed.

        The interval prevents connections from calling set_oids() with
        excessive frequency.
        """
        now = time()
        if now >= self.next_update:
            self.next_update = now + self.pool_ctl.scan_interval
            return 1
        return 0

    def set_oids(self, oids):
        """Records the OIDs this connection is using.
        """
        self.pool_ctl.set_connection_oids(self.conn_id, oids)


class Scanner:
    """Scanning for an ApeStorage.

    Uses gateways to scan for changes.
    """

    def __init__(self):
        self.current = OOBTree()  # OOBTree({ oid -> {source->state} })
        self.future = {}          # { oid -> ({source->state}, atime) }
        self.lock = allocate_lock()
        self.storage = None

    def set_oids(self, oids):
        """Sets the list of OIDs to scan.

        Gathers source information about new OIDs and discards
        source information for OIDs no longer in use.
        """
        new_sources = {}  # { oid -> sourcedict }
        self.lock.acquire()
        try:
            removed = difference(self.current, oids)
            for oid in removed.keys():
                del self.current[oid]
            added = difference(oids, self.current)
            for oid in added.keys():
                if self.future.has_key(oid):
                    # Source info for this OID was provided earlier.
                    sources, atime = self.future[oid]
                    del self.future[oid]
                    self.current[oid] = sources
                else:
                    new_sources[oid] = None
        finally:
            self.lock.release()
        if new_sources:
            # Load source info the slow way.
            if self.storage is not None:
                LOG('Ape', DEBUG, 'Getting sources for %d oids.'
                    % len(new_sources))
                new_sources = self.storage.get_all_sources(new_sources.keys())
            else:
                LOG('Ape', DEBUG, "Can't get sources for %d oids. "
                    "Assuming no sources!" % len(new_sources))
                # This will cause the scanner to miss changes, but
                # since no storage is known, there is little we can
                # do.
                for oid in new_sources.keys():
                    new_sources[oid] = {}
            self.lock.acquire()
            try:
                for oid, sources in new_sources.items():
                    if not self.current.has_key(oid):
                        self.current[oid] = sources
                    # else something else added the source info
                    # while self.lock was released.
            finally:
                self.lock.release()


    def after_load(self, oid, sources):
        """Called by the storage after an object is loaded.
        """
        if sources is None:
            sources = {}
        self.lock.acquire()
        try:
            if not self.current.has_key(oid):
                # This object is being loaded for the first time.
                # Make a record of its current state immediately
                # so that the next scan can pick up changes.
                self.future[oid] = (sources, time())
            # else we already have info about this object, and now
            # isn't a good time to update self.current since that
            # would prevent changes from being detected at a time when
            # it's possible to send invalidation messages.
        finally:
            self.lock.release()


    def scan(self):
        """Scan sources, returning the OIDs of changed objects.
        """
        to_scan = {}        # { repo -> { source -> state } }
        to_invalidate = {}  # { oid -> 1 }
        self.lock.acquire()  # lock because oid_states might be self.current.
        try:
            for oid, sources in self.current.items():
                for source, state in sources.items():
                    repo, location = source
                    to_scan.setdefault(repo, {})[source] = state
        finally:
            self.lock.release()
        changes = {}
        for repo, d in to_scan.items():
            c = repo.poll(d)
            if c:
                changes.update(c)
        if changes:
            # Something changed.  Map the changes back to oids and
            # update self.current.
            self.lock.acquire()
            try:
                for oid, sources in self.current.items():
                    for source, state in sources.items():
                        if changes.has_key(source):
                            to_invalidate[oid] = 1
                            sources[source] = changes[source]
            finally:
                self.lock.release()
        return to_invalidate.keys()


    def prune_future(self):
        """Prunes the cache of future source information.
        """
        if self.future:
            self.lock.acquire()
            try:
                # OIDs older than some timeout will probably never be loaded.
                cutoff = time() - future_timeout
                for oid, (sources, atime) in self.future.items():
                    if atime < cutoff:
                        del self.future[oid]
            finally:
                self.lock.release()
            LOG('Ape', DEBUG,
                'Future sources cache size: %d objects.' % len(self.future))


    def changed_sources(self, oid, sources):
        """Records changes to sources made by ZODB.
        """
        self.current[oid] = sources
        if self.future.has_key(oid):
            del self.future[oid]
