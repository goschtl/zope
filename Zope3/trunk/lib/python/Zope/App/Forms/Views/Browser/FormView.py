##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: FormView.py,v 1.4 2002/07/16 14:03:02 srichter Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Interface import Interface
from Schema.IField import IField
from Zope.ComponentArchitecture import getView
import Schema
from IForm import IForm

class FormView(BrowserView):

    __implements__ = IForm, BrowserView.__implements__

    schema = None
    custom_widgets = None

    def getWidgetForFieldId(self, id):
        field = self.schema[id]
        return self.getWidgetForField(field)


    def getWidgetForField(self, field):
        if self.custom_widgets is not None and \
           field.getValue('id') in custom_widgets.keys():
            return custom_widgets[field.getValue('id')](field)

        return getView(field, 'widget', self.request)

    def getFieldData(self):
        result = {}
        request = self.request

        for name in schema.names(1):
            field = schema.getDescriptionFor(name)

            if IField.isImplementedBy(field):
                widget = self.getWidgetForField(field)
                result[field.getValue(id)] = widget.convert(request)

        return result


    def saveValuesInContext(self, mapping):
        """Store all the new data inside the context object."""
        for item in mapping.items():
            if getattr(self.context, item[0]) != item[1]:
                setattr(self.context, attr, mapping[attr])


    def action(self):
        """Execute the form. By default it tries to save the values back
           into the content object."""
        data = self.getFieldData()
        try:
            Schema.validateMappingAll(self.schema, self.getFieldData())
        except ValidationErrorsAll, errors:
            # display the form again
            pass
        else:
            self.saveValuesInContext(data)
