##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

from cPickle import dumps
from time import time
from threading import Lock

import persistent

from BTrees.Length import Length
from persistent.list import PersistentList
from BTrees.OOBTree import OOBTree
from ZODB.interfaces import IDatabase

from zope import interface
from zope import component

from zope.app.cache.ram import Storage

from ram import ViewCache as RAMViewCache

from lovely.mount.root import DBRoot
from lovely.viewcache.interfaces import IZODBViewCache


class ViewCache(RAMViewCache):
    interface.implements(IZODBViewCache)

    mountpoint = None

    def __init__(self, dbName=''):
        self.dbName = dbName
        super(ViewCache, self).__init__()

    def _getStorage(self):
        "Finds or creates a storage object."
        if self.mountpoint is None:
            self.mountpoint = DBRoot(str(self.dbName))
        if self.dbName != self.mountpoint.dbName:
            self.mountpoint.dbName = str(self.dbName)
        if self.__name__ not in self.mountpoint:
            storage = PersistentStorage(
                self.maxEntries, self.maxAge, self.cleanupInterval)
            self.mountpoint[self.__name__] = storage
        return self.mountpoint[self.__name__]


class PersistentStorage(persistent.Persistent):
    """A storage for ViewCache using ZODB.

    Storage keeps the count and does the aging and cleanup of cached
    entries.

    This object is shared between threads.  It corresponds to a single
    persistent `RAMCache` object.  Storage does the locking necessary
    for thread safety.
    """

    def __init__(self, maxEntries=1000, maxAge=3600, cleanupInterval=300):
        self.invalidateAll()
        self.maxEntries = maxEntries
        self.maxAge = maxAge
        self.cleanupInterval = cleanupInterval
        self.lastCleanup = time()

    def update(self, maxEntries=None, maxAge=None, cleanupInterval=None):
        """Set the registration options.

        ``None`` values are ignored.
        """
        if maxEntries is not None:
            self.maxEntries = maxEntries
        if maxAge is not None:
            self.maxAge = maxAge
        if cleanupInterval is not None:
            self.cleanupInterval = cleanupInterval

    def getEntry(self, ob, key):
        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()
        try:
            data = self._data[ob][key]
        except KeyError:
            if ob not in self._misses:
                self._misses[ob] = Length()
            self._misses[ob].change(1)
            raise
        else:
            #NOTE: hit count is deactivated because of too many database writes
            #data[2].change(1)
            return data[0]

    def setEntry(self, ob, key, value, lifetime=(0, None)):
        """Stores a value for the object.  Creates the necessary
        dictionaries."""
        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()
        if ob not in self._data:
            self._data[ob] = OOBTree()
        timestamp = time()
        # [data, ctime, access count, lifetime, Invalidated]
        self._data[ob][key] = PersistentList(
                [value, timestamp, Length(), lifetime, False])

    def invalidate(self, ob, key=None):
        """Drop the cached values.

        Drop all the values for an object if no key is provided or
        just one entry if the key is provided.
        """
        try:
            if key is None:
                del self._data[ob]
                self._misses[ob] = Length()
            else:
                del self._data[ob][key]
                if not self._data[ob]:
                    del self._data[ob]
        except KeyError:
            pass

    def invalidateAll(self):
        """Drop all the cached values.
        """
        self._data = OOBTree()
        self._misses = OOBTree()

    def removeStaleEntries(self):
        "Remove the entries older than `maxAge`"
        punchline = time() - self.maxAge
        data = self._data
        for object, dict in data.items():
            for ob, key in dict.items():
                minTime = key[3][0]
                lifetime = time() - key[1]
                if lifetime < minTime:
                    # minimum lifetime not reached, do not remove it
                    continue
                lifetime = time() - key[1]
                if (   key[4]
                    or (    self.maxAge > 0
                        and key[1] < punchline
                       )
                    or (   key[3][1] is not None
                        and key[3][1] < lifetime
                       )
                   ):
                    # invalidation flag set or maxAge reached
                    del dict[ob]
                    if not dict:
                        del data[object]

    def cleanup(self):
        "Cleanup the data"
        self.removeStaleEntries()
        self.removeLeastAccessed()

    def removeLeastAccessed(self):
        ""
        data = self._data
        keys = [(ob, k) for ob, v in data.iteritems() for k in v]

        if len(keys) > self.maxEntries:
            def getKey(item):
                ob, key = item
                return data[ob][key]
            keys=sorted([v for v in keys], key=getKey)

            ob, key = keys[self.maxEntries]
            maxDropCount = data[ob][key][2]()

            keys.reverse()

            for ob, key in keys:
                if data[ob][key][2]() <= maxDropCount:
                    del data[ob][key]
                    if not data[ob]:
                        del data[ob]

            self._clearAccessCounters()

    def _clearAccessCounters(self):
        for dict in self._data.itervalues():
            for val in dict.itervalues():
                val[2].set(0)
        for k in self._misses.values():
            k.set(0)

    def getKeys(self, object):
        return self._data[object].keys()

    def getStatistics(self):
        "Basically see IRAMCache"
        objects = list(self._data.keys())
        objects.sort()
        result = []

        for ob in objects:
            size = len(dumps(self._data[ob]))
            hits = sum(entry[2]() for entry in self._data[ob].itervalues())
            if ob in self._misses:
                misses = self._misses[ob]()
            else:
                misses = 0
            result.append({'path': ob,
                           'hits': hits,
                           'misses': misses,
                           'size': size,
                           'entries': len(self._data[ob])})
        return tuple(result)

    def getExtendedStatistics(self):
        "Basically see IRAMCache"
        result = []
        for ob in self._getStatisticObjects():
            # use min and maxage for first cache entry (one is always present)
            minage =  self._data[ob].values()[0][3][0] #damn complicating!
            maxage =  self._data[ob].values()[0][3][1] or self.maxAge #damn complicating!
            #the size of all cached values of all subkeys as pickeled in zodb
            totalsize = len(dumps(self._data[ob]))
            deps = []
            for dep in self._data.keys():
                for cacheentry in self._data[dep].values():
                    if str(ob) in cacheentry[0]:
                        #dependency cache entries have a list of dependen objects in val[0]
                        deps.append(dep)
            hits = sum(entry[2]() for entry in self._data[ob].itervalues())
            if ob in self._misses:
                misses = self._misses[ob]()
            else:
                misses = 0
            result.append({'path': ob,
                           'key': None,
                           'misses': misses,
                           'size': totalsize,
                           'entries': len(self._data[ob]),
                           'hits': hits,
                           'minage': minage,
                           'maxage': maxage,
                           'deps': deps,
                           'keys': []})
            pathObj = result[-1]

            for key, value in self._data[ob].items():
                if key is not None:
                    pathObj['keys'].append({'path': ob,
                                   'key': key,
                                   'misses': '',
                                   'size': len(dumps(value)),
                                   'entries': '',
                                   'hits': value[2](),
                                   'minage': '',
                                   'maxage': '',
                                   'deps': None,
                                   'keys':[]})
        return tuple(result)

    def _getStatisticObjects(self):
        return sorted(list(self._data.keys()))

