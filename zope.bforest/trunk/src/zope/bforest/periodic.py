import datetime
import BTrees
import zope.bforest.bforest
import zope.bforest.utils

def mutating(name):
    def mutate(self, *args, **kwargs):
        if (datetime.datetime.now(zope.bforest.utils.UTC) -
            self.last_rotation) >= self._inner_period:
            self.rotateBucket()
        return getattr(super(Abstract, self), name)(*args, **kwargs)
    return mutate

class Abstract(zope.bforest.bforest.AbstractBForest):
    def __init__(self, period, d=None, count=2):
        super(Abstract, self).__init__(d, count)
        self.period = period
        self.last_rotation = datetime.datetime.now(zope.bforest.utils.UTC)

    _inner_period = _period = None
    def period(self, value):
        self._period = value
        self._inner_period = self._period / (len(self.buckets) - 1)
    period = property(
        lambda self: self._period, period)
    
    def copy(self):
        # this makes an exact copy, including the individual state of each 
        # bucket.  If you want a dict, cast it to a dict, or if you want
        # another one of these but with all of the keys in the first bucket,
        # call obj.__class__(obj)
        copy = self.__class__(self.period, count=len(self.buckets))
        for i in range(len(self.buckets)):
            copy.buckets[i].update(self.buckets[i])
        return copy

    def rotateBucket(self):
        super(Abstract, self).rotateBucket()
        self.last_rotation = datetime.datetime.now(zope.bforest.utils.UTC)

    __setitem__ = mutating('__setitem__')
    __delitem__ = mutating('__delitem__')
    pop = mutating('pop')
    popitem = mutating('popitem')
    update = mutating('update')

class IOBForest(Abstract):
    _treemodule = BTrees.family32.IO

class OIBForest(Abstract):
    _treemodule = BTrees.family32.OI

class IIBForest(Abstract):
    _treemodule = BTrees.family32.II

class LOBForest(Abstract):
    _treemodule = BTrees.family64.IO

class OLBForest(Abstract):
    _treemodule = BTrees.family64.OI

class LLBForest(Abstract):
    _treemodule = BTrees.family64.II

class OOBForest(Abstract):
    _treemodule = BTrees.family32.OO
