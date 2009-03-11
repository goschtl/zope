##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" ``dateTime`` formatter implementation
Author: Nikolay Kim <fafhrd91@gmail.com>

$Id$
"""
from pytz import utc, timezone
from datetime import datetime

from zope import interface, component
from zope.component import getUtility
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.http import IHTTPRequest

from interfaces import IFormatter, IFormatterFactory, IFormatterConfiglet


class DatetimeFormatter(object):
    interface.implements(IFormatter)

    def __init__(self, request, *args):
        try:
            self.tp = args[0]
        except:
            self.tp = 'medium'

        self.request = request
        self.formatter = request.locale.dates.getFormatter('dateTime', self.tp)

    def format(self, value):
        formatter = self.formatter

        configlet = getUtility(IFormatterConfiglet)
        tz = None
        if configlet.principalTimezone:
            tz = ITZInfo(self.request.principal, None)

        if tz is None:
            tz = timezone(configlet.timezone)

        if value.tzinfo is None:
            value = datetime(value.year, value.month, value.day, value.hour,
                             value.minute, value.second, value.microsecond, utc)

        value = value.astimezone(tz)

        if configlet.timezoneFormat == 3:
            if self.tp in ('medium', 'full'):
                formatter.setPattern(
                    formatter.getPattern().replace('z', '').strip())
                formatted = formatter.format(value)
                return u'%s %s'%(formatted, tz.zone)

        return formatter.format(value)


class DatetimeFormatterFactory(object):
    component.adapts(IHTTPRequest)
    interface.implements(IFormatterFactory)

    def __init__(self, request):
        self.request = request
        
    def __call__(self, *args, **kw):
        return DatetimeFormatter(self.request, *args)
