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
$Id: FormView.py,v 1.9 2002/07/24 10:53:48 srichter Exp $
"""
from Interface.Implements import flattenInterfaces
from Schema.IField import IField
from Schema.Exceptions import StopValidation, ValidationError, \
     ConversionError, ValidationErrorsAll, ConversionErrorsAll

from Zope.Proxy.ContextWrapper import ContextWrapper
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
    fields_order = None

    def getFields(self):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        context = removeAllProxies(self.context)
        interfaces = context.__implements__
        if isinstance(interfaces, (tuple, list)):
            interfaces = flattenInterfaces(interfaces)
        else:
            interfaces = (interfaces,)
        request = self.request
        fields = {}
        for interface in interfaces:
            for name in interface.names(1):
                attr = interface.getDescriptionFor(name)
                if IField.isImplementedBy(attr):
                    # Give the field a context before adding, so they
                    # know how to retrieve data.
                    fields[name] = ContextWrapper(attr, self.context,
                                                  name=name)

        if self.fields_order is None:
            return fields.values()

        result = []
        for id in self.fields_order:
            result.append(fields[id])
        return result


    def getField(self, id):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        # XXX This needs to be optimized!
        field = None
        for f in self.getFields():
            if f.id == id:
                field = f
                break
        if field is None:
            raise KeyError, 'Field id "%s" does not exist.' %id
        return field


    def getWidgetForFieldId(self, id):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        field = self.getField(id)
        return self.getWidgetForField(field)


    def getWidgetForField(self, field):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        if self.custom_widgets is not None and \
           field.id in self.custom_widgets.keys():
            return self.custom_widgets[field.id](field, self.request)
        return getView(field, 'widget', self.request)


    def renderField(self, field, useRequest=0):
        'See Zope.App.Forms.Views.Browser.IForm.IReadForm'
        widget = self.getWidgetForField(field)
        value = None
        if useRequest:
            value = self.request.form.get('field_' + field.id)
        if value is None:
            value = getattr(self.context, field.id)
        return widget.render(value)


    def getAllRawFieldData(self):
        """Returns field data retrieved from request."""
        request = self.request
        data = {}
        for field in self.getFields():
            raw_data = request.form.get('field_' + field.id)
            data[field] = raw_data
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
                errors.append((field, error))

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
                errors.append((field, error))

        if errors:
            raise ValidationErrorsAll, errors


    def storeAllDataInContext(self, mapping):
        """Store the data back into the context object."""
        context = removeAllProxies(self.context)
        for field in mapping:
            value = mapping[field]
            if value != getattr(context, field.id):
                setattr(context, field.id, value)


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
        
