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
""" ``fancyDatetime`` formatter implementation

$Id$
"""

from pytz import utc, timezone
from datetime import datetime
from zope import interface, component
from zope.component import getUtility
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.http import IHTTPRequest

from interfaces import _, IFormatter, IFormatterFactory, IFormatterConfiglet


class FancyDatetimeFormatter(object):
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

        timezoneFormat = configlet.timezoneFormat

        d1 = datetime.now(utc).date()
        d2 = value.astimezone(utc).date()

        delta = d1 - d2

        if delta.days == 0:
            pattern = formatter.getPattern()
            pos = pattern.find('h')
            if pos < 0:
                pos = pattern.find('H')

            formatter.setPattern("'%s '"%_(u'Today at') + pattern[pos:])

        if delta.days == 1:
            pattern = formatter.getPattern()
            pos = pattern.find('h')
            if pos < 0:
                pos = pattern.find('H')

            formatter.setPattern("'%s '"%_(u'Yesterday at') + pattern[pos:])

        if timezoneFormat == 3:
            if self.tp in ('full',):
                formatter.setPattern(
                    formatter.getPattern().replace('z', '').strip())
                formatted = formatter.format(value)
                return u'%s %s'%(formatted, tz.zone)

        return formatter.format(value)


class FancyDatetimeFormatterFactory(object):
    component.adapts(IHTTPRequest)
    interface.implements(IFormatterFactory)

    def __init__(self, request):
        self.request = request
        
    def __call__(self, *args, **kw):
        return FancyDatetimeFormatter(self.request, *args)
