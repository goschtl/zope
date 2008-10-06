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
two--around 50 strings or less--to be rewritten in the database, rather than
the entire contents (which might be thousands of strings, for instance).

If the sequence is most often completely rearranged, the complexity of the code
in this package is not desirable.  It only makes sense if changes most
frequently are fairly small.

One downside is that reading and writing is more work than with a normal list.
If this were to actually gain traction, perhaps writing some or all of it in C
would be helpful.  However, it still seems pretty snappy.

Another downside is the corollary of the bucket advantage listed initially:
with more persistent objects, iterating over it will fill a lot of ZODB's
object cache (which is based on the number of objects cached, rather than the
size). Consider specifying a big object cache if you are using these to store a
lot of data and are frequently iterating or changing.

These sequences return slices as iterators, and add some helpful iteration
methods.  It adds a ``copy`` method that provides a cheap copy of the blist
that shares all buckets and indexes until a write happens, at which point it
copies and mutates the affected indexes and buckets.

We'll take a glance at how these differences work, and then describe the
implementation's basic mechanism, and close with a brief discussion of
performance characteristics in the abstract.

==============================
Differences from Python's List
==============================

Slices are Iterators
====================

This doesn't need much discussion.  Getting slices of all sorts returns
iterators.

    >>> from zc.blist import BList
    >>> l = BList(range(1000))
    >>> l[345:351] # doctest: +ELLIPSIS
    <generator object at ...>
    >>> list(l[345:351])
    [345, 346, 347, 348, 349, 350]

    >>> l[351:345:-1] # doctest: +ELLIPSIS
    <generator object at ...>
    >>> list(l[351:345:-1])
    [351, 350, 349, 348, 347, 346]

    >>> l[345:351:2] # doctest: +ELLIPSIS
    <generator object at ...>
    >>> list(l[345:351:2])
    [345, 347, 349]

Additional Iteration Methods
============================

``iterReversed`` lets you iterate over the list in reverse order, efficiently,
with a given start point.  It is used for slices that proceed with a step of
-1.

    >>> i = l.iterReversed()
    >>> i.next()
    999
    >>> i.next()
    998
    >>> list(i)[-10:]
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

``iterSlice`` lets you iterate over the list with a slice.  It is equivalent to
using a slice with __getitem__.

    >>> i = l.iterSlice(345, 351, 2)
    >>> i # doctest: +ELLIPSIS
    <generator object at ...>
    >>> list(i)
    [345, 347, 349]

Cheap ``copy``
==============

The ``copy`` method produces a cheap copy of the given blist.  All buckets
and indexes are shared until a change is made to either side.  Copies can
safely be made of other copies.

    >>> c = l.copy()
    >>> l == c
    True
    >>> list(c) == list(l)
    True
    >>> del c[10:]
    >>> list(l) == range(1000)
    True
    >>> list(c)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> l == c
    False
    >>> c2 = c.copy()
    >>> c2 == c
    True
    >>> list(c2)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

=========
Mechanism
=========

In its implementation, the sequence is an adapted B+ tree. Indexes are keys, but
each bucket or branch starts at 0. For instance, a perfectly-balanced bucket
sequence with 16 items, and a limit of 3 entries in a bucket or branch, would
have "keys" like this. In the diagram, the top three rows are indexes, and the
bottom row consists of buckets::

        0           8
     0     4     0     4
    0 2   0 2   0 2   0 2
   01 01 01 01 01 01 01 01

So, for instance, you would get the value at position 5 using this process:

- In the top index (the top row, with keys of 0 and 8), find the largest key
  that is lower than the desired position, and use the associated value (index
  or bucket, which is in this case the index represented by the first pair of 0
  and 4 in the second row) for the next step. In this case, the top index has
  keys of 0 and 8, so the largest key lower than position 5 is 0. Subtract this
  key from the position for the next step. This difference will be used as the
  position for the next step. In this case, the next position will be (5-0=) 5.

- The next index has keys of 0 and 4. The largest key lower than 5 is 4. Use
  the child index associated with the 4 key for the next step (the second pair
  of 0 and 2 in the third row), and subtract the key (4) from the position (5)
  for the position to be used in the next step (=1).

- The next index (the second pair of 0 and 2 in the third row) needs to find
  position 1.  This will return the third pair of 0 1 in the last row.  The new
  position will be (1-0=) 1.

- Finally, position 1 in the bottom bucket stores the actual desired value.

This arrangement minimizes the changes to keys necessary when a new value is
inserted low in the sequence: ignoring balancing the tree, only parents and
their subsequent siblings must be adjusted. For instance, inserting a new value
in the 0 position of the bucketsequence described above (the worst case for the
algorithm, in terms of the number of objects touched) would result in the
following tree::

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
  brute force, and in Python. In contrast, lists and tuples will load all
  items (worse), and is brute force in C (better, but not algorithmically).

The Bad
=======

- This will create a lot of Persistent objects for one blist, which may cause
  cache eviction problems depending on circumstances and usage.

- Did I mention that this was in Python, not C?  That's fixable, at least, and
  in fact doesn't appear to be too problematic at the moment, at least for the
  author's usage.

