##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Widgets for enumerated field flavours.

$Id: enumerated.py,v 1.2 2004/03/17 17:37:03 philikon Exp $
"""

from zope.app.form.browser.textwidgets import TextWidget
from zope.app.form.browser.textwidgets import IntWidget, FloatWidget
from zope.app.form.browser.textwidgets import DatetimeWidget, DateWidget

__metaclass__ = type

class Enumerated:
    """Mixin for enumerated field widgets
    """
    def __init__(self, *args):
        super(Enumerated, self).__init__(*args)
        field = self.context
        if field.allowed_values is not None:
            values = []
            # if field is optional and missing_value isn't in
            # allowed_values, add an additional option at top to represent
            # field.missing_value
            if not field.required and \
                field.missing_value not in field.allowed_values:
                values.append(field.missing_value)
            values += list(field.allowed_values)
            self.__values = values

    def __call__(self):
        selected = self._showData()
        result = ['<select id="%s" name="%s">' % (self.name, self.name)]
        for value in self.__values:
            unconverted = self._unconvert(value)
            selectedStr = unconverted == selected and ' selected' or ''
            result.append('<option value="%s"%s>%s</option>' % \
                   (unconverted, selectedStr, unconverted))
        result.append('</select>')
        return '\n\t'.join(result)

class EnumeratedTextWidget(Enumerated, TextWidget):
    """EnumeratedText widget (for TextLines)
    """

class EnumeratedIntWidget(Enumerated, IntWidget):
    """EnumeratedInt widget
    """

class EnumeratedFloatWidget(Enumerated, FloatWidget):
    """EnumeratedFloat widget
    """

class EnumeratedDatetimeWidget(Enumerated, DatetimeWidget):
    """EnumeratedDatetime widget
    """

class EnumeratedDateWidget(Enumerated, DateWidget):
    """EnumeratedDate widget
    """
