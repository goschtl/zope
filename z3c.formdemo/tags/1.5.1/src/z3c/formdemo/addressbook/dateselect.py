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
"""Date Selection

$Id$
"""
__docformat__ = "reStructuredText"
import datetime
import zope.component
import zope.interface
import zope.schema
from zope.schema import vocabulary
from z3c.form import interfaces, widget
from z3c.form.browser import select


class DateSelectWidget(widget.Widget):

    selects = ( ('year', range(1920, 2011), 0),
                ('month', range(1, 13), 1),
                ('day', range(1, 32), 2) )

    def update(self):
        for (name, options, loc) in self.selects:
            selectWidget = select.SelectWidget(self.request)
            selectWidget.terms = vocabulary.SimpleVocabulary.fromValues(options)
            selectWidget.required = True
            selectWidget.name = self.name + '.' + name
            selectWidget.id = selectWidget.name.replace('.', '-')
            selectWidget.klass = name
            setattr(self, name, selectWidget)

        super(DateSelectWidget, self).update()

        for (name, options, loc) in self.selects:
            selectWidget = getattr(self, name)
            if self.value and not selectWidget.value:
                selectWidget.value = (self.value[loc],)
            selectWidget.update()


    def extract(self, default=interfaces.NOVALUE):
        """See z3c.form.interfaces.IWidget."""
        value = (self.year.extract(default),
                 self.month.extract(default),
                 self.day.extract(default))
        if default in value:
            return default
        return value


@zope.component.adapter(zope.schema.interfaces.IDate, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def DateSelectFieldWidget(field, request):
    """IFieldWidget factory for DateSelectWidget."""
    return widget.FieldWidget(field, DateSelectWidget(request))


class DateSelectDataConverter(object):
    zope.component.adapts(zope.schema.interfaces.IDate, DateSelectWidget)
    zope.interface.implements(interfaces.IDataConverter)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return None
        return (str(value.year), str(value.month), str(value.day))

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == None:
            return self.field.missing_value
        return datetime.date(*[int(part[0]) for part in value])
