##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
from time import time
from sys import getrefcount
from weakref import ref

from persistence.interfaces import ICache

class Cache(object):

    __implements__ = ICache

    def __init__(self, size=500, inactive=300):
        self.__ghosts = {}
        self.__gget = self.__ghosts.get
        self.__active = {}
        self.__aget = self.__active.get
        self._size = size
        self._inactive = inactive

    def __getitem__(self, oid):
        o = self.__gget(oid, self)
        if o is self:
            o = self.__active[oid]
        o=o()
        if o is None:
            raise KeyError, oid
        else:
            return o

    def get(self, oid, default=None):
        o = self.__gget(oid, None)
        if o is None:
            o = self.__active.get(oid, None)
            if o is None:
                return default
        o = o()
        if o is None:
            return default
        else:
            return o

    def __setitem__(self, oid, obj):
        if obj._p_changed is None:
            # ghost
            self.__ghosts[oid] = ref(obj, _dictdel(oid, self.__ghosts))
        else:
            self.__active[oid] = ref(obj, _dictdel(oid, self.__active))

    def __delitem__(self, oid):
        # XXX is there any way to know which dict the key is in?
        try:
            del self.__ghosts[oid]
        except KeyError:
            pass
        try:
            del self.__active[oid]
        except KeyError:
            pass

    def __len__(self):
        return len(self.__ghosts) + len(self.__active)

    def setstate(self, oid, object):
        try:
            del self.__ghosts[oid]
        except KeyError:
            pass
        self.__active[oid] = ref(object, _dictdel(oid, self.__active))

    def incrgc(self):
        na = len(self.__active)
        if na < 1:
            return

        now = int(time() % 86400)

        # Implement a trivial LRU cache by sorting the items by
        # access time and trundling over the last until we've reached
        # out target.  The number of objects in the cache should
        # be relatively small (thousands) so the memory for the
        # list is pretty minimal.
        L = []
        for oid, ob in self.__active.iteritems():
            if ob is not None:
                ob = ob()
            L.append((ob._p_atime, oid, ob))
        L.sort()

        if na > self._size:
            # If the cache is full, ghostify everything up to the cache
            # limit.
            n = na - self._size
            must_go = L[:n]
            L = L[n:]
            for atime, oid, ob in L:
                self._ghostify(oid, ob)

        # ghostify old objects regardless of cache size
        stop_at = now - self._inactive
        for atime, oid, ob in L:
            if atime > stop_at:
                break
            self._ghostify(oid, ob)

    def _ghostify(self, oid, ob):
        ob._p_deactivate()
        if ob._p_changed == None:
            del self.__active[oid]
            self.__ghosts[oid] = ref(ob, _dictdel(oid, self.__ghosts))

    def invalidate(self, oid):
        ob = self.__aget(oid)
        if ob is None:
            return
        ob = ob()
        del ob._p_changed
        del self.__active[oid]
        self.__ghosts[oid] = ref(ob, _dictdel(oid, self.__ghosts))

    def invalidateMany(self, oids):
        if oids is None:
            oids = self.__active.keys()
        for oid in oids:
            self.invalidate(oid)

    def clear(self):
        for oid in self.__active.keys():
            self.invalidate(oid)

    def statistics(self):
        return {
            'ghosts': len(self.__ghosts),
            'active': len(self.__active),
            }

class _dictdel(object):

    __slots__ = 'oid', 'dict'

    def __init__(self, oid, dict):
        self.oid, self.dict = oid, dict

    def __call__(self, ref):
        del self.dict[self.oid]
