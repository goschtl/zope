import math, datetime, time

from zope import interface
from zope.cachedescriptors import property
import persistent

from z3c.metrics import interfaces

inf = 1e1000000

class ExponentialScale(persistent.Persistent):
    interface.implements(interfaces.IScale)

    origin = 1

    @property.readproperty
    def default(self):
        return self.start

    def __init__(self, scale_unit=1, scale_ratio=2,
                 start=1, min_unit=None):
        self.scale_unit = self._fromDelta(scale_unit)
        self.scale_ratio = scale_ratio
        self.start = start
        if min_unit is not None:
            self.min_unit = self._fromDelta(min_unit)
            self.origin = getOrigin(
                self.min_unit, self.scale_unit, scale_ratio)

    def _fromDelta(self, delta):
        return delta

    def _toDelta(self, quantity):
        return quantity

    def fromValue(self, value):
        return self.origin*self.scale_ratio**(
            self._fromDelta(value-self.start)/float(self.scale_unit))

    def toValue(self, scaled):
        return self.start + self._toDelta(
            math.log(scaled/float(self.origin),
                     self.scale_ratio)*self.scale_unit)

    def normalize(self, raw, query=None):
        if query is None:
            query = self.default
        return raw/float(self.fromValue(query))

def getOrigin(min_unit, scale_unit, scale_ratio):
    """
    The scale ratio to the power of the proportion of the minimum
    guaranteed granularity to the scale unit is the proportion of the
    number after the origin to the origin.

    scale_ratio**(min_unit/scale_unit) == origin+1/origin

    Solve the above for origin.

    scale_ratio**(min_unit/scale_unit) == 1+1/origin

    scale_ratio**(min_unit/scale_unit)-1 == 1/origin
    """
    return 1/(scale_ratio**(
        min_unit/float(scale_unit))-1)
    
def getRatio(scaled, scale_units, scale_unit, min_unit=None):
    """
    Return the ratio such that the number of units will result in
    scaled.

    scaled == origin*scale_ratio**units

    scaled == scale_ratio**units/(
        scale_ratio**(min_unit/scale_unit)-1)

    scaled*(scale_ratio**(
        min_unit/scale_unit)-1) == scale_ratio**units
    
    scale_ratio**(min_unit/scale_unit)-1 == scale_ratio**units/scaled

    ----------------------------

    units == math.log(scaled/origin, scale_ratio)

    units == math.log(
    scaled*(scale_ratio**(min_unit/scale_unit)-1), scale_ratio)

    1 == math.log(
    (scaled*(scale_ratio**(min_unit/scale_unit)-1))**(1/unit), scale_ratio)

    scale_ratio**units == scaled*(scale_ratio**(min_unit/scale_unit)-1)
    """
    raise NotImplementedError

epoch = datetime.datetime(*time.gmtime(0)[:3])
one_day = datetime.timedelta(1)
one_year = one_day*365
seconds_per_day = 24*60*60

class ExponentialDatetimeScale(ExponentialScale):

    def __init__(self, scale_unit=one_year, scale_ratio=2,
                 start=epoch, min_unit=None):
        super(ExponentialDatetimeScale, self).__init__(
            scale_unit=scale_unit, scale_ratio=scale_ratio,
            start=start, min_unit=min_unit)

    @property.readproperty
    def default(self):
        return datetime.datetime.now()

    def _fromDelta(self, delta):
        """Convert a time delta into a float of seconds"""
        return (delta.days*seconds_per_day + delta.seconds +
                delta.microseconds/float(1000000))

    def _toDelta(self, quantity):
        return datetime.timedelta(seconds=quantity)
