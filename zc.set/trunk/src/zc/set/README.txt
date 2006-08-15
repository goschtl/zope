Persistent sets are persistent objects that have the API of standard
Python sets.  The persistent set should work the same as normal sets,
except that changes to them are persistent.

They have the same limitation as persistent lists and persistent
mappings, as found in the `persistent` package: unlike `BTree` package
data structures, changes copy the entire object in the database.  This
generally means that persistent sets, like persistent lists and
persistent mappings, are inappropriate for very large collections.  For
those, use `BTree` data structures.

The rest of this file is tests, not documentation.  Find out about the
Python set API from standard Python documentation
(http://docs.python.org/lib/types-set.html, for instance) and find out about
persistence in the ZODB documentation
(http://www.zope.org/Wikis/ZODB/FrontPage/guide/index.html, for instance).

The persistent set module contains a simple persistent version of a set, that
inherits from persistent.Persistent and marks _p_changed = True for any
potentially mutating operation.

    >>> from ZODB.tests.util import DB
    >>> db = DB()
    >>> conn = db.open()
    >>> root = conn.root()
    >>> import zope.app.folder # import rootFolder
    >>> app = root['Application'] = zope.app.folder.rootFolder()
    >>> import transaction
    >>> transaction.commit()

    >>> from zc.set import Set
    >>> s = Set()
    >>> app['s'] = s
    >>> transaction.commit()

    >>> import persistent.interfaces
    >>> persistent.interfaces.IPersistent.providedBy(s)
    True
    >>> original = factory() # set in one test run; a persistent set in another
    >>> sorted(set(dir(original)) - set(dir(s)))
    []

add sets _p_changed

    >>> s._p_changed = False
    >>> s.add(1) # add
    >>> s._p_changed
    True

__repr__ includes module, class, and a contents view like a normal set
    >>> s # __repr__
    zc.set.Set([1])

update works as normal, but sets _p_changed

    >>> s._p_changed = False
    >>> s.update((2,3,4,5,6,7)) # update
    >>> s._p_changed
    True

__iter__ works

    >>> sorted(s) # __iter__
    [1, 2, 3, 4, 5, 6, 7]

__len__ works

    >>> len(s)
    7

as does __contains__

    >>> 3 in s
    True
    >>> 'kumquat' in s
    False

__gt__, __ge__, __eq__, __ne__, __lt__, and __le__ work normally,
equating with normal set, at least if spelled in the right direction.

    >>> s > original
    True
    >>> s >= original
    True
    >>> s < original
    False
    >>> s <= original
    False
    >>> s == original
    False
    >>> s != original
    True
    
    >>> original.update(s)
    >>> s > original
    False
    >>> s >= original
    True
    >>> s < original
    False
    >>> s <= original
    True
    >>> s == original
    True
    >>> s != original
    False

    >>> original.add(8)
    >>> s > original
    False
    >>> s >= original
    False
    >>> s < original
    True
    >>> s <= original
    True
    >>> s == original
    False
    >>> s != original
    True

I don't know what __cmp__ is supposed to do--it doesn't work with sets--so
I won't test it.

issubset and issuperset work when it is a subset.

    >>> s.issubset(original)
    True
    >>> s.issuperset(original)
    False

__ior__ works, including setting _p_changed

    >>> s._p_changed = False
    >>> s |= original
    >>> s._p_changed
    True
    >>> s == original
    True

issubset and issuperset work when sets are equal.

    >>> s.issubset(original)
    True
    >>> s.issuperset(original)
    True

issubset and issuperset work when it is a superset.

    >>> s.add(9)
    >>> s.issubset(original)
    False
    >>> s.issuperset(original)
    True

__hash__ works, insofar as raising an error as it is supposed to.

    >>> hash(original)
    Traceback (most recent call last):
    ...
    TypeError: set objects are unhashable

__iand__ works, including setting _p_changed

    >>> s._p_changed = False
    >>> s &= original
    >>> s._p_changed
    True
    >>> sorted(s)
    [1, 2, 3, 4, 5, 6, 7, 8]

__isub__ works, including setting _p_changed

    >>> s._p_changed = False
    >>> s -= factory((1, 2, 3, 4, 5, 6, 7))
    >>> s._p_changed
    True
    >>> sorted(s)
    [8]

__ixor__ works, including setting _p_changed

    >>> s._p_changed = False
    >>> s ^= original
    >>> s._p_changed
    True
    >>> sorted(s)
    [1, 2, 3, 4, 5, 6, 7]

difference_update works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.difference_update((7, 8))
    >>> s._p_changed
    True
    >>> sorted(s)
    [1, 2, 3, 4, 5, 6]

intersection_update works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.intersection_update((2, 3, 4, 5, 6, 7))
    >>> s._p_changed
    True
    >>> sorted(s)
    [2, 3, 4, 5, 6]

symmetric_difference_update works, including setting _p_changed

    >>> s._p_changed = False
    >>> original.add(9)
    >>> s.symmetric_difference_update(original)
    >>> s._p_changed
    True
    >>> sorted(s)
    [1, 7, 8, 9]

remove works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.remove(1)
    >>> s._p_changed
    True
    >>> sorted(s)
    [7, 8, 9]

If it raises an error, _p_changed is not set.

    >>> s._p_changed = False
    >>> s.remove(1)
    Traceback (most recent call last):
    ...
    KeyError: 1
    >>> s._p_changed
    False
    >>> sorted(s)
    [7, 8, 9]

discard works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.discard(9)
    >>> s._p_changed
    True
    >>> sorted(s)
    [7, 8]

If you discard something that wasn't in the set, _p_changed will still
be set.  This is an efficiency decision, rather than our desired behavior,
necessarily.

    >>> s._p_changed = False
    >>> s.discard(9)
    >>> s._p_changed
    True
    >>> sorted(s)
    [7, 8]

pop works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.pop() in (7, 8)
    True
    >>> s._p_changed
    True
    >>> len(s)
    1

clear works, including setting _p_changed

    >>> s._p_changed = False
    >>> s.clear()
    >>> s._p_changed
    True
    >>> len(s)
    0

The methods that return sets all return persistent sets.  They otherwise
work identically.

__and__

    >>> s.update((0,1,2,3,4))
    >>> res = s & original
    >>> sorted(res)
    [1, 2, 3, 4]
    >>> res.__class__ is s.__class__
    True

__or__

    >>> res = s | original
    >>> sorted(res)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> res.__class__ is s.__class__
    True

__sub__

    >>> res = s - original
    >>> sorted(res)
    [0]
    >>> res.__class__ is s.__class__
    True

__xor__

    >>> res = s ^ original
    >>> sorted(res)
    [0, 5, 6, 7, 8, 9]
    >>> res.__class__ is s.__class__
    True

__rand__

    >>> res = set((3,4,5)) & s
    >>> sorted(res)
    [3, 4]
    >>> res.__class__ is s.__class__
    True

__ror__

    >>> res = set((3,4,5)) | s
    >>> sorted(res)
    [0, 1, 2, 3, 4, 5]
    >>> res.__class__ is s.__class__
    True

__rsub__

    >>> res = set((3,4,5)) - s
    >>> sorted(res)
    [5]
    >>> res.__class__ is s.__class__
    True

__rxor__

    >>> res = set((3,4,5)) ^ s
    >>> sorted(res)
    [0, 1, 2, 5]
    >>> res.__class__ is s.__class__
    True

difference

    >>> res = s.difference((3,4,5))
    >>> sorted(res)
    [0, 1, 2]
    >>> res.__class__ is s.__class__
    True

intersection

    >>> res = s.intersection((3,4,5))
    >>> sorted(res)
    [3, 4]
    >>> res.__class__ is s.__class__
    True

symmetric_difference

    >>> res = s.symmetric_difference((3,4,5))
    >>> sorted(res)
    [0, 1, 2, 5]
    >>> res.__class__ is s.__class__
    True

union

    >>> res = s.union((3,4,5))
    >>> sorted(res)
    [0, 1, 2, 3, 4, 5]
    >>> res.__class__ is s.__class__
    True

copy returns...a copy.

    >>> res = s.copy()
    >>> res == s
    True
    >>> res.__class__ is s.__class__
    True
