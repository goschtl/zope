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
import os
import unittest
import random
import sys
import traceback

from zope.testing import doctest

import zc.blist
import zc.blist.testing

def by_hand_regression_test():
    """
    ==================
    Regression Testing
    ==================
    
    We'll use a `matches` function to compare a bucket sequence with a standard
    Python list to which the same modifications have made.  This also checks for
    bucket health.
    
        >>> import zc.blist
        >>> from zc.blist.testing import matches, checkIndex
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
    
        >>> alt = zc.blist.BList(b)
        >>> alt_comp = comparison[:]
        >>> matches(b, comparison)
        True
        >>> del alt[::3]
        >>> del alt_comp[::3]
        >>> matches(alt, alt_comp)
        True
        >>> del alt[::3]
        >>> del alt_comp[::3]
        >>> matches(alt, alt_comp)
        True
        >>> del alt[-1:5:-2]
        >>> del alt_comp[-1:5:-2]
        >>> matches(alt, alt_comp)
        True
    
    The ``copy`` method gives a complete copy, reusing buckets and indexes.
    
        >>> from zc.blist.testing import checkCopies
        >>> old_comparison = comparison[:]
        >>> new = b.copy()
        >>> new == b
        True
        >>> def check():
        ...     assert matches(new, comparison)
        ...     assert matches(b, old_comparison)
        ...     return checkCopies(b, new)
        ...

    So, ``checkCopies`` and ``check`` return three lists: the bucket
    identifiers that are only in b, the bucket identifiers that are only in
    new, and the bucket identifiers that are in both, but different. Initially,
    all three lists are empty, because the two blists share all buckets and
    indexes.

        >>> check()
        ([], [], [])
        >>> del new[4]
        >>> del comparison[4]
        >>> [len(v) for v in check()] # 4 = 1 bucket, 3 indexes
        [0, 0, 4]
        >>> del old_comparison[10]
        >>> del b[10]
        >>> [len(v) for v in check()]
        [0, 1, 9]
        >>> new.append(999999999)
        >>> comparison.append(999999999)
        >>> [len(v) for v in check()]
        [0, 1, 10]
        >>> new.extend(range(5000, 5100))
        >>> comparison.extend(range(5000, 5100))
        >>> [len(v) for v in check()]
        [0, 27, 13]
        >>> del new[15:50]
        >>> del comparison[15:50]
        >>> [len(v) for v in check()]
        [20, 27, 16]
        >>> del new[::3]
        >>> del comparison[::3]
        >>> [len(v) for v in check()]
        [35, 26, 28]
        >>> del new[::2]
        >>> del comparison[::2]
        >>> [len(v) for v in check()]
        [56, 19, 10]
        >>> del new[-1:5:-2]
        >>> del comparison[-1:5:-2]
        >>> [len(v) for v in check()]
        [56, 7, 10]
    """

class Canary(object):
    def __init__(self, comp, blist = None):
        if blist is None:
            blist = zc.blist.BList(comp)
        self.blist = blist
        self.comp = comp
        self.ops = [getattr(self, n) for n in dir(self) if n.startswith('t_')]
        self.empty_ops = [getattr(self, n) for n in dir(self) if n.startswith('e_')]
        self.ops.extend(self.empty_ops)

    def __call__(self, count=100):
        for i in range(count):
            if len(self.comp):
                c = random.choice(self.ops)
            else:
                c = random.choice(self.empty_ops)
            self.run(c)

    def run(self, call):
        orig = self.blist.copy()
        orig_comp = self.comp[:]
        try:
            zc.blist.testing.checkCopies(self.blist, orig) # initial
            args = call()
            zc.blist.testing.matches(self.blist, self.comp)
            zc.blist.testing.matches(orig, orig_comp)
            return zc.blist.testing.checkCopies(self.blist, orig) # post
        except Exception, e:
            traceback.print_exc()
            import pdb; pdb.post_mortem(sys.exc_info()[2])
            raise

    def _getval(self):
        return random.randint(-sys.maxint, sys.maxint)

    def _getloc(self, adjustment=-1):
        max = len(self.comp)+adjustment
        if max <= 1:
            return 0
        return random.randint(0, max)

    def _get_start_stop(self):
        if not self.comp:
            return 0, 0
        max = len(self.comp)-1
        start = random.randint(0, max)
        if start == max:
            stop = start
        else:
            stop = random.randint(start, max)
        if random.choice((True, False)):
            start -= len(self.comp)
        if random.choice((True, False)):
            stop -= len(self.comp)
        return start, stop

    def _get_start_stop_step(self):
        if not self.comp:
            return 0, 0, 1
        max = len(self.comp)-1
        start = random.randint(0, max)
        step = 1
        if start == max:
            stop = start
        else:
            stop = random.randint(start, max)
            if stop-start > 1:
                step = random.randint(1, stop-start)
        if random.choice((True, False)):
            start -= len(self.comp)
        if random.choice((True, False)):
            stop -= len(self.comp)
        if random.choice((True, False)):
            stop, start = start, stop
            step = -step
        return start, stop, step

    def _getvals(self):
        return [self._getval() for i in range(random.randint(1, 100))]

    def e_append(self):
        val = self._getval()
        self.comp.append(val)
        self.blist.append(val)
        return (val,)

    def e_extend(self):
        new = self._getvals()
        self.comp.extend(new)
        self.blist.extend(new)
        return (new,)

    def e_iadd(self):
        new = self._getvals()
        self.comp += new
        self.blist += new
        return (new,)

    def e_insert(self):
        val = self._getval()
        location = self._getloc(0) # can insert after last item
        self.comp.insert(location, val)
        self.blist.insert(location, val)
        return location, val

    def t_delitem(self):
        location = self._getloc()
        del self.comp[location]
        del self.blist[location]
        return (location,)

    def t_delslice(self):
        start, stop = self._get_start_stop()
        del self.comp[start:stop]
        del self.blist[start:stop]
        return start, stop

    def t_delslice_step(self):
        start, stop, step = self._get_start_stop_step()
        del self.comp[start:stop:step]
        del self.blist[start:stop:step]
        return start, stop, step

    def e_delslice_noop(self):
        stop, start = self._get_start_stop()
        del self.comp[start:stop]
        del self.blist[start:stop]
        return start, stop

    def e_delslice_step_noop(self):
        stop, start, step = self._get_start_stop_step()
        del self.comp[start:stop:step]
        del self.blist[start:stop:step]
        return start, stop, step

    def t_pop(self):
        location = self._getloc()
        assert self.comp.pop(location) == self.blist.pop(location)
        return (location,)

    def t_remove(self):
        val = self.comp[self._getloc()]
        self.comp.remove(val)
        self.blist.remove(val)
        return (val,)

    def t_reverse(self):
        self.comp.reverse()
        self.blist.reverse()
        return ()

    def t_sort(self):
        self.comp.sort()
        self.blist.sort()
        return ()

    def t_sort_cmp(self):
        self.comp.sort(lambda s, o: cmp(str(o), str(s))) # reverse, by
        self.blist.sort(lambda s, o: cmp(str(o), str(s))) # string
        return ()

    def t_sort_key(self):
        self.comp.sort(key=lambda v: str(v))
        self.blist.sort(key=lambda v: str(v))
        return ()

    def t_sort_reverse(self):
        self.comp.sort(reverse = True)
        self.blist.sort(reverse = True)
        return ()

    def t_setitem(self):
        location = self._getloc()
        val = self._getval()
        self.comp[location] = val
        self.blist[location] = val
        return location, val

    def e_setitem_slice(self):
        start, stop = self._get_start_stop()
        vals = self._getvals()
        self.comp[start:stop] = vals
        self.blist[start:stop] = vals
        return start, stop, vals

    def e_setitem_slice_step(self):
        start, stop, step = self._get_start_stop_step()
        vals = [self._getval() for i in range(len(self.comp[start:stop:step]))]
        self.comp[start:stop:step] = vals
        self.blist[start:stop:step] = vals
        return start, stop, step, vals

class CanaryTestCase(unittest.TestCase):
    def test_empty_canary(self):
        c = Canary([])
        c()

    def test_small_bucket_empty_canary(self):
        c = Canary([], zc.blist.BList(bucket_size=5, index_size=4))
        c()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocTestSuite(),
        unittest.TestLoader().loadTestsFromTestCase(CanaryTestCase),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
