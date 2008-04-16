from zope.cachedescriptors import property

from z3c.metrics import scale

import DateTime

epoch = DateTime.DateTime(0)
one_year = 365

class ExponentialDateTimeScale(scale.ExponentialDatetimeScale):

    def __init__(self, scale_unit=one_year, scale_ratio=2,
                 start=epoch, min_unit=None):
        super(ExponentialDateTimeScale, self).__init__(
            scale_unit=scale_unit, scale_ratio=scale_ratio,
            start=start, min_unit=min_unit)

    @property.readproperty
    def default(self):
        return DateTime.DateTime()

    def _fromDelta(self, delta):
        """DateTime deltas are just a float of days"""
        return delta

    def _toDelta(self, quantity):
        """DateTime deltas are just a float of days"""
        return quantity
