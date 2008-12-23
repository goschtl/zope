##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""zc.dict -- A BTree based persistent mapping

$Id$
"""
import copy

import BTrees
import BTrees.Length
import persistent
import zc.blist


class Dict(persistent.Persistent):
    """A BTree-based dict-like persistent object that can be safely
    inherited from.
    """

    def __init__(self, *args, **kwargs):
        self._data = BTrees.OOBTree.OOBTree()
        self._len = BTrees.Length.Length()
        if args or kwargs:
            self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        delta = 1
        if key in self._data:
            delta = 0
        self._data[key] = value
        if delta:
            self._len.change(delta)

    def __delitem__(self, key):
        self.pop(key)

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError(
                    'update expected at most 1 arguments, got %d' %
                    (len(args),))
            if getattr(args[0], 'keys', None):
                for k in args[0].keys():
                    self[k] = args[0][k]
            else:
                for k, v in args[0]:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def setdefault(self, key, failobj=None):
        # we can't use BTree's setdefault because then we don't know to
        # increment _len
        try:
            res = self._data[key]
        except KeyError:
            res = failobj
            self[key] = res
        return res

    def pop(self, key, *args):
        try:
            res = self._data.pop(key)
        except KeyError:
            if args:
                res = args[0]
            else:
                raise
        else:
            self._len.change(-1)
        return res

    def clear(self):
        self._data.clear()
        self._len.set(0)

    def __len__(self):
        return self._len()

    def keys(self):
        return list(self._data.keys())

    def values(self):
        return list(self._data.values())

    def items(self):
        return list(self._data.items())

    def copy(self):
        if self.__class__ is Dict:
            return Dict(self._data)
        data = self._data
        try:
            self._data = BTrees.OOBTree.OOBTree()
            c = copy.copy(self)
        finally:
            self._data = data
        c.update(self._data)
        return c

    def __getitem__(self, key): return self._data[key]
    def __iter__(self): return iter(self._data)
    def iteritems(self): return self._data.iteritems()
    def iterkeys(self): return self._data.iterkeys()
    def itervalues(self): return self._data.itervalues()
    def has_key(self, key): return bool(self._data.has_key(key))
    def get(self, key, failobj=None): return self._data.get(key, failobj)
    def __contains__(self, key): return self._data.__contains__(key)

    def popitem(self):
        try:
            key = self._data.minKey()
        except ValueError:
            raise KeyError, 'container is empty'
        return (key, self.pop(key))

class OrderedDict(Dict):
    """A Ordered BTree-based dict-like persistent object that can be safely
    inherited from.

    """

    # what do we get from the superclass:
    # update, setdefault, __len__, popitem, __getitem__, has_key, __contains__,
    # get, __delitem__

    def __init__(self, *args, **kwargs):
        self._order = zc.blist.BList()
        super(OrderedDict, self).__init__(*args, **kwargs)

    def keys(self):
        return list(self._order)

    def __iter__(self):
        return iter(self._order)

    def values(self):
        return [self._data[key] for key in self._order]

    def items(self):
        return [(key, self._data[key]) for key in self._order]

    def __setitem__(self, key, value):
        delta = 1
        if key in self._data:
            delta = 0
        self._data[key] = value
        if delta:
            self._order.append(key)
            self._len.change(delta)

    def updateOrder(self, order):
        order = zc.blist.BList(order)

        if len(order) != len(self._order):
            raise ValueError("Incompatible key set.")

        order_set = set(order)
        
        if len(order) != len(order_set):
            raise ValueError("Duplicate keys in order.")

        if order_set.difference(self._order):
            raise ValueError("Incompatible key set.")

        self._order = order

    def clear(self):
        super(OrderedDict, self).clear()
        del self._order[:]

    def copy(self):
        if self.__class__ is OrderedDict:
            return OrderedDict(self)
        data = self._data
        order = self._order
        try:
            self._data = OOBTree()
            self._order = zc.blist.BList()
            c = copy.copy(self)
        finally:
            self._data = data
            self._order = order
        c.update(self)
        return c

    def iteritems(self):
        return ((key, self._data[key]) for key in self._order)

    def iterkeys(self):
        return iter(self._order)

    def itervalues(self):
        return (self._data[key] for key in self._order)

    def pop(self, key, *args):
        try:
            res = self._data.pop(key)
        except KeyError:
            if args:
                res = args[0]
            else:
                raise
        else:
            self._len.change(-1)
            self._order.remove(key)
        return res

    
