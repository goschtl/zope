##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Test widget registrations.

$Id$
"""
import unittest

from zope.configuration import xmlconfig
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.tests import setup
# import all widgets (in this case, importing * is ok, since we
# absolutely know what we're importing)
from zope.app.form.browser import *

from zope.app.form.interfaces import IDisplayWidget, IInputWidget
import zope.app.form.browser

import zope.schema as fields
from zope.schema import interfaces
from zope.schema import vocabulary

class ISampleObject(interfaces.IField):
    pass

class SampleObject(object):
    implements(ISampleObject)

class ISampleVocabulary(interfaces.IVocabularyTokenized,
                        interfaces.IVocabulary):
    pass

class SampleVocabulary(vocabulary.SimpleVocabulary):
    implements(ISampleVocabulary)

request = TestRequest()
sample = SampleObject()
vocab = SampleVocabulary([])

def setUp(test):
    setup.placelessSetUp()
    context = xmlconfig.file("tests/registerWidgets.zcml",
                             zope.app.form.browser)

class Tests(object):
    """Documents and tests widgets registration for specific field types.
    
    Standard Widgets
    ------------------------------------------------------------------------
    The relationships between field types and standard widgets are listed
    below.
    
    IField, IDisplayWidget -> DisplayWidget
        
        >>> field = fields.Field()
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, DisplayWidget)
        True
        
    ITextLine, IInputWidget -> TextWidget 
        
        >>> field = fields.TextLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, TextWidget)
        True
        
    IText, IInputWidget -> TextAreaWidget
    
        >>> field = fields.Text()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, TextAreaWidget)
        True
        
    ISourceText, IInputWidget -> TextAreaWidget
    
        >>> field = fields.SourceText()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, TextAreaWidget)
        True

    IBytesLine, IInputWidget -> BytesWidget
    
        >>> field = fields.BytesLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, BytesWidget)
        True

    IBytes, IInputWidget -> FileWidget
    
        >>> field = fields.Bytes()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, FileWidget)
        True
        
    IASCII, IInputWidget -> BytesAreaWidget
    
        >>> field = fields.ASCII()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, BytesAreaWidget)
        True
        
    IInt, IInputWidget -> IntWidget
    
        >>> field = fields.Int()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, IntWidget)
        True
        
    IFloat, IInputWidget -> FloatWidget
    
        >>> field = fields.Float()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, FloatWidget)
        True
        
    IDatetime, IInputWidget -> DatetimeWidget
    
        >>> field = fields.Datetime()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, DatetimeWidget)
        True
        
    IDate, IInputWidget -> DateWidget
    
        >>> field = fields.Date()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, DateWidget)
        True
        
    IBool, IInputWidget -> CheckBoxWidget
    
        >>> field = fields.Bool()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, CheckBoxWidget)
        True
        
    ITuple, IInputWidget -> TupleSequenceWidget
    
        >>> field = fields.Tuple(value_type=fields.Int())
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, TupleSequenceWidget)
        True

    IList, IInputWidget -> ListSequenceWidget
    
        >>> field = fields.List(value_type=fields.Int())
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, ListSequenceWidget)
        True

    IPassword, IInputWidget -> PasswordWidget
    
        >>> field = fields.Password()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, PasswordWidget)
        True

    IChoice, IDisplayWidget -> ItemDisplayWidget
    
        >>> field = fields.Choice(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, ItemDisplayWidget)
        True
                
    IChoice, IInputWidget -> DropdownWidget
    
        >>> field = fields.Choice(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, DropdownWidget)
        True

    IList with IChoice value_type, IDisplayWidget -> ItemsMultiDisplayWidget
    
        >>> field = fields.List(value_type=fields.Choice(vocabulary=vocab))
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, ItemsMultiDisplayWidget)
        True
                
    IList with IChoice value_type, IInputWidget -> MultiSelectWidget
    
        >>> field = fields.List(value_type=fields.Choice(vocabulary=vocab))
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, MultiSelectWidget)
        True
    """

def test_suite():    
    return DocTestSuite(setUp=setUp, tearDown=setup.placelessTearDown)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
