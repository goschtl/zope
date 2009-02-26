##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Special ExtJS data converters

$Id$
"""

import zope.i18n.format
from z3c.form import converter
from z3c.formext import interfaces

class ExtJSDateDataConverter(converter.CalendarDataConverter):
    zope.component.adapts(
        zope.schema.interfaces.IDate, interfaces.IExtJSDateWidget)
    type = "date"

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return self.formatter.format(value, pattern="MM/dd/yyyy")

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        try:
            # Note: use ExtJS.DateField.format = 'm/d/Y', not the default!
            return self.formatter.parse(value, pattern="MM/dd/yyyy")
        except zope.i18n.format.DateTimeParseError, err:
            raise converter.FormatterValidationError(err.args[0], value)


class ExtJSSingleCheckBoxDataConverter(converter.BaseDataConverter):
    zope.component.adapts(
        zope.schema.interfaces.IBool, interfaces.IExtJSSingleCheckBoxWidget)

    def toWidgetValue(self, value):
        """Convert from Python bool to HTML representation."""
        if value:
            return 'on'
        return 'off'

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == 'on':
            return True
        return False
