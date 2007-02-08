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

import logging
from time import time

from zope import interface
from cPickle import dumps
from zope.app.cache.ram import RAMCache, Storage, writelock, caches

from lovely.viewcache.interfaces import IViewCache


class ViewCache(RAMCache):
    interface.implements(IViewCache)

    def set(self, data, ob, key=None,
                            dependencies=None,
                            lifetime=(0, None)):
        logging.debug('Viewcache.set(%r, %r, %r)'% (ob, key, dependencies))
        s = self._getStorage()
        key = self._buildKey(key)
        s.setEntry(ob, key, data, lifetime)
        if dependencies is not None:
            for dep in dependencies:
                try:
                    obs = s.getEntry(dep, None)
                    obs += ((ob, key), )
                except KeyError:
                    obs = ((ob, key), )
                s.setEntry(dep, None, obs, lifetime)

    def invalidate(self, ob=None, key=None, dependencies=None):
        logging.debug('Viewcache.invalidate(%r, %r, %r)'% (
            ob, key, dependencies))
        if dependencies is not None:
            s = self._getStorage()
            if key:
                key =  self._buildKey(key)
            for dep in dependencies:
                try:
                    obs = s.getEntry(dep, None)
                    s.invalidate(dep)
                except KeyError:
                    obs = ()
                for ob, key in obs:
                    s.invalidate(ob, key)
        else:
            #TODO: invalidate dependency-indices
            super(ViewCache, self).invalidate(ob, key)
            
    
    def _getStorage(self):
        "Finds or creates a storage object."
        cacheId = self._cacheId
        writelock.acquire()
        try:
            if cacheId not in caches:
                caches[cacheId] = LifetimeStorage(self.maxEntries, self.maxAge,
                                                  self.cleanupInterval)
            return caches[cacheId]
        finally:
            writelock.release()
            
            
    def getExtendedStatistics(self):
        s = self._getStorage()
        return s.getExtendedStatistics()
        

class LifetimeStorage(Storage):

    def setEntry(self, ob, key, value, lifetime=(0, None)):
        """Stores a value for the object.  Creates the necessary
        dictionaries."""

        if self.lastCleanup <= time() - self.cleanupInterval:
            self.cleanup()

        self.writelock.acquire()
        try:
            if ob not in self._data:
                self._data[ob] = {}

            timestamp = time()
            # [data, ctime, access count, lifetime, Invalidated]
            self._data[ob][key] = [value, timestamp, 0, lifetime, False]
        finally:
            self.writelock.release()
            self._invalidate_queued()

    def _do_invalidate(self, ob, key=None):
        """This does the actual invalidation, but does not handle the locking.

        This method is supposed to be called from `invalidate`
        """
        obEntry = self._data.get(ob, None)
        if obEntry is not None:
            keyEntry = obEntry.get(key, None)
            if keyEntry is not None:
                minTime = keyEntry[3][0]
                lifetime = time() - keyEntry[1]
                if lifetime < minTime:
                    # minimum lifetime not reached, just mark it for removal
                    keyEntry[4]=True
                    return
        try:
            if key is None:
                del self._data[ob]
                self._misses[ob] = 0
            else:
                del self._data[ob][key]
                if not self._data[ob]:
                    del self._data[ob]
        except KeyError:
            pass

    def removeStaleEntries(self):
        "Remove the entries older than `maxAge`"
        punchline = time() - self.maxAge
        self.writelock.acquire()
        try:
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
        finally:
            self.writelock.release()
            self._invalidate_queued()

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
            hits = sum(entry[2] for entry in self._data[ob].itervalues())
            result.append({'path': ob,
                           'key': None,
                           'misses': self._misses.get(ob, 0),
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
                                   'hits': value[2],
                                   'minage': '',
                                   'maxage': '',
                                   'deps': None,
                                   'keys':[]})
        return tuple(result)

    def _getStatisticObjects(self):
        return sorted(self._data.keys())

