##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Network ZODB storage client

XXX support multiple outstanding requests up until the vote?
XXX is_connected() vis ClientDisconnected error
"""
__version__='$Revision: 1.36 $'[11:-2]

import cPickle
import os
import socket
import string
import struct
import sys
import tempfile
import thread
import threading
import time
from types import TupleType, StringType
from struct import pack, unpack

import ExtensionClass, Sync, ThreadLock
import ClientCache
import zrpc2
import ServerStub
from TransactionBuffer import TransactionBuffer

from ZODB import POSException
from ZODB.TimeStamp import TimeStamp
from zLOG import LOG, PROBLEM, INFO, BLATHER
from Exceptions import Disconnected

def log2(type, msg, subsys="ClientStorage %d" % os.getpid()):
    LOG(subsys, type, msg)

try:
    from ZODB.ConflictResolution import ResolvedSerial
except ImportError:
    ResolvedSerial = 'rs'

class ClientStorageError(POSException.StorageError):
    """An error occured in the ZEO Client Storage"""

class UnrecognizedResult(ClientStorageError):
    """A server call returned an unrecognized result"""

class ClientDisconnected(ClientStorageError, Disconnected):
    """The database storage is disconnected from the storage."""

def get_timestamp(prev_ts):
    t = time.time()
    t = apply(TimeStamp, (time.gmtime(t)[:5] + (t % 60,)))
    t = t.laterThan(prev_ts)
    return t

class DisconnectedServerStub:
    """Raise ClientDisconnected on all attribute access."""

    def __getattr__(self, attr):
        raise ClientDisconnected()

disconnected_stub = DisconnectedServerStub()

class ClientStorage:

    def __init__(self, addr, storage='1', cache_size=20000000,
                 name='', client='', debug=0, var=None,
                 min_disconnect_poll=5, max_disconnect_poll=300,
                 wait_for_server_on_startup=0, read_only=0):

        self._server = disconnected_stub
        self._is_read_only = read_only
        self._storage = storage

        self._info = {'length': 0, 'size': 0, 'name': 'ZEO Client',
                      'supportsUndo':0, 'supportsVersions': 0}

        self._tbuf = TransactionBuffer()
        self._db = None
        self._oids = []
        # XXX It's confusing to have _serial, _serials, and _seriald. 
        self._serials = []
        self._seriald = {}

        self._basic_init(name or str(addr))

        # Decide whether to use non-temporary files
        client = client or os.environ.get('ZEO_CLIENT', '')
        self._cache = ClientCache.ClientCache(storage, cache_size,
                                              client=client, var=var)
        self._cache.open() # XXX

        self._rpc_mgr = zrpc2.ConnectionManager(addr, self,
                                                #debug=debug,
                                                tmin=min_disconnect_poll,
                                                tmax=max_disconnect_poll)

        # XXX What if we can only get a read-only connection and we
        # want a read-write connection?  Looks like the current code
        # will block forever.
        
        if wait_for_server_on_startup:
            self._rpc_mgr.connect(sync=1)
        else:
            if not self._rpc_mgr.attempt_connect():
                self._rpc_mgr.connect()

    def _basic_init(self, name):
        """Handle initialization activites of BaseStorage"""

        self.__name__ = name

        # A ClientStorage only allows one client to commit at a time.
        # A client enters the commit state by finding tpc_tid set to
        # None and updating it to the new transaction's id.  The
        # tpc_tid variable is protected by tpc_cond.
        self.tpc_cond = threading.Condition()
        self._transaction = None

        # Prevent multiple new_oid calls from going out.  The _oids
        # variable should only be modified while holding the
        # oid_cond. 
        self.oid_cond = threading.Condition()

        commit_lock = thread.allocate_lock()
        self._commit_lock_acquire = commit_lock.acquire
        self._commit_lock_release = commit_lock.release

        t = time.time()
        t = self._ts = apply(TimeStamp,(time.gmtime(t)[:5]+(t%60,)))
        self._serial = `t`
        self._oid='\0\0\0\0\0\0\0\0'

    def registerDB(self, db, limit):
        """Register that the storage is controlled by the given DB."""
        log2(INFO, "registerDB(%s, %s)" % (repr(db), repr(limit)))
        self._db = db

    def is_connected(self):
        if self._server is disconnected_stub:
            return 0
        else:
            return 1

    def notifyConnected(self, c):
        log2(INFO, "Connected to storage")
        stub = ServerStub.StorageServer(c)

        self._oids = []

        # XXX Why is this synchronous?  If it were async, verification
        # would start faster.
        stub.register(str(self._storage), self._is_read_only)
        self.verify_cache(stub)

        # Don't make the server available to clients until after
        # validating the cache
        self._server = stub

    def verify_cache(self, server):
        server.beginZeoVerify()
        self._cache.verify(server.zeoVerify)
        server.endZeoVerify()

    ### Is there a race condition between notifyConnected and
    ### notifyDisconnected? In Particular, what if we get
    ### notifyDisconnected in the middle of notifyConnected?
    ### The danger is that we'll proceed as if we were connected
    ### without worrying if we were, but this would happen any way if
    ### notifyDisconnected had to get the instance lock.  There's
    ### nothing to gain by getting the instance lock.

    ### Note that we *don't* have to worry about getting connected
    ### in the middle of notifyDisconnected, because *it's*
    ### responsible for starting the thread that makes the connection.

    def notifyDisconnected(self):
        log2(PROBLEM, "Disconnected from storage")
        self._server = disconnected_stub
        if self._transaction:
            self._transaction = None
            self.tpc_cond.notifyAll()
            self.tpc_cond.release()

    def __len__(self):
        return self._info['length']

    def getName(self):
        return "%s (%s)" % (self.__name__, "XXX")

    def getSize(self):
        return self._info['size']
                  
    def supportsUndo(self):
        return self._info['supportsUndo']
    
    def supportsVersions(self):
        return self._info['supportsVersions']

    def supportsTransactionalUndo(self):
        try:
            return self._info['supportsTransactionalUndo']
        except KeyError:
            return 0

    def isReadOnly(self):
        return self._is_read_only

    def _check_trans(self, trans, exc=None):
        if self._transaction is not trans:
            if exc is None:
                return 0
            else:
                raise exc(self._transaction, trans)
        return 1
        
    def _check_tid(self, tid, exc=None):
        # XXX Is all this locking unnecessary?  The only way to
        # begin a transaction is to call tpc_begin().  If we assume
        # clients are single-threaded and well-behaved, i.e. they call
        # tpc_begin() first, then there appears to be no need for
        # locking.  If _check_tid() is called and self.tpc_tid != tid,
        # then there is no way it can be come equal during the call.
        # Thus, there should be no race.
        
        if self.tpc_tid != tid:
            if exc is None:
                return 0
            else:
                raise exc(self.tpc_tid, tid)
        return 1

        # XXX But I'm not sure
        
        self.tpc_cond.acquire()
        try:
            if self.tpc_tid != tid:
                if exc is None:
                    return 0
                else:
                    raise exc(self.tpc_tid, tid)
            return 1
        finally:
            self.tpc_cond.release()

    def abortVersion(self, src, transaction):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        self._check_trans(transaction,
                          POSException.StorageTransactionError)
        oids = self._server.abortVersion(src, self._serial)
        for oid in oids:
            self._tbuf.invalidate(oid, src)
        return oids

    def close(self):
        self._rpc_mgr.close()
        if self._cache is not None:
            self._cache.close()
        
    def commitVersion(self, src, dest, transaction):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        self._check_trans(transaction,
                          POSException.StorageTransactionError)
        oids = self._server.commitVersion(src, dest, self._serial)
        if dest:
            # just invalidate our version data
            for oid in oids:
                self._tbuf.invalidate(oid, src)
        else:
            # dest is '', so invalidate version and non-version
            for oid in oids:
                self._tbuf.invalidate(oid, dest)
        return oids

    def history(self, oid, version, length=1):
        return self._server.history(oid, version, length)     
                  
    def loadSerial(self, oid, serial):
        return self._server.loadSerial(oid, serial)     

    def load(self, oid, version, _stuff=None):
        p = self._cache.load(oid, version)
        if p:
            return p
        if self._server is None:
            raise ClientDisconnected()
        p, s, v, pv, sv = self._server.zeoLoad(oid)
        self._cache.checkSize(0)
        self._cache.store(oid, p, s, v, pv, sv)
        if v and version and v == version:
            return pv, sv
        else:
            if s:
                return p, s
            raise KeyError, oid # no non-version data for this
                    
    def modifiedInVersion(self, oid):
        v = self._cache.modifiedInVersion(oid)
        if v is not None:
            return v
        return self._server.modifiedInVersion(oid)

    def new_oid(self, last=None):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        # We want to avoid a situation where multiple oid requests are
        # made at the same time.
        self.oid_cond.acquire()
        if not self._oids:
            self._oids = self._server.new_oids()
            self._oids.reverse()
            self.oid_cond.notifyAll()
        oid = self._oids.pop()
        self.oid_cond.release()
        return oid
        
    def pack(self, t=None, rf=None, wait=0, days=0):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        # Note that we ignore the rf argument.  The server
        # will provide it's own implementation.
        if t is None:
            t = time.time()
        t = t - (days * 86400)
        return self._server.pack(t, wait)

    def _check_serials(self):
        if self._serials:
            l = len(self._serials)
            r = self._serials[:l]
            del self._serials[:l]
            for oid, s in r:
                if isinstance(s, Exception):
                    raise s
                self._seriald[oid] = s
            return r

    def store(self, oid, serial, data, version, transaction):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        self._check_trans(transaction, POSException.StorageTransactionError)
        self._server.storea(oid, serial, data, version, self._serial) 
        self._tbuf.store(oid, version, data)
        return self._check_serials()

    def tpc_vote(self, transaction):
        if transaction is not self._transaction:
            return
        self._server.vote(self._serial)
        return self._check_serials()
            
    def tpc_abort(self, transaction):
        if transaction is not self._transaction:
            return
        self._server.tpc_abort(self._serial)
        self._tbuf.clear()
        self._seriald.clear()
        del self._serials[:]
        self._transaction = None
        self.tpc_cond.notify()
        self.tpc_cond.release()

    def tpc_begin(self, transaction):
        self.tpc_cond.acquire()
        while self._transaction is not None:
            if self._transaction == transaction:
                self.tpc_cond.release()
                return
            self.tpc_cond.wait()

        if self._server is None:
            self.tpc_cond.release()
            raise ClientDisconnected()
            
        self._ts = get_timestamp(self._ts)
        id = `self._ts`
        self._transaction = transaction

        try:
            r = self._server.tpc_begin(id,
                                       transaction.user,
                                       transaction.description,
                                       transaction._extension)
        except:
            # If _server is None, then the client disconnected during
            # the tpc_begin() and notifyDisconnected() will have
            # released the lock.
            if self._server is not disconnected_stub:
                self.tpc_cond.release()
            raise

        self._serial = id
        self._seriald.clear()
        del self._serials[:]

    def tpc_finish(self, transaction, f=None):
        if transaction is not self._transaction:
            return
        if f is not None: # XXX what is f()?
            f()

        self._server.tpc_finish(self._serial)

        r = self._check_serials()
        assert r is None or len(r) == 0, "unhandled serialnos: %s" % r

        self._update_cache()

        self._transaction = None
        self.tpc_cond.notify()
        self.tpc_cond.release()

    def _update_cache(self):
        # Iterate over the objects in the transaction buffer and
        # update or invalidate the cache. 
        self._cache.checkSize(self._tbuf.get_size())
        self._tbuf.begin_iterate()
        while 1:
            try:
                t = self._tbuf.next()
            except ValueError, msg:
                raise ClientStorageError, (
                    "Unexpected error reading temporary file in "
                    "client storage: %s" % msg)
            if t is None:
                break
            oid, v, p = t
            if p is None: # an invalidation 
                s = None
            else:
                s = self._seriald[oid]
            if s == ResolvedSerial or s is None:
                self._cache.invalidate(oid, v)
            else:
                self._cache.update(oid, s, v, p)
        self._tbuf.clear()

    def transactionalUndo(self, trans_id, trans):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        self._check_trans(trans, POSException.StorageTransactionError)
        oids = self._server.transactionalUndo(trans_id, self._serial)
        for oid in oids:
            self._tbuf.invalidate(oid, '')
        return oids

    def undo(self, transaction_id):
        if self._is_read_only:
            raise POSException.ReadOnlyError()
        # XXX what are the sync issues here?
        oids = self._server.undo(transaction_id)
        for oid in oids:
            self._cache.invalidate(oid, '')                
        return oids

    def undoInfo(self, first=0, last=-20, specification=None):
        return self._server.undoInfo(first, last, specification)

    def undoLog(self, first, last, filter=None):
        if filter is not None:
            return () # XXX can't pass a filter to server
        
        return self._server.undoLog(first, last) # Eek!

    def versionEmpty(self, version):
        return self._server.versionEmpty(version)

    def versions(self, max=None):
        return self._server.versions(max)

    # below are methods invoked by the StorageServer

    def serialno(self, arg):
        self._serials.append(arg)

    def info(self, dict):
        self._info.update(dict)

    def begin(self):
        self._tfile = tempfile.TemporaryFile()
        self._pickler = cPickle.Pickler(self._tfile, 1)
        self._pickler.fast = 1 # Don't use the memo

    def invalidate(self, args):
        if self._pickler is None:
            return
        self._pickler.dump(args)

    def end(self):
        if self._pickler is None:
            return
        self._pickler.dump((0,0))
##        self._pickler.dump = None
        self._tfile.seek(0)
        unpick = cPickle.Unpickler(self._tfile)
        self._tfile = None

        while 1:
            oid, version = unpick.load()
            if not oid:
                break
            self._cache.invalidate(oid, version=version)
            self._db.invalidate(oid, version=version)

    def Invalidate(self, args):
        # XXX _db could be None
        for oid, version in args:
            self._cache.invalidate(oid, version=version)
            try:
                self._db.invalidate(oid, version=version)
            except AttributeError, msg:
                log2(PROBLEM,
                    "Invalidate(%s, %s) failed for _db: %s" % (repr(oid),
                                                               repr(version),
                                                               msg))
                    
