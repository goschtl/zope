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

$Id: $
"""
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from persistent import Persistent
from persistent.list import PersistentList
from types import StringTypes, TupleType, ListType

class OrderedDict(Persistent):
    """A Ordered BTree-based dict-like persistent object that can be safely
    inherited from.
    """

    def __init__(self, dict=None, **kwargs):
        self._order = PersistentList()
        self._data = OOBTree()
        self._len = Length()
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def keys(self):
        return self._order[:]

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        return self._data[key]

    def values(self):
        return [self._data[i] for i in self._order]

    def __len__(self):
        return self._len()

    def items(self):
        return [(i, self._data[i]) for i in self._order]

    def __contains__(self, key): return self._data.__contains__(key)

    def has_key(self, key): return bool(self._data.has_key(key))

    def __setitem__(self, key, value):
        delta = 1
        if key in self._data:
            delta = 0
        self._data[key] = value
        if delta:
            self._order.append(key)
            self._len.change(delta)

    def __delitem__(self, key):
        del self._data[key]
        self._order.remove(key)
        self._len.change(-1)

    def updateOrder(self, order):
        if not isinstance(order, ListType) and \
            not isinstance(order, TupleType):
            raise TypeError('order must be a tuple or a list.')

        if len(order) != len(self._order):
            raise ValueError("Incompatible key set.")

        was_dict = {}
        will_be_dict = {}
        new_order = PersistentList()

        for i in range(len(order)):
            was_dict[self._order[i]] = 1
            will_be_dict[order[i]] = 1
            new_order.append(order[i])

        if will_be_dict != was_dict:
            raise ValueError("Incompatible key set.")

        self._order = new_order

    def update(self, other):
        if other.__class__ != OrderedDict:
            raise TypeError('argument must be an OrderedDict.')
        for k, v in other.iteritems():
            self[k] = v

    def clear(self):
        self._data.clear()
        self._order = PersistentList()
        self._len.set(0)

    def copy(self):
        import copy
        data = self._data
        order = self._order
        try:
            self._data = OOBTree()
            self._order = PersistentList()
            c = copy.copy(self)
        finally:
            self._data = data
            self._order = order
        c.update(self)
        return c

    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return iter(self.values())

    def get(self, key, failobj=None):
        return self._data.get(key, failobj)

