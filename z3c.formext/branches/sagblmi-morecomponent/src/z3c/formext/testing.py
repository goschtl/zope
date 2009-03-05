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
"""Test Setup.

$Id$
"""
import zope.component
import zope.interface
import zope.schema.interfaces
from zope.traversing.testing import setUp as setupTraversing
from zope.traversing.interfaces import IContainmentRoot

import z3c.form.testing
from z3c.form.interfaces import IButtonAction
from z3c.form.interfaces import ITextWidget
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import ISelectWidget
from z3c.form.interfaces import ISingleCheckBoxWidget
from z3c.form.interfaces import IRadioWidget
from z3c.form.form import BaseForm

from z3c.form.testing import setupFormDefaults
from z3c.formext import component, form, converter, interfaces

TestRequest = z3c.form.testing.TestRequest


def setupExtJSComponents():
    zope.component.provideAdapter(component.SimpleFiedWidgetFactory)
    #TextWidget
    #     TextField
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IBytesLine),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IASCIILine),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.ITextLine),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IId),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IDatetime),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextField,
            (None, None, None, ITextWidget, zope.schema.interfaces.ITimedelta),
            interfaces.IExtJSComponent)
    #     DateField
    zope.component.provideAdapter(component.DateField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IDate),
            interfaces.IExtJSComponent)
    #     TimeField
    zope.component.provideAdapter(component.TimeField,
            (None, None, None, ITextWidget, zope.schema.interfaces.ITime),
            interfaces.IExtJSComponent)
    #     NumberField
    zope.component.provideAdapter(component.NumberField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IInt),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.NumberField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IFloat),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.NumberField,
            (None, None, None, ITextWidget, zope.schema.interfaces.IDecimal),
            interfaces.IExtJSComponent)
    #    PasswordField
    zope.component.provideAdapter(component.Password,
            (None, None, None, ITextWidget,
                zope.schema.interfaces.IPassword),
            interfaces.IExtJSComponent)
    #TextAreaWidget
    zope.component.provideAdapter(component.TextArea,
            (None, None, None, ITextAreaWidget, zope.schema.interfaces.IText),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.TextArea,
            (None, None, None, ITextAreaWidget, zope.schema.interfaces.IASCII),
            interfaces.IExtJSComponent)
    #RadioWidget
    zope.component.provideAdapter(component.RadioGroup,
            (None, None, None, IRadioWidget, zope.schema.interfaces.IBool),
            interfaces.IExtJSComponent)
    #other widgets
    zope.component.provideAdapter(component.DateWidget,
            (None, None, None,
                interfaces.IExtJSDateWidget, zope.schema.interfaces.IDate),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.ComboBox,
            (None, None, None, ISelectWidget, zope.schema.interfaces.IChoice),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.CheckBox,
            (None, None, None,
                ISingleCheckBoxWidget, zope.schema.interfaces.IField),
            interfaces.IExtJSComponent)
    zope.component.provideAdapter(component.Panel)
    zope.component.provideAdapter(component.GroupPanel)
    zope.component.provideAdapter(component.FormPanel)
    zope.component.provideAdapter(component.ExtFormPanel)
    zope.component.provideAdapter(component.Button)
    zope.component.provideAdapter(component.ClientButton)
    zope.component.provideAdapter(form.ClientButtonAction,
                                  provides=IButtonAction)


def setupFormExt():
    setupExtJSComponents()
    setupFormDefaults()
    setupTraversing()
    zope.interface.classImplements(BaseForm, interfaces.IBaseForm)
    zope.component.provideAdapter(converter.ExtJSDateDataConverter)
    zope.component.provideAdapter(converter.ExtJSSingleCheckBoxDataConverter)
    zope.component.provideAdapter(converter.SingleCheckBoxDataConverter)


class Context(object):
    zope.interface.implements(IContainmentRoot)
    __name__ = ''


class TestingForm(object):

    __name__ = 'index.html'

    def getContent(self):
        if self.context is None:
            self.context = Context()
        return self.context
