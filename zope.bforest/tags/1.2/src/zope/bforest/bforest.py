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
"""

import persistent
import persistent.list
import BTrees

class AbstractBForest(persistent.Persistent):

    _treemodule = None # override
    _marker = object()
    
    def __init__(self, d=None, count=2):
        if count < 0:
            raise ValueError("count must be 0 or greater")
        if count == 0:
            if d is not None:
                raise ValueError(
                    "cannot set initial values without a bucket")
            l = persistent.list.PersistentList()
        else:
            Tree = self._treemodule.BTree
            if d is not None:
                first = Tree(d)
            else:
                first = Tree()
            l = [Tree() for i in range(count - 1)]
            l.insert(0, first)
            l = persistent.list.PersistentList(l)
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
            # we delete all, in case one bucket is masking an old value
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
        buckets = self.buckets
        if len(buckets) == 1:
            res = buckets[0].keys()
        elif getattr(self._treemodule, 'multiunion', None) is not None:
            return self._treemodule.multiunion(buckets)
        else:
            union = self._treemodule.union
            res = union(buckets[0], buckets[1])
            for b in buckets[2:]:
                res = union(res, b)
        return res
    
    def tree(self):
        # convert to a tree; do as much in C as possible.
        buckets = self.buckets
        res = self._treemodule.BTree(buckets[-1])
        for b in buckets[-2::-1]:
            res.update(b)
        return res
    
    def items(self):
        return self.tree().items()

    def values(self):
        return self.tree().values()

    def maxKey(self, key=None):
        res = m = self._marker
        if key is None:
            args = ()
        else:
            args = (key,)
        for b in self.buckets:
            try:
                v = b.maxKey(*args)
            except ValueError:
                pass
            else:
                if res is m or v > res:
                    res = v
        if res is m:
            raise ValueError('no key')
        return res

    def minKey(self, key=None):
        res = m = self._marker
        if key is None:
            args = ()
        else:
            args = (key,)
        for b in self.buckets:
            try:
                v = b.minKey(*args)
            except ValueError:
                pass
            else:
                if res is m or v < res:
                    res = v
        if res is m:
            raise ValueError('no key')
        return res

    def iteritems(self, min=None, max=None, excludemin=False, excludemax=False):
        # this approach might be slower than simply iterating over self.keys(),
        # but it has a chance of waking up fewer objects in the ZODB, if the
        # iteration stops early.
        sources = []
        for b in self.buckets:
            i = iter(b.items(min, max, excludemin, excludemax))
            try:
                first = i.next()
            except StopIteration:
                pass
            else:
                sources.append([first, i])
        scratch = self._treemodule.Bucket()
        while sources:
            for ((k, v), i) in sources:
                scratch.setdefault(k, v)
            k = scratch.minKey()
            yield k, scratch[k]
            for i in range(len(sources)-1, -1, -1):
                source = sources[i]
                if source[0][0] == k:
                    try:
                        source[0] = source[1].next()
                    except StopIteration:
                        del sources[i]
            scratch.clear()
    
    def iterkeys(self,
                 min=None, max=None, excludemin=False, excludemax=False):
        return (k for k, v in self.iteritems(min, max, excludemin, excludemax))
    
    __iter__ = iterkeys
    
    def itervalues(self,
                   min=None, max=None, excludemin=False, excludemax=False):
        return (v for k, v in self.iteritems(min, max, excludemin, excludemax))
    
    def __eq__(self, other):
        # we will declare contents and its ordering to define equality.  More
        # restrictive definitions can be wrapped around this one.
        if getattr(other, 'iteritems', None) is None:
            return False
        si = self.iteritems()
        so = other.iteritems()
        while 1:
            try:
                k, v = si.next()
            except StopIteration:
                try:
                    so.next()
                except StopIteration:
                    return True
                return False
            try:
                ok, ov = so.next()
            except StopIteration:
                return False
            else:
                if ok != k or ov != v:
                    return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        # TODO blech, change this
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) > id(other)
        return dict(self) > other

    def __lt__(self, other):
        # TODO blech, change this
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) < id(other)
        return dict(self) < other
        
    def __ge__(self, other):
        # TODO blech, change this
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) >= id(other)
        return dict(self) >= other
        
    def __le__(self, other):
        # TODO blech, change this
        if not isinstance(other, dict):
            try:
                other = dict(other)
            except TypeError:
                return id(self) <= id(other)
        return dict(self) <= other

    def __len__(self):
        # keeping track of a separate length is currently considered to be
        # somewhat expensive per write and not necessarily always valuable
        # (that is, we don't always care what the length is). Therefore, we
        # have this quite expensive default approach. If you need a len often
        # and cheaply then you'll need to wrap the BForest and keep track of it
        # yourself.  This is expensive both because it wakes up every BTree and
        # bucket in the BForest, which might be quite a few objects; and
        # because of the merge necessary to create the composite tree (which
        # eliminates duplicates from the count).
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
        key = self.minKey()
        val = self.pop(key)
        return key, val

    def __contains__(self, key):
        for b in self.buckets:
            if b.has_key(key):
                return True
        return False

    has_key = __contains__

    def copy(self):
        # this makes an exact copy, including the individual state of each 
        # bucket.  If you want a dict, cast it to a dict, or if you want
        # another one of these but with all of the keys in the first bucket,
        # call obj.__class__(obj)
        copy = self.__class__(count=len(self.buckets))
        for i in range(len(self.buckets)):
            copy.buckets[i].update(self.buckets[i])
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
    _treemodule = BTrees.family32.IO

class OIBForest(AbstractBForest):
    _treemodule = BTrees.family32.OI

class IIBForest(AbstractBForest):
    _treemodule = BTrees.family32.II

class LOBForest(AbstractBForest):
    _treemodule = BTrees.family64.IO

class OLBForest(AbstractBForest):
    _treemodule = BTrees.family64.OI

class LLBForest(AbstractBForest):
    _treemodule = BTrees.family64.II

class OOBForest(AbstractBForest):
    _treemodule = BTrees.family32.OO
