##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""objects with dict API comprised of multiple btrees.

$Id$
"""

from persistent import Persistent
from BTrees import IOBTree, OOBTree, OIBTree, IIBTree
from persistent.list import PersistentList

class AbstractBForest(Persistent):

    _treemodule = None # override
    _treeclass = None # override
    _marker = object()
    
    def __init__(self, d=None, count=2):
        if count < 0:
            raise ValueError("count must be 0 or greater")
        if count == 0:
            if d is not None:
                raise ValueError(
                    "cannot set initial values without a bucket")
            l = PersistentList()
        else:
            Tree = self._treeclass
            if d is not None:
                first = Tree(d)
            else:
                first = Tree()
            l = [Tree() for i in range(count - 1)]
            l.insert(0, first)
            l = PersistentList(l)
        self.buckets = l
    
    def __getitem__(self, key):
        m = self._marker
        res = self.get(key, m)
        if res is m:
            raise KeyError(key)
        return res
    
    def __setitem__(self, key, value):
        self.buckets[0][key] = value
    
    def get(self, key, default=None):
        m = self._marker
        for b in self.buckets:
            res = b.get(key, m)
            if res is not m:
                return res
        return default
    
    def __delitem__(self, key):
        found = False
        for b in self.buckets:
            try:
                del b[key]
            except KeyError:
                pass
            else:
                found = True
        if not found:
            raise KeyError(key)
    
    def update(self, d):
        self.buckets[0].update(d)
    
    def keys(self):
        union = self._treemodule.union
        buckets = self.buckets
        if len(buckets) == 1:
            res = buckets[0].keys()
        else:
            res = union(buckets[0], buckets[1])
            for b in buckets[2:]:
                res = union(res, b)
        return res
    
    def tree(self):
        # convert to a tree; do as much in C as possible.
        buckets = self.buckets
        res = self._treeclass(buckets[-1])
        for b in buckets[-2::-1]:
            res.update(b)
        return res
    
    def items(self):
        return self.tree().items()

    def values(self):
        return self.tree().values()
    
    def iteritems(self):
        for key in self.keys():
            yield key, self[key]
    
    def iterkeys(self):
        return iter(self.keys())
    
    __iter__ = iterkeys
    
    def itervalues(self):
        for key in self.keys():
            yield self[key]
    
    def has_key(self, key): 
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True
    
    def __eq__(self, other):
        if not isinstance(other, dict):
            if (isinstance(other, AbstractBForest) and 
                self._treemodule is not other._treemodule):
                return False
            try:
                other = dict(other)
            except TypeError:
                return False
        return dict(self)==other # :-/
    
    def __gt__(self, other):
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) > id(other)
        return dict(self) > other

    def __lt__(self, other):
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) < id(other)
        return dict(self) < other
        
    def __ge__(self, other):
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) >= id(other)
        return dict(self) >= other
        
    def __le__(self, other):
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) <= id(other)
        return dict(self) <= other

    def __len__(self):
        return len(self.tree())
    
    def setdefault(self, key, failobj=None):
        try:
            res = self[key]
        except KeyError:
            res = self[key] = failobj
        return res
    
    def pop(self, key, d=_marker):
        try:
            res = self[key]
        except KeyError:
            if d is self._marker:
                raise KeyError(key)
            else:
                return d
        else:
            del self[key]
            return res
    
    def popitem(self):
        for b in self.buckets:
            try:
                key = b.minKey()
            except ValueError:
                pass
            else:
                val = b[key]
                del b[key]
                return key, val
        else:
            raise KeyError('popitem():dictionary is empty')
                        
    def __contains__(self, key):
        for b in self.buckets:
            if b.has_key(key):
                return True
        return False
    
    def copy(self):
        # this makes an exact copy, including the individual state of each 
        # bucket.  If you want a dict, cast it to a dict, or if you want
        # another one of these but with all of the keys in the first bucket,
        # call obj.__class__(obj)
        copy = self.__class__(count=0)
        copy.buckets = [self._treeclass(t) for t in self.buckets]
        return copy
    
    def clear(self):
        for b in self.buckets:
            b.clear()
    
    def __nonzero__(self):
        for b in self.buckets:
            if bool(b):
                return True
        return False
    
    def rotateBucket(self):
        buckets = self.buckets
        b = buckets.pop()
        b.clear()
        buckets.insert(0, b)

class IOBForest(AbstractBForest):
    _treemodule = IOBTree
    _treeclass = IOBTree.IOBTree

class OIBForest(AbstractBForest):
    _treemodule = OIBTree
    _treeclass = OIBTree.OIBTree

class OOBForest(AbstractBForest):
    _treemodule = OOBTree
    _treeclass = OOBTree.OOBTree

class IIBForest(AbstractBForest):
    _treemodule = IIBTree
    _treeclass = IIBTree.IIBTree
