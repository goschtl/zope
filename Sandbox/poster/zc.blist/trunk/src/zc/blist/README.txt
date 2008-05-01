~~~~~~~~
zc.blist
~~~~~~~~

.. contents::

========
Overview
========

The sequence in this package has a list-like API, but stores its values in
individual buckets. This means that, for small changes in large sequences, the
sequence could be a big win. For instance, an ordered BTree-based container
might want to store order in a sequence, so that moves only cause a bucket or
two-- around 50 strings or less--to be rewritten in the database, rather than
the entire contents (which might be thousands of strings or more).

If the sequence is most often completely rearranged, the complexity of the code
in this package is not desirable.  It only makes sense if changes most
frequently are fairly small.

One downside is that reading and writing is more work than with a normal list.
If this were to actually gain traction, perhaps writing some or all of it in C
would be helpful.  However, it still seems pretty snappy.

Another downside is the corollary of the bucket advantage listed initially:
with more persistent objects, iterating over it will fill a lot of ZODB's
object cache (which is based on the number of objects cached, rather than the
size).  Specify a big cache if you are using these to store a lot of data and
are frequently iterating or changing.

These sequences return slices as iterators, and add some helpful iteration
methods.

Other than that, these sequences work like a standard Python sequence. Therefore
this file is not geared towards users of the data structure but implementers.

=========
Mechanism
=========

In its implementation, the sequence is an adapted B+ tree. Indexes are keys, but
each bucket or branch starts at 0. For instance, a perfectly-balanced bucket
sequence with 16 items, and 3 in a bucket or branch, would have "keys" like
this::

        0           8
     0     4     0     4
    0 2   0 2   0 2   0 2
   01 01 01 01 01 01 01 01 

This arrangement minimizes the changes to keys necessary when a new value is
inserted low in the sequence: ignoring balancing the tree, only subsequent
siblings and subsequent siblings of parents must be adjusted.  For instance,
inserting a new value in the 0 position of the bucketsequence described above
(the worst case for the algorithm, in terms of the number of objects touched)
would result in the following tree::

        0           9
     0     5     0     4
    0  3   0 2   0 2   0 2
   012 01 01 01 01 01 01 01

===========================
Performance Characteristics
===========================

The Good
========

- ``__getitem__`` is efficient, not loading unnecessary buckets.  It handles
  slices pretty well too, not even loading intermediary buckets if the slice
  is very large.  Slices currently return iterables rather than lists; this
  may switch to a view of some sort.  All that should be assumed right now is
  that you can iterate over the result of a slice.

- ``__setitem__`` and all the write methods do a pretty good job in terms of
  efficient loading of buckets, and only writing what they need to.  It
  supports full Python slice semantics.

- ``copy`` is cheap: it reuses buckets and indexes so that new inner
  components are created lazily when they mutate.

- While ``__contains__``, ``__iter__``, ``index`` and other methods are brute
  force and written in Python, they might not load all buckets and items, while
  with a normal list or tuple, they always will. See also ``iter``,
  ``iterReversed``, and ``iterSlice``.

The So-So
=========

- ``count``, ``__eq__``, and other methods load all buckets and items, and are
  brute force in Python. Lists and tuples will load all items, and is brute
  force in C.

The Bad
=======

- This will create a lot of Persistent objects for one blist, which can cause
  cache eviction problems.

==================
Regression Testing
==================

We'll use a `matches` function to compare a bucket sequence with a standard
Python list to which the same modifications have made.  This also checks for
bucket health [#matches]_.

    >>> import zc.blist
    >>> b = zc.blist.BList(bucket_size=5, index_size=4) # we want > 3 so min is > 1
    >>> matches(b, [])
    True
    >>> b.append(0)
    >>> matches(b, [0])
    True
    >>> del b[0]
    >>> matches(b, [])
    True
    >>> b.extend(range(10))
    >>> comparison = range(10)
    >>> matches(b, comparison)
    True
    >>> b.reverse()
    >>> comparison.reverse()
    >>> matches(b, comparison)
    True
    >>> for i in range(10):
    ...     b[i] = i+10
    ...     comparison[i] = i+10
    ...
    >>> matches(b, comparison)
    True
    >>> b[5:10] = [9, 8, 7, 6, 5]
    >>> comparison[5:10] = [9, 8, 7, 6, 5]
    >>> matches(b, comparison)
    True
    >>> b[0:0] = [-3, -2, -1]
    >>> comparison[0:0] = [-3, -2, -1]
    >>> matches(b, comparison)
    True
    >>> b.extend(range(90, 100))
    >>> comparison.extend(range(90,100))
    >>> matches(b, comparison)
    True
    >>> b[10:10] = range(20, 90)
    >>> comparison[10:10] = range(20, 90)
    >>> matches(b, comparison)
    True
    >>> b[b.index(82)]
    82
    >>> del b[:4]
    >>> del comparison[:4]
    >>> matches(b, comparison)
    True
    >>> comparison[2:10:2] = [100, 102, 104, 106]
    >>> b[2:10:2] = [100, 102, 104, 106]
    >>> matches(b, comparison)
    True
    >>> del b[1:88]
    >>> del comparison[1:88]
    >>> matches(b, comparison)
    True
    >>> list(b[:])
    [11, 99]
    >>> b[0] = 0
    >>> b[2] = 100
    >>> b[3] = 101
    >>> b[4] = 102
    >>> matches(b, [0, 99, 100, 101, 102])
    True

Switching two values is most efficiently done with slice notation.

    >>> b[:] = range(1000)
    >>> b[5:996:990] = (b[995], b[5])
    >>> list(b[:7])
    [0, 1, 2, 3, 4, 995, 6]
    >>> list(b[994:])
    [994, 5, 996, 997, 998, 999]
    >>> comparison = range(1000)
    >>> comparison[5] = 995
    >>> comparison[995] = 5
    >>> matches(b, comparison)
    True

We'll test some of the other methods

    >>> b.pop(995) == comparison.pop(995)
    True
    >>> matches(b, comparison)
    True
    >>> b.insert(995, 5)
    >>> comparison.insert(995, 5)
    >>> matches(b, comparison)
    True

These are some more stress and regression tests.

    >>> del b[900:]
    >>> del comparison[900:]
    >>> matches(b, comparison)
    True

    >>> del comparison[::2]
    >>> del b[::2] # 1
    >>> matches(b, comparison)
    True
    >>> del b[::2] # 2
    >>> del comparison[::2]
    >>> matches(b, comparison)
    True
    >>> del b[::2] # 3
    >>> del comparison[::2]
    >>> matches(b, comparison)
    True

XXX lots more to test, especially exceptions.

.. [#matches] 
    >>> def checkIndex(ix, b, previous, previous_ix=0):
    ...     computed = 0
    ...     if len(previous) < previous_ix+1:
    ...         previous.append(None)
    ...         assert len(previous) >= previous_ix + 1
    ...     # assert isinstance(ix, zc.blist.Index)
    ...     assert b.data is ix or len(ix) <= b.index_size
    ...     assert b.data is ix or len(ix) >= b.index_size // 2
    ...     assert ix.minKey() == 0
    ...     for k, v in ix.items():
    ...         v = b._mapping[v]
    ...         assert computed == k
    ...         assert v.parent == ix.identifier
    ...         p = previous[previous_ix]
    ...         if p is not None:
    ...             p = p.identifier
    ...         assert v.previous == p
    ...         assert (v.previous is None or
    ...                 previous[previous_ix].next == v.identifier)
    ...         assert (v.next is None or
    ...                 b._mapping[v.next].previous == v.identifier)
    ...         computed += v.contained_len(b)
    ...         if isinstance(v, zc.blist.Index):
    ...             checkIndex(v, b, previous, previous_ix+1)
    ...         else:
    ...             assert isinstance(v, zc.blist.Bucket)
    ...             assert len(v) <= b.bucket_size
    ...             assert len(v) >= b.bucket_size // 2
    ...         previous[previous_ix] = v
    ...     
    >>> def matches(b, result):
    ...     assert list(b) == result, repr(list(b)) + ' != ' + repr(result)
    ...     res = []
    ...     for i in range(len(b)):
    ...         res.append(b[i])
    ...     assert res == result, repr(res) + ' != ' + repr(result)
    ...     #assert set(result) == set(b.children)
    ...     #children_errors = [(k, [b._mapping.get(i) for i in v]) for k, v in
    ...     #                   b.children.items() if len(v) != 1]
    ...     #assert children_errors == [], repr(children_errors)
    ...     # we'll check the buckets internally while we are here
    ...     assert b.data.parent is None
    ...     assert b.data.previous is None and b.data.next is None
    ...     if isinstance(b.data, zc.blist.Index):
    ...         checkIndex(b.data, b, [None])
    ...     return True
    ...
