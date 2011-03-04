##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Demo storage that stores changes in a non-memory storage
"""

import threading

import ZODB.POSException
from ZODB.utils import p64, u64, z64

from zc.demostorage2.synchronized import synchronized

class DemoStorage2:

    def __init__(self, base, changes):
        self.changes = changes
        self.base = base

        supportsUndo = getattr(changes, 'supportsUndo', None)
        if supportsUndo is not None and supportsUndo():
            for meth in ('supportsUndo', 'undo', 'undoLog', 'undoInfo'):
                setattr(self, meth, getattr(changes, meth))

        for meth in ('getSize', 'history', 'isReadOnly', 'sortKey',
                     'tpc_transaction'):
            setattr(self, meth, getattr(changes, meth))

        lastInvalidations = getattr(changes, 'lastInvalidations', None)
        if lastInvalidations is not None:
            self.lastInvalidations = lastInvalidations
    
        self._oid = max(u64(changes.new_oid()), 1l << 62)
        self._lock = threading.RLock()
        self._commit_lock = threading.Lock()

        self._transaction = None

    def close(self):
        self.base.close()
        self.changes.close()

    def getName(self):
        return "DemoStorage2(%s, %s)" % (
            self.base.getName(), self.changes.getName())

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.getName())

    def getTid(self, oid):
        try:
            return self.changes.getTid(oid)
        except ZODB.POSException.POSKeyError:
            return self.base.getTid(oid)

    @synchronized
    def lastTransaction(self):
        t = self.changes.lastTransaction()
        if t == z64:
            t = self.base.lastTransaction()
        return t

    def __len__(self):
        return len(self.changes)

    @synchronized
    def load(self, oid, version=''):
        try:
            return self.changes.load(oid, version)
        except ZODB.POSException.POSKeyError:
            return self.base.load(oid, version)

    @synchronized
    def loadBefore(self, oid, tid):
        try:
            result = self.changes.loadBefore(oid, tid)
        except ZODB.POSException.POSKeyError:
            return self.base.loadBefore(oid, tid)

    @synchronized
    def loadSerial(self, oid, serial):
        try:
            return self.changes.loadSerial(oid, serial)
        except ZODB.POSException.POSKeyError:
            return self.base.loadSerial(oid, serial)

    @synchronized
    def new_oid(self):
        self._oid += 1
        return p64(self._oid)

    def pack(self, pack_time, referencesf):
        pass

    def registerDB(self, db):
        self.base.registerDB(db)
        self.changes.registerDB(db)

    @synchronized
    def store(self, oid, serial, data, version, transaction):
        assert version==''
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        # See if we already have changes for this oid
        try:
            old = self.changes.load(oid, '')[1]
        except ZODB.POSException.POSKeyError:
            try:
                old = self.base.load(oid, '')[1]
            except ZODB.POSException.POSKeyError:
                old = serial
                
        if old != serial:
            raise ZODB.POSException.ConflictError(
                oid=oid, serials=(old, serial)) # XXX untested branch

        return self.changes.store(oid, serial, data, '', transaction)


    @synchronized
    def tpc_abort(self, transaction):
        if self._transaction is not transaction:
            return
        self._transaction = None
        try:
            self.changes.tpc_abort(transaction)
        finally:
            self._commit_lock.release()

    def tpc_begin(self, transaction, tid=None, status=' '):
        if self._transaction is transaction:
            return
        self._commit_lock.acquire()
        self._begin(transaction, tid, status)

    @synchronized
    def _begin(self, transaction, tid, status):
        self._transaction = transaction
        self.changes.tpc_begin(transaction, tid, status)

    @synchronized
    def tpc_finish(self, transaction, func = lambda: None):
        if self._transaction is not transaction:
            return
        self._transaction = None
        self.changes.tpc_finish(transaction)
        self._commit_lock.release()
    
    @synchronized
    def tpc_vote(self, transaction):
        if self._transaction is not transaction:
            return
        return self.changes.tpc_vote(transaction)

    # Gaaaaaa! Work around ZEO bug.
    def modifiedInVersion(self, oid):
        return ''

class ZConfig:

    def __init__(self, config):
        self.config = config
        self.name = config.getSectionName()

    def open(self):
        base = self.config.base.open()
        changes = self.config.changes.open()
        return DemoStorage2(base, changes)
