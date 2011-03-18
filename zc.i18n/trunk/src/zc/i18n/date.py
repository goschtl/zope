#############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""

$Id: date.py 2041 2005-06-16 18:34:44Z fred $
"""

import datetime
import pytz
from zope.interface.common.idatetime import ITZInfo

def now(request):
    return datetime.datetime.now(ITZInfo(request))

def format(request, dt=None):
    if dt is None:
        dt = now(request)
    formatter = request.locale.dates.getFormatter(
        'dateTime', 'medium')
    return formatter.format(dt)

def normalize(request, dt):

    """this method normalizes datetime instances by converting them to
    utc, daylight saving times are also taken into account. This
    method requires an adapter to get the tzinfo from the request.

    >>> from zope import component, interface
    >>> import pytz
    >>> from zope.interface.common.idatetime import ITZInfo
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.publisher.browser import TestRequest
    >>> requestTZ = pytz.timezone('Europe/Vienna')
    >>> @interface.implementer(ITZInfo)
    ... @component.adapter(IBrowserRequest)
    ... def tzinfo(request):
    ...     return requestTZ
    >>> component.provideAdapter(tzinfo)
    >>> dt = datetime.datetime(2006,5,1,12)
    >>> request = TestRequest()

    The Vienna timezone has a 2 hour offset to utc at this date.

    >>> normalize(request,dt)
    datetime.datetime(2006, 5, 1, 10, 0, tzinfo=<UTC>)

    At this date the timezone has only a one hour offset.
    >>> dt = datetime.datetime(2006,2,1,12)

    >>> normalize(request,dt)
    datetime.datetime(2006, 2, 1, 11, 0, tzinfo=<UTC>)

    Normalizing UTC to UTC should work also
    >>> dt = datetime.datetime(2006,5,1,12,tzinfo=pytz.UTC)
    >>> normalize(request,dt)
    datetime.datetime(2006, 5, 1, 12, 0, tzinfo=<UTC>)

    This way too UTC to UTC
    >>> requestTZ = pytz.UTC
    >>> dt = datetime.datetime(2006,5,1,12)
    >>> normalize(request,dt)
    datetime.datetime(2006, 5, 1, 12, 0, tzinfo=<UTC>)

    Just so you would know that these are possible -

    The time that does not exist (defaulting to is_dst=False will raise an
    index error in this case):

    >>> requestTZ = pytz.timezone('Europe/Vilnius')
    >>> dt = datetime.datetime(2006,3,26,3,30)
    >>> normalize(request,dt)
    Traceback (most recent call last):
    ...
    NonExistentTimeError: 2006-03-26 03:30:00

    An ambiguous time:

    >>> dt = datetime.datetime(2006,10,29,3,30)
    >>> normalize(request,dt)
    Traceback (most recent call last):
    ...
    AmbiguousTimeError: 2006-10-29 03:30:00

    """

    if dt.tzinfo is None:
        tzinfo = ITZInfo(request)
        dt = tzinfo.localize(dt, is_dst=None)

    return dt.astimezone(pytz.utc)
