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
$Id: FormView.py,v 1.10 2002/09/04 13:44:23 faassen Exp $
"""
from Schema.IField import IField
from Schema.Exceptions import StopValidation, ValidationError, \
     ConversionError, ValidationErrorsAll, ConversionErrorsAll
from Schema import getFields, validateMappingAll
#from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ComponentArchitecture import getView
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Publisher.Browser.BrowserView import BrowserView

from IForm import IForm


class FormView(BrowserView):
    """A View that represents a complete HTML Form based on the Schema of the
    object."""
    __implements__ = IForm

    form = None
    custom_widgets = None
    schema = None
    fields_order = None

    def getFields(self):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        fields = getFields(self.schema)
        fields_order = self.fields_order
        if fields_order:
            return [fields[name] for name in fields_order]
        else:
            return fields.values()
        
    def getField(self, name):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        field = self.schema.getDescriptionFor(name)
        assert IField.isImplementedBy(field)
        return field

    def getWidgetForFieldName(self, name):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        return self.getWidgetForField(self.getField(name))

    def getWidgetForField(self, field):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        name = field.getName()
        if (self.custom_widgets is not None and
            self.custom_widgets.has_key(name)):
            return self.custom_widgets[name](field, self.request)
        return getView(field, 'widget', self.request)

    def renderField(self, field, useRequest=0):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        widget = self.getWidgetForField(field)
        value = None
        if useRequest:
            value = self.request.form.get('field_' + field.getName())
        if value is None:
            value = getattr(self.context, field.getName())
        return widget.render(value)

    def getAllRawFieldData(self):
        """Returns field data retrieved from request."""
        request = self.request
        data = {}
        for field in self.getFields():
            name = field.getName()
            raw_data = request.form.get('field_' + name)
            data[name] = raw_data
        return data

    def convertAllFieldData(self, raw_data):
        """Convert the raw data into valid objects."""
        result = {}
        errors = []
        for name, value in raw_data.iteritems():
            widget = self.getWidgetForFieldName(name)
            try:
                result[name] = widget.convert(value)
            except ConversionError, error:
                errors.append((name, error))

        if errors:
            raise ConversionErrorsAll, errors

        return result
            
    def validateAllFieldData(self, data):
        """Validate all the data."""
        validateMappingAll(self.schema, data)

    def storeAllDataInContext(self, data):
        """Store the data back into the context object."""
        context = removeAllProxies(self.context)
        for name, value in data.iteritems():
            if value != getattr(context, name):
                setattr(context, name, value)

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
        except (ValidationErrorsAll, ConversionErrorsAll), e:
            print e[0]
            return self.form(self, errors=e)
        else:
            # XXX This should do a redirect by looking up the object in
            # the view registry
            return self.form(self)
        
