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
$Id: FormView.py,v 1.5 2002/07/16 23:42:58 srichter Exp $
"""
from Interface.Implements import flattenInterfaces
from Schema.IField import IField

from Zope.ComponentArchitecture import getView
from Zope.Publisher.Browser.BrowserView import BrowserView

from IForm import IForm


class FormView(BrowserView):
    """A View that represents a complete HTML Form based on the Schema of the
    object."""
    __implements__ = IForm

    form = None
    custom_widgets = None

    def getFields(self):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        interfaces = self.context.__implements__
        if isinstance(interfaces, (tuple, list)):
            interfaces = flattenInterfaces(interfaces)
        else:
            interfaces = (interfaces,)
        request = self.request
        fields = []
        for interface in interfaces:
            for name in interface.names(1):
                attr = interface.getDescriptionFor(name)
                if IField.isImplementedBy(attr):
                    fields.append(attr)
        return fields


    def getWidgetForFieldId(self, id):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        # XXX This needs to be optimized!
        field = None
        for f in self.getFields():
            if f.id == id:
                field = f
        if field is None:
            raise KeyError, 'Field id "%s" does not exist.' %id
        return self.getWidgetForField(field)


    def getWidgetForField(self, field):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        if self.custom_widgets is not None and \
           field.id in self.custom_widgets.keys():
            return self.custom_widgets[field.id](field, self.request)
        return getView(field, 'widget', self.request)


    def renderField(self, field):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        widget = self.getWidgetForField(field)
        value = self.request.form.get('field_' + field.id)
        if value is None:
            value = getattr(self.context, field.id)
        return widget.render(value)


    def getAllRawFieldData(self):
        """Returns field data retrieved from request."""
        interfaces = _flatten(self.context.__implements__)
        request = self.request
        data = {}
        for field in self.getFields():
            raw_data = request.form.get('field_' + attr.get('id'))
            data[attr] = raw_data
        return data


    def convertAllFieldData(self, mapping):
        """Convert the raw data into valid objects."""
        data = {}
        errors = []
        for field in mapping:
            widget = self.getWidgetForField(field)
            try:
                data[field] = widget.convert(mapping[field])
            except ConversionError, error:
                errors.append((field.get('id'), error))

        if errors:
            raise ConversionErrorsAll, errors
        
        return data
            

    def validateAllFieldData(self, mapping):
        """Validate all the data."""
        errors = []
        for field in mapping:
            try:
                field.validate(mapping[field])
            except ValidationError, error:
                errors.append((field.get('id'), error))

        if errors:
            raise ValidationErrorsAll, errors


    def storeAllDataInContext(self, mapping):
        """Store the data back into the context object."""
        for field in mapping:
            value = mapping[field]
            if value != getattr(self, field.get('id')):
                setattr(self, field.get('id'))


    def saveValuesInContext(self):
        'See Zope.App.Forms.Views.Browser.IForm.IWriteForm'
        data = self.getAllRawFieldData()
        data = self.convertAllFieldData(data)
        self.validateAllFieldData(data)
        self.storeAllDataInContext(data)


    def action(self):
        'See Zope.App.Forms.Views.Browser.IForm.IWriteForm'
        try:
            self.saveValuesInContext()
        except Error, e:
            errors = e
        else:
            return self.request.response.redirect(self.request.URL[-1])
        
