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

        d1 = datetime.now(utc)
        d2 = value.astimezone(utc)

        delta = d1 - d2

        years, months, weeks, hours, minutes = (
            delta.days/365, delta.days/30, delta.days/7,
            delta.seconds/3600, delta.seconds/60)

        if years > 0:
            return translate(
                u'${value} year(s) ago', 'z3ext.formatter',
                mapping={'value': years})

        if months > 0:
            return translate(u'${value} month(s) ago', 'z3ext.formatter',
                             mapping={'value': months})

        if weeks > 0:
            return translate(u'${value} week(s) ago', 'z3ext.formatter',
                             mapping={'value': weeks})

        if delta.days > 0:
            return translate(u'${value} day(s) ago', 'z3ext.formatter',
                             mapping={'value': delta.days})

        if hours > 0:
            return translate(u'${value} hour(s) ago', 'z3ext.formatter',
                             mapping={'value': hours})

        if minutes > 0:
            return translate(u'${value} minute(s) ago', 'z3ext.formatter',
                             mapping={'value': minutes})

        return translate(u'${value} second(s) ago', 'z3ext.formatter',
                         mapping={'value': delta.seconds})


class HumanDatetimeFormatterFactory(object):
    component.adapts(IHTTPRequest)
    interface.implements(IFormatterFactory)

    def __init__(self, request):
        self.request = request

    def __call__(self, *args, **kw):
        return HumanDatetimeFormatter(self.request, *args)
