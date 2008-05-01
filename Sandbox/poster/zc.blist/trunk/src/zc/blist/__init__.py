##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
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
import sys
import random

import persistent
import persistent.list
import BTrees.OOBTree
import BTrees.Length
import rwproperty

def method(f):
    def wrapper(self, *args, **kwargs):
        if self.shared:
            raise RuntimeError('cannot mutate shared object')
        return f(self, *args, **kwargs)
    return wrapper

class setproperty(rwproperty.rwproperty):

    @staticmethod
    def createProperty(func):
        return property(None, method(func))

    @staticmethod
    def enhanceProperty(oldprop, func):
        return property(oldprop.fget, method(func), oldprop.fdel)

def supercall(name):
    sys._getframe(1).f_locals[name] = method(
        lambda self, *args, **kwargs: getattr(
            super(self.__class__, self), name)(*args, **kwargs))

def makeProperty(name, default=None):
    protected = '_z_%s__' % name
    def setprop(self, value):
        if self.shared:
            raise RuntimeError('cannot mutate shared object')
        if value is not None and not isinstance (value, (int, long)):
            raise TypeError(value)
        setattr(self, protected, value)
    sys._getframe(1).f_locals[name] = property(
        lambda self: getattr(self, protected, default), setprop)

# helpers

def shift_sequence(l, count):
    res = l[:count]
    del l[:count]
    return res

# Bucket and Index extend this

class Collections(persistent.Persistent):
    # separate persistent object so a change does not necessitate rewriting
    # bucket or index
    def __init__(self, *collections):
        self._collections = collections

    def __iter__(self):
        return iter(self._collections)

    def add(self, collection):
        if collection not in self._collections:
            self._collections += (collection,)

    def remove(self, collection):
        res = []
        found = False
        for coll in self._collections:
            if coll is not collection:
                res.append(coll)
            else:
                assert not found
                found = True
        self._collections = tuple(res)

    def __len__(self):
        return len(self._collections)

    def __getitem__(self, key):
        return self._collections.__getitem__(key)

class AbstractData(persistent.Persistent):
    def __init__(self, collection, identifier=None, previous=None, next=None,
                 parent=None):
        self.collections = Collections(collection)
        self.identifier = identifier
        self.previous = previous
        self.next = next
        self.parent = parent

    @property
    def collection(self):
        if len(self.collections) > 1:
            raise ValueError('ambiguous')
        return self.collections[0]

    @property
    def shared(self):
        return len(self.collections) > 1
    
    makeProperty('identifier')
    makeProperty('previous')
    makeProperty('next')
    makeProperty('parent')

    # the other shared "interface" bits are `contained_len`, `clear`, `copy`,
    # and `index`

class Bucket(persistent.list.PersistentList, AbstractData):
    """Buckets hold blocks of data from from the collection."""

    def __init__(self, collection,
                 identifier, previous=None, next=None, parent=None, vals=None):
        AbstractData.__init__(
            self, collection, identifier, previous, next, parent)
        persistent.list.PersistentList.__init__(self, vals)

    def __getslice__(self, i, j):
        return self.data[i:j]

    def contained_len(self, collection):
        return len(self)

    @method
    def clear(self):
        del self[:]

    def copy(self, collection):
        assert self.shared, 'only copy shared object'
        self.collections.remove(collection)
        return Bucket(
            collection, self.identifier, self.previous, self.next,
            self.parent, self)

    @method
    def balance(self, right):
        len_left = len(self)
        len_right = len(right)
        move_index = (len_left + len_right) // 2
        right = self.collection._mutable(right)
        if len_left > len_right:
            # move some right
            moved = self[move_index:]
            right[0:0] = moved
            del left[move_index:]
        else:
            # move some left
            move_index -= len_left
            moved = right[:move_index]
            left.extend(moved)
            del right[:move_index]

    @method
    def rotate(self, right):
        if len(self) + len(right) > self.collection.bucket_size:
            self.balance(right)
        else:
            moved = right[:]
            self.extend(moved)
            right = self.collection._mutable(right)
            del right[:]

    @method
    def rotateRight(self, right):
        if len(self) + len(right) > self.collection.bucket_size:
            self.balance(right)
        else:
            moved = self[:]
            right = self.collection._mutable(right)
            right[0:0] = moved
            del self[:]
        

    supercall('__setitem__')
    supercall('__delitem__')
    supercall('__setslice__')
    supercall('__delslice__')
    supercall('__iadd__')
    supercall('__imul__')
    supercall('append')
    supercall('insert')
    supercall('pop')
    supercall('remove')
    supercall('reverse')
    supercall('sort')
    supercall('extend')

class Index(BTrees.family32.II.Bucket, AbstractData):
    """Indexes index buckets and sub-indexes."""

    supercall('clear')
    supercall('update')
    supercall('__setitem__')
    supercall('__delitem__')
    supercall('setdefault')
    supercall('pop')

    def __init__(self, collection,
                 identifier, previous=None, next=None, parent=None):
        AbstractData.__init__(
            self, collection, identifier, previous, next, parent)

    def index(self, other):
        for k, v in self.items():
            if v == other:
                return k
        raise ValueError('value not found; likely programmer error')

    def contained_len(self, collection):
        val = self.maxKey()
        return val + collection._mapping[self[val]].contained_len(collection)

    @method
    def balance(self, right):
        len_left = len(self)
        len_right = len(right)
        move_index = (len_left + len_right) // 2
        right = self.collection._mutable(right)
        if len_left > len_right:
            # move some right
            items = list(self.items()[move_index:])
            zero = items[0][0] # this will be index 0 on the right
            offset = (items[-1][0] + # this is offset for current right values
                      self.collection._mapping[items[-1][1]].contained_len(
                        self.collection) - zero)
            for k, o in reversed(right.items()):
                right[offset+k] = o
                del right[k]
            for k, o in items:
                right[k-zero] = o
                del self[k]
                self.collection._mutable(
                    self.collection._mapping[o]).parent = right.identifier
        else:
            # move some left
            move_index -= len_left
            items = list(right.items()[:move_index])
            offset = self.contained_len(self.collection)
            for k, o in items:
                self[offset+k] = o
                del right[k]
                self.collection._mutable(
                    self.collection._mapping[o]).parent = self.identifier
            offset = (items[-1][0] +
                      self.collection._mapping[items[-1][1]].contained_len(
                        self.collection))
            for k, o in list(right.items()):
                del right[k]
                right[k-offset] = o

    @method
    def rotate(self, right):
        if len(self) + len(right) > self.collection.index_size:
            self.balance(right)
        else:
            offset = self.contained_len(self.collection)
            for k, o in list(right.items()):
                self[offset+k] = o
                self.collection._mutable(
                    self.collection._mapping[o]).parent = self.identifier
            right = self.collection._mutable(right)
            right.clear()

    @method
    def rotateRight(self, right):
        if len(self) + len(right) > self.collection.index_size:
            self.balance(right)
        else:
            offset = self.contained_len(self.collection)
            right = self.collection._mutable(right)
            for k, o in reversed(right.items()):
                right[offset+k] = o
                del right[k]
            for k, o in self.items():
                right[k] = o
                self.collection._mutable(
                    self.collection._mapping[o]).parent = right.identifier
            self.clear()

    def copy(self, collection):
        assert self.shared, 'only copy shared object'
        self.collections.remove(collection)
        res = Index(collection, self.identifier, self.previous, self.next,
                    self.parent)
        res.update(self)
        return res

class BList(persistent.Persistent):

    def __init__(self, vals=None,
                 bucket_size=30, index_size=10, family=BTrees.family32):
        self.bucket_size = bucket_size
        self.index_size = index_size
        self.family = family
        self._mapping = self.family.IO.BTree()
        self._top_index = 0
        self._mapping[self._top_index] = Bucket(self, self._top_index)
        if vals is not None:
            self.extend(vals)

    def copy(self):
        res = self.__class__.__new__(self.__class__)
        res.bucket_size = self.bucket_size
        res.index_size = self.index_size
        res.family = self.family
        res._mapping = self.family.IO.BTree()
        res._top_index = 0
        res._mapping.update(self._mapping)
        for v in self._mapping.values():
            v.collections.add(res)
        return res

    @property
    def data(self):
        return self._mapping[self._top_index]

    # Read API

    def __contains__(self, value):
        # this potentially loads all buckets and items from ZODB.  Then again,
        # standard list or tuple *will* load all items.
        for item in self:
            if value == item:
                return True
        return False

    def __len__(self):
        return self.data.contained_len(self)

    def count(self, value):
        # whee!  Let's load everything!
        ct = 0
        for item in self:
            if value == item:
                ct += 1
        return ct

    def _get_bucket(self, index):
        bucket = self.data
        ix = index
        while not isinstance(bucket, Bucket):
            key = bucket.maxKey(ix)
            bucket = self._mapping[bucket[key]]
            ix -= key
        return bucket, ix

    def iter(self, start=0):
        length = len(self)
        if start < 0:
            start += length
            if start < 0:
                raise IndexError('list index out of range')
        if length > start:
            bucket, ix = self._get_bucket(start)
            for v in bucket[ix:]:
                yield v
            bucket_ix = bucket.next
            while bucket_ix is not None:
                bucket = self._mapping[bucket_ix]
                for v in bucket:
                    yield v
                bucket_ix = bucket.next

    def iterReversed(self, start=-1):
        length = len(self)
        if start < 0:
            start += length
            if start < 0:
                raise IndexError('list index out of range')
        if length > start:
            bucket, ix = self._get_bucket(start)
            for v in reversed(bucket[:ix+1]):
                yield v
            bucket_ix = bucket.previous
            while bucket_ix is not None:
                bucket = self._mapping[bucket_ix]
                for v in reversed(bucket):
                    yield v
                bucket_ix = bucket.previous

    def iterSlice(self, start=0, stop=None, stride=None):
        if isinstance(start, slice):
            if stop is not None or stride is not None:
                raise ValueError(
                    'cannot pass slice with additional stop or stride')
        else:
            start = slice(start, stop, stride)
        start, stop, stride = start.indices(len(self))
        if stride == 1:
            ix = start
            i = self.iter(start)
            while ix < stop:
                yield i.next()
                ix += 1
        elif stride == -1:
            ix = start
            i = self.iterReversed(start)
            while ix > stop:
                yield i.next()
                ix -= 1
        else:
            if stride < 0:
                condition = lambda begin, end: begin > end
            else:
                condition = lambda begin, end: begin < end
            ix = start
            while condition(ix, stop):
                bucket, i = self._get_bucket(ix)
                yield bucket[i]
                ix += stride

    def __iter__(self):
        return self.iter()

    def index(self, value, start=0, stop=None):
        for ct, item in enumerate(self.iterSlice(start, stop)):
            if item == value:
                return start + ct
        raise ValueError('.index(x): x not in collection')

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.iterSlice(index) # XXX return view?
        if index < 0:
            index += length
            if index < 0:
                raise IndexError('list index out of range')
        elif index > len(self):
            raise IndexError('list index out of range')
        bucket, ix = self._get_bucket(index)
        return bucket[ix]

    # Write API
    
    # Everything relies on __setitem__ to reduce duplicated logic

    def append(self, value):
        self[len(self)] = value

    def insert(self, index, value):
        self[index:index] = (value,)

    def __delitem__(self, index):
        if not isinstance(index, slice):
            if index > len(self):
                raise IndexError('list assignment index out of range')
            index = slice(index, index+1)
        elif index.step == 1:
            index = slice(index.start, index.stop)
        elif index.step is not None:
            start, stop, stride = index.indices(len(self))
            if stride < 0:
                ix = range(start, stop, stride)
            else:
                ix = reversed(range(start, stop, stride))
            for i in ix:
                self.__setitem__(slice(i, i+1), ())
            return
        self.__setitem__(index, ())

    def extend(self, iterable):
        length = len(self)
        self[length:length] = iterable

    __iadd__ = extend

    def pop(self, index=-1):
        res = self[index]
        self[index:index+1] = ()
        return res

    def remove(self, item):
        index = self.index(item)
        self[index:index+1] = ()

    def reverse(self):
        self[:] = reversed(self)

    def sort(self, cmpfunc=None):
        vals = list(self)
        vals.sort(cmpfunc)
        self[:] = l

    # __setitem__ helpers

    def _reindex(self, start_bucket, stop_bucket, recurse=False):
        bucket = start_bucket
        k = None
        stopped = False
        while bucket is not None and bucket.identifier != self._top_index:
            stopped = stopped or bucket is stop_bucket
            parent = self._mapping[bucket.parent]
            if k is None:
                k = parent.index(bucket.identifier)
                if k == parent.minKey() and k > 0:
                    parent = self._mutable(parent)
                    del parent[k]
                    k = 0
                    parent[k] = bucket.identifier
            v = bucket.contained_len(self)
            try:
                next = parent.minKey(k+1)
            except ValueError:
                k = None
                if recurse:
                    self._reindex(parent, self._mapping[stop_bucket.parent],
                                  recurse)
                if stopped:
                    break
            else:
                k += v
                if next != k:
                    b = parent[next]
                    parent = self._mutable(parent)
                    del parent[next]
                    parent[k] = b
            bucket = bucket.next
            if bucket is not None:
                bucket = self._mapping[bucket]

    def _mutable(self, bucket):
        if bucket.shared:
            bucket = bucket.copy(self)
            self._mapping[bucket.identifier] = bucket
        return bucket

    _v_nextid = None

    def _generateId(self):
        # taken from zope.app.intid code
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(
                    self.family.minint, self.family.maxint)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self._mapping:
                return uid
            self._v_nextid = None

    # __setitem__ itself: the workhorse

    def __setitem__(self, index, value):
        length = len(self)
        # To reduce the amount of duplicated code, everything is based on
        # slices. Either you are replacing specific items (index is an integer
        # less than len or a slice with an explicit step) or deleting/inserting
        # ranges (index is an integer equal to len or a slice with an implicit
        # step of 1).  We convert integer requests to slice requests here.
        if not isinstance(index, slice):
            value = (value,)
            if index == length:
                index = slice(length, length)
            elif index > length:
                raise IndexError('list assignment index out of range')
            elif index == -1:
                index = slice(length-1, length, 1) # we specify a step to use
                # the second, "replace values" code path below, rather than
                # the first "range" code path.
            else:
                index = slice(index, index+1, 1) # same reason as above for
                # specifying the step.

        start, stop, stride = index.indices(length)
        if index.step is None:
            # delete and/or insert range; bucket arrangement may change
            value = list(value) # we actually do mutate this, so a list is
            # intentional.  Even if the original value is a list, we don't want
            # to mutate the original.
            len_value = len(value)
            if start == 0 and stop == length and stride == 1:
                # shortcut: clear out everything
                self._mapping.clear()
                self._top_index = 0
                start_bucket = self._mapping[
                    self._top_index] = Bucket(self, self._top_index)
                start_ix = 0
            elif stop != start:
                # we're supposed to delete
                start_bucket, start_ix = self._get_bucket(start)
                stop_bucket, stop_ix = self._get_bucket(stop)
                bucket = start_bucket
                ix = start_ix
                while True:
                    if bucket is stop_bucket:
                        removed = bucket[ix:stop_ix]
                        if removed:
                            bucket = self._mutable(bucket)
                            del bucket[ix:stop_ix]
                        break
                    removed = bucket[ix:]
                    if removed:
                        bucket = self._mutable(bucket)
                        del bucket[ix:]
                    bucket_ix = bucket.next
                    if bucket_ix is None:
                        break
                    bucket = self._mapping[bucket_ix]
                    ix = 0
                bucket = start_bucket
                ix = start_ix
                # populate old buckets with new values, until we are out of
                # new values or old buckets
                while value:
                    items = shift_sequence(
                        value, self.bucket_size - len(bucket))
                    bucket[ix:ix] = items
                    if bucket is stop_bucket or not value:
                        stop_ix = len(items)
                        break
                    bucket = self._mapping[bucket.next]
                    ix = 0

                # we've deleted values, and may have replaced some,
                # and now we need to see if we need to rearrange
                # buckets because they are smaller than the fill ratio
                # allows.  We do this even if we have more values to
                # insert so that the insert code can begin from a sane
                # state; this is an obvious possible optimization point,
                # therefore (though other optimizations may be better choices).

                # The algorithm has us first try to balance across
                # siblings, and then clean up the parents.  Typically
                # B+ tree algorithm descriptions go
                # one-item-at-a-time, while we may have swaths of
                # changes to which we need to adjust.
                #
                # Key adjustments are different than the standard B+
                # tree story because this is a sequence, and our keys
                # are indices that we need to adjust to accomodate the
                # deletions.  This means siblings to all of our
                # parents, walking up the tree.  The "swaths of
                # changes" also makes this a bit tricky.

                fill_maximum = self.bucket_size
                fill_minimum = fill_maximum // 2

                original_stop_bucket = stop_bucket

                while start_bucket is not None:

                    # We'll get the buckets rotated so that any
                    # bucket that has members will be above the fill ratio
                    # (unless it is the only bucket).
                    #
                    # `bucket` is the last bucket we might have put
                    # anything in to; we'll want to look at it and the
                    # `stop_bucket` (if different) to see if we need to
                    # adjust.
                    #
                    # if bucket and stop_bucket are different and
                    # stop_bucket is not empty and either are below the
                    # fill_minimum...
                        # if the combination is less than the fill_maximum,
                        # put in bucket and empty stop_bucket
                        # else redistribute across so both are above
                        # fill_minimum

                    len_bucket = len(bucket)
                    len_stop = len(stop_bucket)
                    if (bucket is not stop_bucket and
                        len_stop and (
                            len_bucket < fill_minimum or
                            len_stop < fill_minimum)):
                        bucket.rotate(stop_bucket)
                        len_bucket = len(bucket)
                        len_stop = len(stop_bucket)

                    # if (bucket is stop_bucket or stop_bucket is empty)
                    # and bucket.previous is None and stop_bucket.next is
                    # None, shortcut: just make sure this is the top
                    # bucket and break.

                    if ((bucket is stop_bucket or not len_stop) and
                        bucket.previous is None and stop_bucket.next is None):
                        if self.data is not bucket:
                            self._mapping.clear()
                            self._mapping[bucket.identifier] = bucket
                            self._top_index = bucket.identifier 
                            bucket.parent = None
                        else:
                            assert bucket.parent is None
                        bucket.next = None
                        stop_bucket = None
                        break

                    # now these are the possible states:
                    # - bucket is stop_bucket and is empty
                    # - bucket is stop_bucket and is too small
                    # - bucket is stop_bucket and is ok
                    # - bucket and stop_bucket are both empty
                    # - bucket is ok and stop_bucket is empty
                    # - bucket is too small and stop_bucket is empty
                    # - bucket is ok and stop_bucket is ok
                    #
                    # Therefore, 
                    # - if the stop_bucket is ok or the bucket is empty,
                    #   we're ok with this step, and can move on to
                    #   adjusting the indexes and pointers.
                    # - otherwise the bucket is too small, and there is
                    #   another bucket to rotate with.  Find the bucket
                    #   and adjust so that no non-empty buckets are
                    #   beneath the fill_minimum.  Make sure to adjust the
                    #   start_bucket or stop_bucket to include the altered
                    #   bucket.

                    if len_bucket < fill_minimum:
                        previous = bucket.previous
                        next = stop_bucket.next
                        assert previous is not None or next is not None
                        assert bucket is stop_bucket or not len_stop
                        if next is not None:
                            next = self._mapping[next]
                        if (next is None or
                            previous is not None and
                            len(next) + len_bucket > fill_maximum):
                            # work with previous
                            previous = self._mapping[previous]
                            previous.rotate(bucket)
                            if bucket is start_bucket:
                                bucket = start_bucket = previous
                            if not bucket:
                                bucket = previous
                                assert bucket
                        else:
                            # work with next
                            bucket.rotateRight(next)
                            stop_bucket = next

                    # OK, now we need to adjust pointers and get rid of
                    # empty buckets.  We'll go level-by-level.

                    reindex_start = start_bucket

                    b = bucket
                    while b is not None:
                        next = b.next
                        if next is not None:
                            next = self._mapping[next]
                        if not b: # it is empty
                            parent = self._mapping[b.parent]
                            ix = parent.index(b.identifier)
                            del parent[ix]
                            if b.previous is not None:
                                self._mapping[b.previous].next = b.next
                            if next is not None: # next defined at loop start
                                next.previous = b.previous
                            if b is reindex_start:
                                reindex_start = next
                            del self._mapping[b.identifier]
                        if b is stop_bucket:
                            break
                        b = next

                    self._reindex(reindex_start, stop_bucket)

                    # now we get ready for the next round...

                    start_bucket = start_bucket.parent
                    if start_bucket is not None:
                        start_bucket = self._mapping[start_bucket]
                    stop_bucket = stop_bucket.parent
                    if stop_bucket is not None:
                        stop_bucket = self._mapping[stop_bucket]
                    bucket = bucket.parent
                    if bucket is not None:
                        bucket = self._mapping[bucket]
                    fill_maximum = self.index_size
                    fill_minimum = fill_maximum // 2
                    
                assert stop_bucket is None

                if not value:
                    return # we're done; don't fall through to add story
                else:
                    # we've replaced old values with new, but there are
                    # some more left.  we'll set things up so the
                    # standard insert story should work for the remaining
                    # values.
                    start_bucket = original_stop_bucket
                    start_ix = stop_ix
                    # ...now continue with add story

            else:
                start_bucket, start_ix = self._get_bucket(start)
            # this is the add story.

            # So, we have a start_bucket and a start_ix: we're supposed
            # to insert the values in i at start_ix in start_bucket.
            if not value:
                return
            fill_maximum = self.bucket_size
            fill_minimum = fill_maximum // 2

            # Clean out the ones after start_ix in the start_bucket, if
            # any.  

            moved = start_bucket[start_ix:]
            value.extend(moved)
            start_bucket = self._mutable(start_bucket)
            del start_bucket[start_ix:]
            ix = start_ix
            bucket = start_bucket
            created = []

            # Start filling at the ix.  Fill until we reached len
            # or until i is empty.  Make new buckets, remembering them in
            # a list, and fill them until i is empty, and then continue
            # with the removed ones from the start_bucket.  If the last
            # bucket is too small, merge or rotate as appropriate.

            length = fill_maximum - len(bucket)
            while value:
                added = shift_sequence(value, length)
                bucket.extend(added)
                if value:
                    old_bucket = bucket
                    identifier = self._generateId()
                    bucket = self._mapping[identifier] = Bucket(
                        self, identifier,
                        previous=old_bucket.identifier, next=old_bucket.next)
                    old_bucket.next = bucket.identifier
                    if bucket.next is not None:
                        self._mapping[bucket.next].previous = bucket.identifier
                    created.append(bucket)
                    length = self.bucket_size

            if (bucket.identifier != self._top_index and
                len(bucket) < fill_minimum):
                # this should only be able to happen when a previous bucket
                # is already filled. It's simplest, then, to just split the
                # contents of the previous bucket and this one--that way
                # there's not any empty bucket to have to handle.
                previous = self._mapping[bucket.previous]
                assert len(previous) + len(bucket) >= 2 * fill_minimum
                previous.balance(bucket)

            # Now we have to insert any new buckets in the parents.  We
            # again fill the parents, creating and remembering as
            # necessary, and rotating at the end.  We keep on walking up
            # until the list of new buckets is empty.  If we reach the top,
            # we add a level at the top and continue.

            if not created:
                self._reindex(start_bucket, bucket)
                return

            value = created
            fill_maximum = self.index_size
            fill_minimum = fill_maximum // 2

            while value:
                if start_bucket.identifier == self._top_index: # the top
                    assert start_bucket.parent is None
                    self._top_index = identifier = self._generateId()
                    parent = self._mapping[identifier] = Index(
                        self, identifier, parent=None)
                    parent[0] = start_bucket.identifier
                    start_bucket.parent = parent.identifier
                    start_ix = 0
                    bucket = start_bucket = parent
                else:
                    parent = self._mapping[start_bucket.parent]
                    start_ix = parent.index(start_bucket.identifier)
                    bucket = start_bucket = parent
                    value.extend(
                        self._mapping[i] for i in
                        start_bucket.values(start_ix, excludemin=True))
                    for k in tuple(
                        start_bucket.keys(start_ix, excludemin=True)):
                        del start_bucket[k]
                ix = start_ix + self._mapping[
                    start_bucket[start_ix]].contained_len(self)
                created = []

                # Start filling at the ix. Fill until we reached len or
                # until i is empty. Make new buckets, remembering them in a
                # list, and fill them until i is empty, and then continue
                # with the removed ones from the start_bucket. If the last
                # bucket is too small, merge or rotate as appropriate.

                length = fill_maximum - len(bucket)
                while value:
                    for o in shift_sequence(value, length):
                        bucket[ix] = o.identifier
                        o.parent = bucket.identifier
                        ix += o.contained_len(self)
                    # we don't necessarily need to fix parents--
                    # we'll get to them above
                    if value:
                        identifier = self._generateId()
                        bucket = self._mapping[identifier] = Index(
                            self, identifier,
                            previous=bucket.identifier, next=bucket.next)
                        self._mapping[bucket.previous].next = identifier
                        if bucket.next is not None:
                            self._mapping[bucket.next].previous = identifier
                        created.append(bucket)
                        length = fill_maximum
                        ix = 0

                if (bucket.identifier != self._top_index and
                    len(bucket) < fill_minimum):
                    # this should only be able to happen when a previous
                    # bucket is already filled. It's simplest, then, to
                    # just split the contents of the previous bucket and
                    # this one--that way there's not any empty bucket to
                    # have to handle.
                    assert (len(self._mapping[bucket.previous]) + len(bucket) >=
                            2 * fill_minimum)
                    self._mapping[bucket.previous].balance(bucket)
                value = created
            if start_bucket.identifier != self._top_index:
                # we need to correct the indices of the parents.
                self._reindex(start_bucket, bucket, recurse=True)

        else:
            # replace one set with a set of equal length
            changed = []
            index = start
            removed = {}
            problems = set()
            added = {}
            error = None
            value_ct = 0
            for v in value:
                value_ct += 1
                if index >= stop:
                    error = ValueError(
                        'attempt to assign sequence of at least size %d '
                        'to extended slice of size %d' % (
                            value_ct, (stop - start) / stride))
                    break
                bucket, ix = self._get_bucket(index)
                old = bucket[ix]
                if old in removed:
                    removed[old].add(bucket)
                else:
                    removed[old] = set((bucket,))
                if v in added:
                    added[v].add(bucket.identifier)
                else:
                    added[v] = set((bucket.identifier,))
                bucket[ix] = v
                changed.append((bucket, ix, old))
                index += stride
            else:
                if value_ct < (stop - start) / stride:
                    error = ValueError(
                            'attempt to assign sequence of size %d to '
                            'extended slice of size %d' % (
                            value_ct, (stop - start) / stride))
            if not error and problems:
                problems.difference_update(removed)
                if problems:
                    error = ValueError('item(s) already in collection',
                        problems)
            if error:
                for bucket, ix, old in changed:
                    bucket[ix] = old
                raise error

#    I want eq and ne but don't care much about the rest

    def __eq__(self, other):
        return isinstance(other, Sequence) and tuple(self) == tuple(other)

    def __ne__(self, other):
        return not self.__eq__(other)

#     def __lt__(self, other):
#         pass
# 
#     def __gt__(self, other):
#         pass
# 
#     def __le__(self, other):
#         pass
# 
#     def __ge__(self, other):
#         pass

#     def __add__(self, other):
#         pass
# 
#     def __mul__(self, other):
#         pass
# 
#     def __rmul__(self, other):
#         pass
