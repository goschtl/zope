##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
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
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ITZInfo(request))
    return dt.astimezone(pytz.utc)
