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
methods.  __eq__ compares identity.

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
  brute force, and in Python. In contrast, lists and tuples will load all
  items, and is brute force in C.

The Bad
=======

- This will create a lot of Persistent objects for one blist, which may cause
  cache eviction problems depending on circumstances and usage.

- Did I mention that this was in Python, not C?  That's fixable, at least.

