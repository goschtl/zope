##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""'format' TALES Namespace Adapter implementation

$Id: __init__.py,v 1.1 2003/09/16 22:18:56 srichter Exp $
"""
from zope.interface import implements
from zope.tales.interfaces import ITALESFunctionNamespace
from zope.security.proxy import removeSecurityProxy
from interfaces import IFormatTalesAPI


class FormatTalesAPI(object):

    implements(IFormatTalesAPI, ITALESFunctionNamespace)

    def __init__(self, context):
        self.context = context

    def setEngine(self, engine):
        """See zope.tales.interfaces.ITALESFunctionNamespace"""
        self.locale = removeSecurityProxy(engine.vars['request']).locale

    def shortDate(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'date', 'short').format(self.context)
        
    def mediumDate(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'date', 'medium').format(self.context)
        
    def longDate(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'date', 'long').format(self.context)

    def fullDate(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'date', 'full').format(self.context)

    def shortTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'time', 'short').format(self.context)

    def mediumTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'time', 'medium').format(self.context)

    def longTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'time', 'long').format(self.context)

    def fullTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'time', 'full').format(self.context)

    def shortDateTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'dateTime', 'short').format(self.context)

    def mediumDateTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'dateTime', 'medium').format(self.context)

    def longDateTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'dateTime', 'long').format(self.context)

    def fullDateTime(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.dates.getFormatter(
            'dateTime', 'full').format(self.context)

    def decimal(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.numbers.getFormatter(
            'decimal').format(self.context)

    def percent(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.numbers.getFormatter(
            'percent').format(self.context)

    def scientific(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.numbers.getFormatter(
            'scientific').format(self.context)

    def currency(self):
        """See book.formatns.interfaces.IFormatTalesAPI"""
        return self.locale.numbers.getFormatter(
            'currency').format(self.context)
