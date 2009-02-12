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
"""Common z3c.form test setups

$Id$
"""
__docformat__ = 'restructuredtext'
import binascii
import doctest
import os
import re
import xml.parsers.expat

import zope.component
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty
import zope.configuration.xmlconfig

from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import TestRequest
from zope.security.interfaces import IInteraction
from zope.security.interfaces import ISecurityPolicy
from zope.security import checker
from zope.app.testing import setup
from zope.testing.doctest import register_optionflag

from z3c.form import browser, button, converter, datamanager, error, field
from z3c.form import form, interfaces, term, validator, widget
from z3c.form.browser import radio, select, text, textarea
from z3c.form.browser import file as fileWidget

from z3c.ptcompat.testing import render
from z3c.ptcompat.testing import OutputChecker

import z3c.ptcompat

import lxml.html
import lxml.doctestcompare

# register lxml doctest option flags
lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')

class TestingFileUploadDataConverter(converter.FileUploadDataConverter):
    """A special file upload data converter that works with testing."""
    zope.component.adapts(
        zope.schema.interfaces.IBytes, interfaces.IFileWidget)

    def toFieldValue(self, value):
        if value is None or value == '':
            value = self.widget.request.get(self.widget.name+'.testing', '')
            encoding = self.widget.request.get(self.widget.name+'.encoding', 'plain')

            # allow for the case where the file contents are base64 encoded.
            if encoding!='plain':
                value = value.decode(encoding)
            self.widget.request.form[self.widget.name] = value

        return super(TestingFileUploadDataConverter, self).toFieldValue(value)

class TestRequest(TestRequest):
    zope.interface.implements(interfaces.IFormLayer)

class SimpleSecurityPolicy(object):
    """Allow all access."""
    zope.interface.implements(IInteraction)
    zope.interface.classProvides(ISecurityPolicy)

    loggedIn = False
    allowedPermissions = ()

    def __init__(self, loggedIn=False, allowedPermissions=()):
        self.loggedIn = loggedIn
        self.allowedPermissions = allowedPermissions

    def __call__(self, *participations):
        self.participations = []
        return self

    def add(self, participation):
        pass

    def remove(self, participation):
        pass

    def checkPermission(self, permission, object):
        if permission is checker.CheckerPublic:
            return True
        if self.loggedIn:
            if permission in self.allowedPermissions:
                return True
        return False

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


#############################
# classes required by ObjectWidget tests
#

class IMySubObject(zope.interface.Interface):
    foofield = zope.schema.Int(
        title=u"My foo field",
        default=1111,
        max=9999,
        required=True)
    barfield = zope.schema.Int(
        title=u"My dear bar",
        default=2222,
        required=False)

class MySubObject(object):
    zope.interface.implements(IMySubObject)

    foofield = FieldProperty(IMySubObject['foofield'])
    barfield = FieldProperty(IMySubObject['barfield'])

class IMySecond(zope.interface.Interface):
    subfield = zope.schema.Object(
        title=u"Second-subobject",
        schema=IMySubObject)
    moofield = zope.schema.TextLine(title=u"Something")

class MySecond(object):
    zope.interface.implements(IMySecond)

    subfield = FieldProperty(IMySecond['subfield'])
    moofield = FieldProperty(IMySecond['moofield'])


class IMyObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySubObject)
    name = zope.schema.TextLine(title=u'name')

class MyObject(object):
    zope.interface.implements(IMyObject)
    def __init__(self, name=u'', subobject=None):
        self.subobject=subobject
        self.name=name


class IMyComplexObject(zope.interface.Interface):
    subobject = zope.schema.Object(title=u'my object', schema=IMySecond)
    name = zope.schema.TextLine(title=u'name')

class MyComplexObject(object):
    zope.interface.implements(IMyComplexObject)
    def __init__(self, name=u'', subobject=None):
        self.subobject=subobject
        self.name=name

class IMySubObjectMulti(zope.interface.Interface):
    foofield = zope.schema.Int(
        title=u"My foo field",
        default=None, #default is None here!
        max=9999,
        required=True)
    barfield = zope.schema.Int(
        title=u"My dear bar",
        default=2222,
        required=False)

class MySubObjectMulti(object):
    zope.interface.implements(IMySubObjectMulti)

    foofield = FieldProperty(IMySubObjectMulti['foofield'])
    barfield = FieldProperty(IMySubObjectMulti['barfield'])

#
#
#############################

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

def setUpZPT(suite):
    z3c.ptcompat.config.disable()
    setUp(suite)

def setUpZ3CPT(suite):
    z3c.ptcompat.config.enable()
    setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()

def setupFormDefaults():
    # Validator adapters
    zope.component.provideAdapter(validator.SimpleFieldValidator)
    zope.component.provideAdapter(validator.InvariantsValidator)
    # Data manager adapter to get and set values to content
    zope.component.provideAdapter(datamanager.AttributeField)
    # Adapter to use form.fields to generate widgets
    zope.component.provideAdapter(field.FieldWidgets)
    # Adapters to lookup the widget for a field
    # Text Field Widget
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IBytesLine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IASCIILine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITextLine, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IId, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IInt, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IFloat, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDecimal, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDate, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IDatetime, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITime, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITimedelta, interfaces.IFormLayer))
    zope.component.provideAdapter(
        text.TextFieldWidget,
        adapts=(zope.schema.interfaces.IURI, interfaces.IFormLayer))
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('text_hidden.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextWidget),
        IPageTemplate, name=interfaces.HIDDEN_MODE)

    # Textarea Field Widget
    zope.component.provideAdapter(
        textarea.TextAreaFieldWidget,
        adapts=(zope.schema.interfaces.IASCII, interfaces.IFormLayer))
    zope.component.provideAdapter(
        textarea.TextAreaFieldWidget,
        adapts=(zope.schema.interfaces.IText, interfaces.IFormLayer))
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('textarea_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextAreaWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('textarea_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ITextAreaWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)

    # Radio Field Widget
    zope.component.provideAdapter(radio.RadioFieldWidget)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('radio_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.IRadioWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)

    # Select Widget
    zope.component.provideAdapter(select.ChoiceWidgetDispatcher)
    zope.component.provideAdapter(select.SelectFieldWidget)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('select_hidden.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISelectWidget),
        IPageTemplate, name=interfaces.HIDDEN_MODE)

    # Checkbox Field Widget; register only templates
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('checkbox_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ICheckBoxWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(
        getPath('checkbox_display.pt'), 'text/html'),
        (None, None, None, None, interfaces.ICheckBoxWidget),
        IPageTemplate, name=interfaces.DISPLAY_MODE)
    # Submit Field Widget
    zope.component.provideAdapter(
        widget.WidgetTemplateFactory(getPath('submit_input.pt'), 'text/html'),
        (None, None, None, None, interfaces.ISubmitWidget),
        IPageTemplate, name=interfaces.INPUT_MODE)
    # selectwidget helper adapters
    zope.component.provideAdapter(select.CollectionSelectFieldWidget)
    zope.component.provideAdapter(select.CollectionChoiceSelectFieldWidget)
    # Adapter to  convert between field/internal and widget values
    zope.component.provideAdapter(converter.FieldDataConverter)
    zope.component.provideAdapter(converter.SequenceDataConverter)
    zope.component.provideAdapter(converter.CollectionSequenceDataConverter)
    zope.component.provideAdapter(converter.FieldWidgetDataConverter)
    # special data converter
    zope.component.provideAdapter(converter.IntegerDataConverter)
    zope.component.provideAdapter(converter.FloatDataConverter)
    zope.component.provideAdapter(converter.DecimalDataConverter)
    zope.component.provideAdapter(converter.DateDataConverter)
    zope.component.provideAdapter(converter.TimeDataConverter)
    zope.component.provideAdapter(converter.DatetimeDataConverter)
    zope.component.provideAdapter(converter.TimedeltaDataConverter)
    # Adapter for providing terms to radio list and other widgets
    zope.component.provideAdapter(term.BoolTerms)
    zope.component.provideAdapter(term.ChoiceTerms)
    zope.component.provideAdapter(term.ChoiceTermsVocabulary)
    zope.component.provideAdapter(term.ChoiceTermsSource)
    zope.component.provideAdapter(term.CollectionTerms)
    zope.component.provideAdapter(term.CollectionTermsVocabulary)
    zope.component.provideAdapter(term.CollectionTermsSource)
    # Adapter to create an action from a button
    zope.component.provideAdapter(
        button.ButtonAction, provides=interfaces.IButtonAction)
    # Adapter to use form.buttons to generate actions
    zope.component.provideAdapter(button.ButtonActions)
    # Adapter to use form.handlers to generate handle actions
    zope.component.provideAdapter(button.ButtonActionHandler)
    # Subscriber handling action execution error events
    zope.component.provideHandler(form.handleActionError)
    # Error View(s)
    zope.component.provideAdapter(error.ErrorViewSnippet)
    zope.component.provideAdapter(error.InvalidErrorViewSnippet)
    zope.component.provideAdapter(error.StandardErrorViewTemplate)

def tearDown(test):
    setup.placefulTearDown()
