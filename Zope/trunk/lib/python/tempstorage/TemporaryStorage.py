##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
A storage implementation which uses RAM to persist objects, much like
MappingStorage.  Unlike MappingStorage, it needs not be packed to get rid of
non-cyclic garbage and it does rudimentary conflict resolution.  This is a
ripoff of Jim's Packless bsddb3 storage.

$Id: TemporaryStorage.py,v 1.1.2.2 2004/05/16 01:41:34 chrism Exp $
"""

__version__ ='$Revision: 1.1.2.2 $'[11:-2]

from zLOG import LOG, BLATHER
from ZODB.serialize import referencesf
from ZODB import POSException
from ZODB.BaseStorage import BaseStorage
from ZODB.ConflictResolution import ConflictResolvingStorage, ResolvedSerial
import time

# keep old object revisions for CONFLICT_CACHE_MAXAGE seconds
CONFLICT_CACHE_MAXAGE = 60
# garbage collect conflict cache every CONFLICT_CACHE_GCEVERY seconds
CONFLICT_CACHE_GCEVERY = 60
# keep history of recently gc'ed oids of length RECENTLY_GC_OIDS_LEN
RECENTLY_GC_OIDS_LEN = 200

class ReferenceCountError(POSException.POSError):
    """ An error occured while decrementing a reference to an object in
    the commit phase. The object's reference count was below zero."""

class TemporaryStorageError(POSException.POSError):
    """ A Temporary Storage exception occurred.  This probably indicates that
    there is a low memory condition or a tempfile space shortage.  Check
    available tempfile space and RAM consumption and restart the server
    process."""

class TemporaryStorage(BaseStorage, ConflictResolvingStorage):

    def __init__(self, name='TemporaryStorage'):
        """
        index -- mapping of oid to current serial
        referenceCount -- mapping of oid to count
        oreferences -- mapping of oid to a sequence of its referenced oids
        opickle -- mapping of oid to pickle
        _tmp -- used by 'store' to collect changes before finalization
        _conflict_cache -- cache of recently-written object revisions
        _last_cache_gc -- last time that conflict cache was garbage collected
        _recently_gc_oids -- a queue of recently gc'ed oids
        """
        BaseStorage.__init__(self, name)

        self._index={}
        self._referenceCount={}
        self._oreferences={}
        self._opickle={}
        self._tmp = []
        self._conflict_cache = {}
        self._last_cache_gc = 0
        self._recently_gc_oids = [None for x in range (RECENTLY_GC_OIDS_LEN)]
        self._oid = '\0\0\0\0\0\0\0\0'

    def __len__(self):
        return len(self._index)

    def getSize(self):
        return 0

    def _clear_temp(self):
        now = time.time()
        if now > (self._last_cache_gc + CONFLICT_CACHE_GCEVERY):
            for k, v in self._conflict_cache.items():
                data, t = v
                if now > (t + CONFLICT_CACHE_MAXAGE):
                    del self._conflict_cache[k]
            self._last_cache_gc = now
        self._tmp = []

    def close(self):
        """
        Close the storage
        """

    def load(self, oid, version):
        self._lock_acquire()
        try:
            try:
                s=self._index[oid]
                p=self._opickle[oid]
                return p, s # pickle, serial
            except KeyError:
                # this oid was probably garbage collected while a thread held
                # on to an object that had a reference to it; we can probably
                # force the loader to sync their connection by raising a
                # ConflictError (at least if Zope is the loader, because it
                # will resync its connection on a retry).  This isn't
                # perfect because the length of the recently gc'ed oids list
                # is finite and could be overrun through a mass gc, but it
                # should be adequate in common-case usage.
                if oid in self._recently_gc_oids:
                    raise POSException.ConflictError(oid=oid)
                else:
                    raise
        finally:
            self._lock_release()

    def loadSerial(self, oid, serial, marker=[]):
        """ this is only useful to make conflict resolution work.  It
        does not actually implement all the semantics that a revisioning
        storage needs! """
        self._lock_acquire()
        try:
            data = self._conflict_cache.get((oid, serial), marker)
            if data is marker:
                # XXX Need 2 serialnos to pass them to ConflictError--
                # the old and the new
                raise POSException.ConflictError(oid=oid)
            else:
                return data[0] # data here is actually (data, t)
        finally:
            self._lock_release()

    def store(self, oid, serial, data, version, transaction):
        if transaction is not self._transaction:
            raise POSException.StorageTransactionError(self, transaction)
        if version:
            # we allow a version to be in use although we don't
            # support versions in the storage.
            LOG('TemporaryStorage', BLATHER,
                ('versions in use with TemporaryStorage although Temporary'
                 'Storage doesnt support versions'),
                )
        self._lock_acquire()
        try:
            if self._index.has_key(oid):
                oserial=self._index[oid]
                if serial != oserial:
                    newdata = self.tryToResolveConflict(
                        oid, oserial, serial, data)
                    if not newdata:
                        raise POSException.ConflictError(
                            oid=oid,
                            serials=(oserial, serial),
                            data=data)
                    else:
                        data = newdata
            else:
                oserial = serial
            newserial=self._tid
            self._tmp.append((oid, data))
            now = time.time()
            self._conflict_cache[(oid, newserial)] = data, now
            return serial == oserial and newserial or ResolvedSerial
        finally:
            self._lock_release()

    def _finish(self, tid, u, d, e):
        zeros={}
        referenceCount=self._referenceCount
        referenceCount_get=referenceCount.get
        oreferences=self._oreferences
        serial=self._tid
        index=self._index
        opickle=self._opickle

        # iterate over all the objects touched by/created within this
        # transaction
        for entry in self._tmp:
            oid, data = entry[:]
            referencesl=[]
            referencesf(data, referencesl)
            references={}
            for roid in referencesl:
                references[roid]=1
            referenced=references.has_key

            # Create a reference count for this object if one
            # doesn't already exist
            if referenceCount_get(oid) is None:
                referenceCount[oid] = 0
                #zeros[oid]=1

            # update references that are already associated with this
            # object
            roids = oreferences.get(oid, [])
            for roid in roids:
                if referenced(roid):
                    # still referenced, so no need to update
                    # remove it from the references dict so it doesn't
                    # get "added" in the next clause
                    del references[roid]
                else:
                    # Delete the stored ref, since we no longer
                    # have it
                    oreferences[oid].remove(roid)
                    # decrement refcnt:
                    rc = referenceCount_get(roid, 1)
                    rc=rc-1
                    if rc < 0:
                        # This should never happen
                        raise ReferenceCountError, (
                            "%s (Oid %s had refcount %s)" %
                            (ReferenceCountError.__doc__,`roid`,rc)
                            )
                    referenceCount[roid] = rc
                    if rc==0:
                        zeros[roid]=1

            # Create a reference list for this object if one
            # doesn't already exist
            if oreferences.get(oid) is None:
                oreferences[oid] = []

            # Now add any references that weren't already stored
            for roid in references.keys():
                oreferences[oid].append(roid)
                # Create/update refcnt
                rc=referenceCount_get(roid, 0)
                if rc==0 and zeros.get(roid) is not None:
                    del zeros[roid]
                referenceCount[roid] = rc+1

            index[oid] =  serial
            opickle[oid] = data

        if zeros:
            for oid in zeros.keys():
                if oid == '\0\0\0\0\0\0\0\0': continue
                self._takeOutGarbage(oid)

        self._tmp = []

    def _takeOutGarbage(self, oid):
        # take out the garbage.
        referenceCount=self._referenceCount
        referenceCount_get=referenceCount.get

        self._recently_gc_oids.pop()
        self._recently_gc_oids.insert(0, oid)

        try: del referenceCount[oid]
        except: pass
        try: del self._opickle[oid]
        except: pass
        try: del self._index[oid]
        except: pass

        # remove this object from the conflict cache if it exists there
        for k in self._conflict_cache.keys():
            if k[0] == oid:
                del self._conflict_cache[k]

        # Remove/decref references
        roids = self._oreferences.get(oid, [])
        while roids:
            roid = roids.pop(0)
            # decrement refcnt:
            rc=referenceCount_get(roid, 0)
            if rc==0:
                self._takeOutGarbage(roid)
            elif rc < 0:
                raise ReferenceCountError, (
                    "%s (Oid %s had refcount %s)" %
                    (ReferenceCountError.__doc__,`roid`,rc)
                    )
            else:
                referenceCount[roid] = rc - 1
        try: del self._oreferences[oid]
        except: pass

    def pack(self, t, referencesf):
        self._lock_acquire()
        try:
            rindex={}
            referenced=rindex.has_key
            rootl=['\0\0\0\0\0\0\0\0']

            # mark referenced objects
            while rootl:
                oid=rootl.pop()
                if referenced(oid): continue
                p = self._opickle[oid]
                referencesf(p, rootl)
                rindex[oid] = None

            # sweep unreferenced objects
            for oid in self._index.keys():
                if not referenced(oid):
                    self._takeOutGarbage(oid)
        finally:
            self._lock_release()
