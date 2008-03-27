##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import zc.extjs.interfaces
import zope.app.form
import zope.app.form.interfaces
import zope.app.form.browser.interfaces
import zope.interface
import zope.cachedescriptors.property
import zope.component
import zope.schema.interfaces

class Base(zope.app.form.InputWidget):

    zope.interface.implements(zc.extjs.interfaces.IInputWidget)

    xtype = None
    widget_constructor = None

    def js_config(self, **kw):
        config = dict(
            fieldLabel = self.label,
            fieldHint = self.hint,
            name = self.name,
            id = self.name,
            **kw)

        if self.xtype:
            config['xtype'] = self.xtype
        elif not self.widget_constructor:
            raise ValueError(
                'Neither xtype nor widget_constructor are defined.')

        if self.widget_constructor:
            config['widget_constructor'] = self.widget_constructor
        
        if self.required:
            config['itemCls'] = 'zc-required-field'

        if self._renderedValueSet():
            value = self.formValue(self._data)
            if value is not None:
                config['value'] = value
        
        return config 

    def formValue(self, v):
        if v == self.context.missing_value:
            return None
        return unicode(v)

    def _toValue(self, v):
        return v

    def hasInput(self):
        return self.name in self.request.form

    def _is_missing(self, raw):
        return False

    def _get_raw(self):
        return self.request.form[self.name]

    def getInputValue(self):
        if not self.hasInput():
            raise zope.app.form.interfaces.MissingInputError(
                self.name, self.label, None)

        raw = self._get_raw()
        if self._is_missing(raw):
            if self.required:
                raise zope.app.form.interfaces.MissingInputError(
                    self.name, self.label, None)
            else:
                return self.context.missing_value
            
        value = self._toValue(raw)
        
        # value must be valid per the field constraints
        try:
            self.context.validate(value)
        except zope.schema.interfaces.ValidationError, v:
            raise zope.app.form.interfaces.WidgetInputError(
                self.context.__name__, self.label, v)
            
        return value
 
    @zope.cachedescriptors.property.Lazy
    def required(self):
        return self.context.required

class InputBool(Base):

    zope.component.adapts(
        zope.schema.interfaces.IBool,
        zc.extjs.interfaces.IAjaxRequest,
        )

    xtype = 'checkbox'

    def hasInput(self):
        return True
        
    def getInputValue(self):
        return self.request.form.get(self.name, '') == 'on'

    def formValue(self, v):
        if v == self.context.missing_value:
            return None
        return bool(v)


    
class InputChoiceIterable(Base):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        zope.schema.interfaces.IIterableSource,
        zc.extjs.interfaces.IAjaxRequest,
        )

    widget_constructor = 'zc.extjs.widgets.InputChoice'

    def __init__(self, context, source, request):
        Base.__init__(self, context, request)
        self.source = source

    def _is_missing(self, raw):
        return not raw

    def _get_raw(self):
        return self.request.form[self.name+'.value']

    def hasInput(self):
        return self.name+'.value' in self.request.form

    def js_config(self):
        result = Base.js_config(self)
        result['hiddenName'] = result['name']+'.value'

        terms = zope.component.getMultiAdapter(
            (self.source, self.request),
            zope.app.form.browser.interfaces.ITerms,
            )

        result['values'] = [
            [term.token, term.title]
            for term in (terms.getTerm(v) for v in self.source)
            ]
        
        if self.required:
            result['allowBlank'] = False

        return result

    def formValue(self, v):
        if v == self.context.missing_value:
            return None
        terms = zope.component.getMultiAdapter(
            (self.source, self.request),
            zope.app.form.browser.interfaces.ITerms,
            )
        return terms.getTerm(v).token

    def _toValue(self, v):
        terms = zope.component.getMultiAdapter(
            (self.source, self.request),
            zope.app.form.browser.interfaces.ITerms,
            )
        return terms.getValue(v)
    
class InputChoiceTokenized(InputChoiceIterable):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        zope.schema.interfaces.IVocabularyTokenized,
        zc.extjs.interfaces.IAjaxRequest,
        )

    def js_config(self):
        result = Base.js_config(self)
        result['hiddenName'] = result['name']+'.value'

        result['values'] = [
            [term.token, term.title or unicode(term.value)]
            for term in self.source
            ]
        
        if self.required:
            result['allowBlank'] = False

        return result

    def formValue(self, v):
        if v == self.context.missing_value:
            return None
        return self.source.getTerm(v).token

    def _toValue(self, v):
        return self.source.getTermByToken(v).value
            
class InputInt(Base):

    zope.component.adapts(
        zope.schema.interfaces.IInt,
        zc.extjs.interfaces.IAjaxRequest,
        )

    widget_constructor = 'zc.extjs.widgets.InputInt'

    def js_config(self):
        config = Base.js_config(self)

        if self.required:
            config['allowBlank'] = False
        
        if self.context.min is not None:
            config['field_min'] = self.context.min
        if self.context.max is not None:
            config['field_max'] = self.context.max
        return config

    def _is_missing(self, raw):
        return not raw

    def _toValue(self, v):
        try:
            return int(v)
        except:
            raise zope.app.form.interfaces.ConversionError(
                u"Invalid integer: %r" % v
                )

class InputTextLine(Base):

    zope.component.adapts(
        zope.schema.interfaces.ITextLine,
        zc.extjs.interfaces.IAjaxRequest,
        )

    xtype = 'textfield'

    def _is_missing(self, raw):
        return (not raw) and self.required
    
    def js_config(self):
        config = Base.js_config(self)
        if self.context.min_length is not None:
            config['minLength'] = self.context.min_length
            if self.context.min_length > 0 and self.required:
                config['allowBlank'] = False

        if self.context.max_length is not None:
            config['maxLength'] = self.context.max_length
            
        return config

class InputText(InputTextLine):

    zope.component.adapts(
        zope.schema.interfaces.IText,
        zc.extjs.interfaces.IAjaxRequest,
        )

    xtype = 'textarea'

class Hidden(Base):

    xtype = 'hidden'
