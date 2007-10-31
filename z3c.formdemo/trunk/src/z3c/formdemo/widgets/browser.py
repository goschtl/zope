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
"""Widgets Demo Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
import zope.interface
import zope.component
from zope.annotation import factory
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.publisher import browser
from zope.schema.fieldproperty import FieldProperty
from zope.pagetemplate.interfaces import IPageTemplate
from zope.session.interfaces import ISession

from z3c.form.interfaces import IWidgets
from z3c.form import button, form, field
from z3c.form.browser import checkbox
from z3c.form.interfaces import HIDDEN_MODE
from z3c.formdemo.widgets import interfaces
from z3c.template.interfaces import ILayoutTemplate

class AllFields(persistent.Persistent):

    zope.interface.implements(interfaces.IAllFields)
    zope.component.adapts(IAttributeAnnotatable)

    asciiField = FieldProperty(interfaces.IAllFields['asciiField'])
    asciiLineField = FieldProperty(interfaces.IAllFields['asciiLineField'])
    boolField = FieldProperty(interfaces.IAllFields['boolField'])
    checkboxBoolField = FieldProperty(
        interfaces.IAllFields['checkboxBoolField'])
    bytesField = FieldProperty(interfaces.IAllFields['bytesField'])
    bytesLineField = FieldProperty(interfaces.IAllFields['bytesLineField'])
    choiceField = FieldProperty(interfaces.IAllFields['choiceField'])
    optionalChoiceField = FieldProperty(
        interfaces.IAllFields['optionalChoiceField'])
    promptChoiceField = FieldProperty(
        interfaces.IAllFields['promptChoiceField'])
    dateField = FieldProperty(interfaces.IAllFields['dateField'])
    datetimeField = FieldProperty(interfaces.IAllFields['datetimeField'])
    decimalField = FieldProperty(interfaces.IAllFields['decimalField'])
    dictField = FieldProperty(interfaces.IAllFields['dictField'])
    dottedNameField = FieldProperty(interfaces.IAllFields['dottedNameField'])
    floatField = FieldProperty(interfaces.IAllFields['floatField'])
    frozenSetField = FieldProperty(interfaces.IAllFields['frozenSetField'])
    idField = FieldProperty(interfaces.IAllFields['idField'])
    intField = FieldProperty(interfaces.IAllFields['intField'])
    listField = FieldProperty(interfaces.IAllFields['listField'])
    objectField = FieldProperty(interfaces.IAllFields['objectField'])
    passwordField = FieldProperty(interfaces.IAllFields['passwordField'])
    setField = FieldProperty(interfaces.IAllFields['setField'])
    sourceTextField = FieldProperty(interfaces.IAllFields['sourceTextField'])
    textField = FieldProperty(interfaces.IAllFields['textField'])
    textLineField = FieldProperty(interfaces.IAllFields['textLineField'])
    timeField = FieldProperty(interfaces.IAllFields['timeField'])
    timedeltaField = FieldProperty(interfaces.IAllFields['timedeltaField'])
    tupleField = FieldProperty(interfaces.IAllFields['tupleField'])
    uriField = FieldProperty(interfaces.IAllFields['uriField'])
    hiddenField = FieldProperty(interfaces.IAllFields['hiddenField'])

# register the AllField class as a annotation adapter
getAllFields = factory(AllFields)


class AllFieldsForm(form.EditForm):
    """A form showing all fields."""
    form.extends(form.EditForm)
    fields = field.Fields(interfaces.IAllFields).omit(
        'dictField', 'objectField')
    fields['checkboxBoolField'].widgetFactory = \
        checkbox.SingleCheckBoxFieldWidget

    buttons = form.EditForm.buttons + \
              button.Buttons(
                 button.ImageButton(name='pressme', image=u'pressme.png')
                 )

    label = 'Widgets Demo'

    @button.handler(buttons['pressme'])
    def handlePressMe(self, action):
        self.status = u'Press me was clicked!'

    def getContent(self):
        return interfaces.IAllFields(self.context)

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.update()
        self.widgets['hiddenField'].mode = HIDDEN_MODE
        self.widgets['promptChoiceField'].prompt = True
        self.widgets['promptChoiceField'].update()

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)
