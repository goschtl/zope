##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
""" ``humanDatetime`` formatter implementation

$Id$
"""
from pytz import utc, timezone
from datetime import datetime
from zope import interface, component
from zope.i18n import translate
from zope.component import getUtility
from zope.publisher.interfaces.http import IHTTPRequest

from interfaces import IFormatter, IFormatterFactory, IFormatterConfiglet


class HumanDatetimeFormatter(object):
    interface.implements(IFormatter)

    def __init__(self, request, *args):
        self.request = request

    def format(self, value):
        configlet = getUtility(IFormatterConfiglet)
        tz = timezone(configlet.timezone)

        if value.tzinfo is None:
            value = datetime(value.year, value.month, value.day, value.hour,
                             value.minute, value.second, value.microsecond, tz)

        value = value.astimezone(tz)
        delta = datetime.now(utc) - value.astimezone(utc)

        years, months, weeks, hours, minutes = (
            delta.days/365, delta.days/30, delta.days/7,
            delta.seconds/3600, delta.seconds/60)
        formatted = None
        if years > 0:
            formatted = translate(
                u'${value} year(s) ago', 'z3ext.formatter',
                mapping={'value': years})

        if months > 0:
            formatted = translate(u'${value} month(s) ago', 'z3ext.formatter',
                             mapping={'value': months})
        elif weeks > 0:
            formatted = translate(u'${value} week(s) ago', 'z3ext.formatter',
                             mapping={'value': weeks})
        elif delta.days > 0:
            formatted = translate(u'${value} day(s) ago', 'z3ext.formatter',
                             mapping={'value': delta.days})
        elif hours > 0:
            formatted = translate(u'${value} hour(s) ago', 'z3ext.formatter',
                             mapping={'value': hours})
        elif minutes > 0:
            formatted = translate(u'${value} minute(s) ago', 'z3ext.formatter',
                             mapping={'value': minutes})
        else:
            formatted = translate(u'${value} second(s) ago', 'z3ext.formatter',
                         mapping={'value': delta.seconds})

        return """<span class="z3ext-formatter-humandatetime" value="%s">%s</span>""" \
                % (value.strftime('%Y %B %d %H:%M:%S %Z'), formatted)


class HumanDatetimeFormatterFactory(object):
    component.adapts(IHTTPRequest)
    interface.implements(IFormatterFactory)

    def __init__(self, request):
        self.request = request

    def __call__(self, *args, **kw):
        return HumanDatetimeFormatter(self.request, *args)
