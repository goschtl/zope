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
""" ``date`` formatter implementation
Author: Nikolay Kim <fafhrd91@gmail.com>

$Id$
"""

from zope import interface, component
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.http import IHTTPRequest

from interfaces import IFormatter, IFormatterFactory


class DateFormatter(object):
    interface.implements(IFormatter)

    def __init__(self, request, *args):
        try:
            self.tp = args[0]
        except:
            self.tp = 'medium'

        self.formatter = request.locale.dates.getFormatter('date', self.tp)

    def format(self, value):
        return self.formatter.format(value)


class DateFormatterFactory(object):
    component.adapts(IHTTPRequest)
    interface.implements(IFormatterFactory)

    def __init__(self, request):
        self.request = request
        
    def __call__(self, *args, **kw):
        return DateFormatter(self.request, *args)
