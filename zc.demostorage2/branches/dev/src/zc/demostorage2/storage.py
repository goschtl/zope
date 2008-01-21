##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Demo storage that stores changes in a file storage

$Id$
"""

import threading

import ZODB.POSException
from ZODB.utils import p64, u64, z64

from demostorage2.synchronized import synchronized

class DemoStorage2:

    def __init__(self, base, changes):
        self.changes = changes
        self.base = base

        self.getName = changes.getName
        self.sortKey = changes.sortKey
        self.getSize = changes.getSize
        self.__len__ = changes.__len__
        self.supportsUndo = changes.supportsUndo
        self.supportsTransactionalUndo = changes.supportsTransactionalUndo
        self.undo = changes.undo
        self.undoLog = changes.undoLog
        self.undoInfo = changes.undoInfo
    
        self._oid = max(u64(changes.new_oid()), 1l << 63)
        self._lock = threading.RLock()
        self._commit_lock = threading.Lock()

        self._transaction = None

    def registerDB(self, db, limit):
        self.base.registerDB(db, limit)
        self.changes.registerDB(db, limit)

    def close(self):
        self.base.close()
        self.changes.close()

    def load(self, oid, version):
        try:
            return self.changes.load(oid, version)
        except ZODB.POSException.POSKeyError:
            return self.base.load(oid, version)
    load = synchronized(load)

    def getSerial(self, oid):
        return self.load(oid, '')[1]

    def loadSerial(self, oid, serial):
        try:
            return self.changes.loadSerial(oid, serial)
        except ZODB.POSException.POSKeyError:
            return self.base.loadSerial(oid, serial)
    loadSerial = synchronized(loadSerial)

    def new_oid(self):
        self._oid += 1
        return p64(self._oid)
    new_oid = synchronized(new_oid)

    def tpc_begin(self, transaction, tid=None, status=' '):
        if self._transaction is transaction:
            return
        self._commit_lock.acquire()
        self._begin(transaction, tid, status)

    def _begin(self, transaction, tid, status):
        self._transaction = transaction
        self.changes.tpc_begin(transaction, tid, status)
    _begin = synchronized(_begin)

    def tpc_abort(self, transaction):
        if self._transaction is not transaction:
            return
        self._transaction = None
        try:
            self.changes.tpc_abort(transaction)
        finally:
            self._commit_lock.release()
    tpc_abort = synchronized(tpc_abort)

    def store(self, oid, serial, data, version, transaction):
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        if version:
            raise ValueError("Invalid version", version)

        # See if we already have changes for this oid
        try:
            old = self.changes.getSerial(oid)
        except ZODB.POSException.POSKeyError:
            try:
                old = self.base.getSerial(oid)
            except ZODB.POSException.POSKeyError:
                old = serial
                
        if old != serial:
            raise ZODB.POSException.ConflictError(
                oid=oid, serials=(oserial, serial))

        return self.changes.store(oid, serial, data, '', transaction)
    store = synchronized(store)

    def supportsVersions(self):
        return False

    def tpc_vote(self, transaction):
        if self._transaction is not transaction:
            return
        return self.changes.tpc_vote(transaction)
    tpc_vote = synchronized(tpc_vote)

    def tpc_finish(self, transaction, func = lambda: None):
        if self._transaction is not transaction:
            return
        self._transaction = None
        self.changes.tpc_finish(transaction)
        self._commit_lock.release()
    tpc_finish = synchronized(tpc_finish)

    def history(self, *args, **kw):
        return self.changes.history(*args, **kw)

    def lastTransaction(self):
        t = self.changes.lastTransaction()
        if t == z64:
            t = self.base.lastTransaction()
        return t
    lastTransaction = synchronized(lastTransaction)

    def isReadOnly(self):
        return False

    def versionEmpty(*args, **kw):
        return True

    def modifiedInVersion(*args, **kw):
        return ''

    def versions(*args, **kw):
        return ()
