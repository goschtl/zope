"""
Date / time related helper classes for z3checkins.

$Id$
"""

import time
from datetime import tzinfo, timedelta

__metaclass__ = type


class FixedTimezone(tzinfo):
    """Timezone with a fixed UTC offset"""

    def __init__(self, offset=None):
        """Create a timezone with a given UTC offset (minutes east of UTC)."""
        self._offset = offset

    def tzname(self, dt):
        if self._offset >= 0:
            sign = '+'
            h, m = divmod(self._offset, 60)
        else:
            sign = '-'
            h, m = divmod(-self._offset, 60)
        return '%c%02d%02d' % (sign, h, m)

    def utcoffset(self, dt):
        return timedelta(minutes=self._offset)

    def dst(self, dt):
        return timedelta(0)


class RFCDateTimeFormatter:
    """RFC822 view for datetime objects."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        """Render datetime objects in RFC822 format."""
        return self.context.strftime("%a, %d %b %Y %H:%M:%S %z")

    __call__ = __str__


class ISODateTimeFormatter:
    """ISO 8601 view for datetime objects."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if time.localtime()[-1]:
            zone = time.altzone
        else:
            zone = time.timezone
        self.userstz = FixedTimezone(-zone / 60)

    def __str__(self):
        """Render datetime objects as "YYYY-MM-DD hh:mm".

        The result is rendered in the local time zone.
        """
        return self.context.astimezone(self.userstz).strftime("%Y-%m-%d %H:%M")

    __call__ = __str__
