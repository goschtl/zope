##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: RAMCache.py,v 1.1 2002/10/31 16:01:39 alga Exp $
"""
from Persistence import Persistent
from Zope.App.Caching.RAMCache.IRAMCache import IRAMCache
from Zope.ComponentArchitecture.IPresentation import IPresentation
from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from time import time
from thread import allocate_lock
from Zope.ComponentArchitecture import getAdapter

# A global caches dictionary shared between threads
caches = {}

# A writelock for caches dictionary
writelock = allocate_lock()

class RAMCache(Persistent):
    """RAM Cache

    The design of this class is heavily based on RAMCacheManager in
    Zope2.

    The idea behind the RAMCache is that it should be shared between
    threads, so that the same objects are not cached in each thread.
    This is achieved by storing the cache data structure itself as a
    module level variable (RAMCache.caches).  This, of course,
    requires locking on modifications of that data structure.

    RAMCache is a persistent object.  The actual data storage is a
    volatile object, which can be acquired/created by calling
    _getStorage().  Storage objects are shared between threads and
    handle their blocking internally.
    """

    __implements__ = IRAMCache

    def __init__(self):
        self._cacheId = "%s_%f" % (id(self), time())
        self.requestVars = ()
        self.maxEntries = 1000
        self.maxAge = 3600
        self.cleanupInterval = 300

    def getStatistics(self):
        "See Zope.App.Caching.RAMCache.IRAMCache.IRAMCache"

    def update(self, requestVars=None, maxEntries=None, maxAge=None,
               cleanupInterval=None):
        "See Zope.App.Caching.RAMCache.IRAMCache.IRAMCache"
        
        if requestVars is not None:
            self.requestVars = requestVars

        if maxEntries is not None:
            self.maxEntries = maxEntries

        if maxAge is not None:
            self.maxAge = maxAge

        if cleanupInterval is not None:
            self.cleanupInterval = cleanupInterval

        self._getStorage().update(maxEntries, maxAge, cleanupInterval)


    def invalidate(self, ob, view_name=None, keywords=None):
        "See Zope.App.Caching.ICache.ICache"
        locatable = getAdapter(ob, IPhysicallyLocatable)
        location = locatable.getPhysicalPath()
        if keywords:
            items = keywords.items()
            items.sort()
            keywords = tuple(items)
        s = self._getStorage()
        if view_name is None:
            s.invalidate(location)
        else:
            keys = s.getKeys(location)
            for key in keys:
                view, req, kw = key
                if view == view_name:
                    
                    if keywords is None or keywords == kw:
                        s.invalidate(location, key)
                        
    def query(self, ob, view_name='', keywords=None, default=None):
        "See Zope.App.Caching.ICache.ICache"
        s = self._getStorage()
        locatable = getAdapter(ob, IPhysicallyLocatable)
        location = locatable.getPhysicalPath()
        key = self._buildKey(view_name, RAMCache._getRequest(ob),
                             self.requestVars, keywords)
        try:
            return s.getEntry(location, key)
        except:
            return default

    def set(self, data, ob, view_name='', keywords=None):
        "See Zope.App.Caching.ICache.ICache"
        s = self._getStorage()
        locatable = getAdapter(ob, IPhysicallyLocatable)
        location = locatable.getPhysicalPath()
        key = self._buildKey(view_name, RAMCache._getRequest(ob),
                             self.requestVars, keywords)
        s.setEntry(location, key, data)

    def _getRequest(ob):
        request = None
        if IPresentation.isImplementedBy(ob):
            request = ob.request
        return request
    
    _getRequest = staticmethod(_getRequest)

    def _getStorage(self):
        "Finds or creates a storage object."

        global caches
        global writelock
        cacheId = self._cacheId
        writelock.acquire()
        try:
            if not caches.has_key(cacheId):
                caches[cacheId] = Storage(self.maxEntries, self.maxAge,
                                          self.cleanupInterval)
                self._v_storage = caches[cacheId]
        finally:
            writelock.release()
        return self._v_storage

    def _buildKey(view_name, req, req_names, kw):
        "Build a tuple which can be used as an index for a cached value"

        req_vars = ()
        if req:
            for key in req_names:
                try:
                    value = req[key]
                    req_vars += (key, value)
                except KeyError:
                    pass

        kw_vars = ()
        if kw:
            items = kw.items()
            items.sort()
            kw_vars = tuple(items)
                
        return (view_name, req_vars, kw_vars)

    _buildKey = staticmethod(_buildKey)

    def notify(self, event):
        """See Zope.Event.ISubscriber

        This method receives ObjectModified events and invalidates
        cached entries for the objects that raise them.
        """

        try:
            locatable = getAdapter(event.object, IPhysicallyLocatable)
            location = locatable.getPhysicalPath()
            self._getStorage().invalidate(location)
        except:
            pass


class Storage:
    """Storage.

    Storage keeps the count and does the aging and cleanup of cached
    entries.

    This object is shared between threads.  It corresponds to a single
    persistent RAMCache object.  Storage does the locking necessary
    for thread safety.

    """

    def __init__(self, maxEntries=1000, maxAge=3600, cleanupInterval=300):
        self._data = {}
        self._invalidate_queue = []
        self.maxEntries = maxEntries
        self.maxAge = maxAge
        self.cleanupInterval = cleanupInterval
        self.writelock = allocate_lock()
        self.lastCleanup = time()

    def update(self, maxEntries=None, maxAge=None, cleanupInterval=None):
        """Set the configuration options.

        None values are ignored.
        """
        if maxEntries is not None:
            self.maxEntries = maxEntries

        if maxAge is not None:
            self.maxAge = maxAge

        if cleanupInterval is not None:
            self.cleanupInterval = cleanupInterval

    def getEntry(self, ob, key):
        data = self._data[ob][key]
        data[2] += 1                    # increment access count
        return data[0]


    def setEntry(self, ob, key, value):
        """Stores a value for the object.  Creates the necessary
        dictionaries."""

        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()
            
        self.writelock.acquire()
        try:
            if ob not in self._data:
                self._data[ob] = {}

            timestamp = time()
            # [data, ctime, access count]
            self._data[ob][key] = [value, timestamp, 0]
        finally:
            self.writelock.release()
            self._invalidate_queued()
            
    def _do_invalidate(self, ob, key=None):
        """This does the actual invalidation, but does not handle the locking.
        
        This method is supposed to be called from invalidate()
        """
        try:
            if key is None:
                del self._data[ob]
            else:
                del self._data[ob][key]
                if len(self._data[ob]) < 1:
                    del self._data[ob]
        except KeyError:
            pass

    def _invalidate_queued(self):
        """This method should be called after each writelock release."""

        while len(self._invalidate_queue):
            obj, key = self._invalidate_queue.pop()
            self.invalidate(obj, key)
        
    def invalidate(self, ob, key=None):
        """Drop the cached values.

        Drop all the values for an object if no key is provided or
        just one entry if the key is provided.

        """
        if self.writelock.acquire(0):
            try:
                self._do_invalidate(ob, key)
            finally:
                self.writelock.release()
                # self._invalidate_queued() not called to avoid a recursion
        else:
            self._invalidate_queue.append((ob,key))


    def removeStaleEntries(self):
        "Remove the entries older than maxAge"

        if self.maxAge > 0:
            punchline = time() - self.maxAge
            self.writelock.acquire()
            try:
                for object, dict in self._data.items():
                    for key, val in self._data[object].items():
                        if self._data[object][key][1] < punchline:
                            del self._data[object][key]
                            if len(self._data[object]) < 1:
                                del self._data[object]
            finally:
                self.writelock.release()
                self._invalidate_queued()

    def cleanup(self):
        "Cleanup the data"
        self.removeStaleEntries()
        self.removeLeastAccessed()

    def removeLeastAccessed(self):
        ""

        self.writelock.acquire()
        try:
            keys = []
            for ob in self._data:
                for key in self._data[ob]:
                    keys.append((ob, key))

            if len(keys) > self.maxEntries:
                def cmpByCount(x,y):
                    ob1, key1 = x
                    ob2, key2 = y
                    return cmp(self._data[ob1][key1],
                               self._data[ob2][key2])
                keys.sort(cmpByCount)

                ob, key = keys[self.maxEntries]
                maxDropCount = self._data[ob][key][2] 

                keys.reverse()

                for ob, key in keys:
                    if self._data[ob][key][2] <= maxDropCount:
                        del self._data[ob][key]
                        if len(self._data[ob]) < 1:
                            del self._data[ob]

                self._clearAccessCounters()
        finally:
            self.writelock.release()
            self._invalidate_queued()
            
    def _clearAccessCounters(self):
        for ob in self._data:
            for key in self._data[ob]:
                self._data[ob][key][2] = 0


    def getKeys(self, object):
        return self._data[object].keys()


__doc__ = RAMCache.__doc__ + __doc__
