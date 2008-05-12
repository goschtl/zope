##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
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
"""\
Utility functions for parsing ISO 8601 values.

"""
__docformat__ = "reStructuredText"

import datetime
import pytz
import re


_tz_re = "(?:Z|(?P<tzdir>[-+])(?P<tzhour>\d\d):(?P<tzmin>\d\d))"

# "Verbose" ISO 8601, with hyphens and colons:
_datetime_re1 = """\
    (?P<year>\d\d\d\d)
    -(?P<month>\d\d)
    -(?P<day>\d\d)
    [T\ ]
    (?P<hour>\d\d)
    :(?P<minute>\d\d)
    (?::(?P<second>\d\d(?:\.\d+)?))?
    """ + _tz_re

# "Compact" ISO 8601, without hyphens and colons:
_datetime_re2 = """\
    (?P<year>\d\d\d\d)
    (?P<month>\d\d)
    (?P<day>\d\d)
    [T\ ]
    (?P<hour>\d\d)
    (?P<minute>\d\d)
    (?P<second>\d\d(?:\.\d+)?)?
    """ + _tz_re.replace("):(", "):?(")

_datetime_rx1 = re.compile(_datetime_re1, re.IGNORECASE | re.VERBOSE)
_datetime_rx2 = re.compile(_datetime_re2, re.IGNORECASE | re.VERBOSE)


def datetimetz(string):
    """Parse an ISO 8601 date including timezone information.

    Returns a Python datetime object.

    """
    string = " ".join(string.split())
    m = _datetime_rx1.match(string)
    if m is None:
        m = _datetime_rx2.match(string)
        if m is None:
            raise ValueError("could not parse ISO 8601 datetime: %r" % string)
    year, month, day, hour, minute = map(
        int, m.group("year", "month", "day", "hour", "minute"))
    second = 0
    microsecond = 0
    s = m.group("second")
    if s:
        try:
            second = int(s)
        except ValueError:
            seconds = float(s)
            second = int(seconds)
            # We figure out microseconds this way to avoid floating-point
            # issues.  Anything smaller than one microsecond is simply thrown
            # away.
            fractional = s.split(".")[1]
            while len(fractional) < 6:
                fractional += "0"
            fractional = fractional[:6]
            microsecond = int(fractional)

    if m.group("tzhour"):
        tzhour, tzmin = map(int, m.group("tzhour", "tzmin"))
        offset = (tzhour * 60) + tzmin
        if m.group("tzdir") == "-":
            offset *= -1
        if offset:
            tzinfo = pytz.FixedOffset(offset)
            dt = datetime.datetime(
                year, month, day, hour, minute, second, microsecond,
                tzinfo=tzinfo)
            return dt.astimezone(pytz.UTC)

    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond,
        tzinfo=pytz.UTC)
