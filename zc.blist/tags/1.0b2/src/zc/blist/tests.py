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
import pickle
import unittest
import random
import sys
import traceback

from zope.testing import doctest

import zc.blist
import zc.blist.testing


class AbstractCanary(object):
    def __init__(self, comp, blist=None, generator=None):
        if generator is None:
            generator = zc.blist.testing.StringGenerator()
        self.generator = generator
        if blist is None:
            blist = zc.blist.BList(comp)
        self.blist = blist
        self.comp = comp
        zc.blist.testing.matches(self.blist, self.comp)
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
            zc.blist.testing.checkCopies(self.blist, orig) # pre
            c, args = call()
            c()
            zc.blist.testing.matches(self.blist, self.comp)
            zc.blist.testing.matches(orig, orig_comp)
            return zc.blist.testing.checkCopies(self.blist, orig) # post
        except Exception, e:
            traceback.print_exc()
            import pdb; pdb.post_mortem(sys.exc_info()[2])
            orig.bad = self.blist
            orig.args = args
            for i in range(1000):
                nm = 'bad_op_%d_%r.pickle' % (random.randint(1, 1000), call)
                if not os.path.exists(nm):
                    f = open(nm, 'w')
                    pickle.dump(orig, f)
                    f.close()
                    break
            raise

    def _getval(self):
        return self.generator.next()

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


class BigOperationCanary(AbstractCanary):

    def e_extend(self):
        new = self._getvals()
        def test():
            self.comp.extend(new)
            self.blist.extend(new)
        return test, (new,)

    def t_delslice(self):
        start, stop = self._get_start_stop()
        def test():
            del self.comp[start:stop]
            del self.blist[start:stop]
        return test, (start, stop)

    def e_setitem_slice(self):
        start, stop = self._get_start_stop()
        vals = self._getvals()
        def test():
            self.comp[start:stop] = vals
            self.blist[start:stop] = vals
        return test, (start, stop, vals)

    def e_setitem_slice_step(self):
        start, stop, step = self._get_start_stop_step()
        vals = [self._getval() for i in range(len(self.comp[start:stop:step]))]
        def test():
            self.comp[start:stop:step] = vals
            self.blist[start:stop:step] = vals
        return test, (start, stop, step, vals)

    def t_delslice_step(self):
        start, stop, step = self._get_start_stop_step()
        def test():
            del self.comp[start:stop:step]
            del self.blist[start:stop:step]
        return test, (start, stop, step)


class Canary(BigOperationCanary):

    def e_append(self):
        val = self._getval()
        def test():
            self.comp.append(val)
            self.blist.append(val)
        return test, (val,)

    def e_iadd(self):
        new = self._getvals()
        def test():
            self.comp += new
            self.blist += new
        return test, (new,)

    def e_insert(self):
        val = self._getval()
        location = self._getloc(0) # can insert after last item
        def test():
            self.comp.insert(location, val)
            self.blist.insert(location, val)
        return test, (location, val)

    def t_delitem(self):
        location = self._getloc()
        def test():
            del self.comp[location]
            del self.blist[location]
        return test, (location,)

    def e_delslice_noop(self):
        stop, start = self._get_start_stop()
        def test():
            del self.comp[start:stop]
            del self.blist[start:stop]
        return test, (start, stop)

    def e_delslice_step_noop(self):
        stop, start, step = self._get_start_stop_step()
        def test():
            del self.comp[start:stop:step]
            del self.blist[start:stop:step]
        return test, (start, stop, step)

    def t_pop(self):
        location = self._getloc()
        def test():
            assert self.comp.pop(location) == self.blist.pop(location)
        return test, (location,)

    def t_remove(self):
        val = self.comp[self._getloc()]
        def test():
            self.comp.remove(val)
            self.blist.remove(val)
        return test, (val,)

    def t_reverse(self):
        def test():
            self.comp.reverse()
            self.blist.reverse()
        return test, ()

    def t_sort(self):
        def test():
            self.comp.sort()
            self.blist.sort()
        return test, ()

    def t_sort_cmp(self):
        def test():
            self.comp.sort(lambda s, o: cmp(str(o), str(s))) # reverse, by
            self.blist.sort(lambda s, o: cmp(str(o), str(s))) # string
        return test, ()

    def t_sort_key(self):
        def test():
            self.comp.sort(key=lambda v: str(v))
            self.blist.sort(key=lambda v: str(v))
        return test, ()

    def t_sort_reverse(self):
        def test():
            self.comp.sort(reverse = True)
            self.blist.sort(reverse = True)
        return test, ()

    def t_setitem(self):
        location = self._getloc()
        val = self._getval()
        def test():
            self.comp[location] = val
            self.blist[location] = val
        return test, (location, val)


class CanaryTestCase(unittest.TestCase):

    level = 2

    def test_canary(self):
        c = Canary([])
        c()

    def test_small_bucket_empty_canary(self):
        c = Canary([], zc.blist.BList(bucket_size=5, index_size=4))
        c()

    def test_big_canary(self):
        for i in range(32):
            c = Canary([], zc.blist.BList(bucket_size=5, index_size=4))
            c(1000)

    def test_several_small_canaries(self):
        for i in range(128):
            c = Canary([], zc.blist.BList(bucket_size=5, index_size=4))
            c(10)

    def test_big_bigop_canary(self):
        for i in range(32):
            c = BigOperationCanary(
                [], zc.blist.BList(bucket_size=5, index_size=4))
            c(1000)

    def test_big_big_bigop_canary(self):
        for i in range(32):
            c = BigOperationCanary(
                range(10000),
                zc.blist.BList(range(10000), bucket_size=5, index_size=4))
            c(2000)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            'regression.txt',
            optionflags=doctest.INTERPRET_FOOTNOTES),
        unittest.TestLoader().loadTestsFromTestCase(CanaryTestCase),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
