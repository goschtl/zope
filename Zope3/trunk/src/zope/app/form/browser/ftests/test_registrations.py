##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Test widget registrations.

$Id: test_registrations.py,v 1.3 2004/03/17 17:59:35 srichter Exp $
"""
import unittest, doctest

from zope.interface import implements
from zope.app import zapi
from zope.publisher.browser import TestRequest

# import all widgets (in this case, importing * is ok, since we
# absolutely know what we're importing)
from zope.app.form.browser import *

import zope.schema as fields
from zope.schema import interfaces
from zope.schema import vocabulary

import zope.app.form.browser.vocabularywidget as vocabwidgets

from zope.app.form.interfaces import IDisplayWidget
from zope.app.form.interfaces import IInputWidget


class ISampleObject(interfaces.IField):
    pass
    
class SampleObject:
    implements(ISampleObject)
    
class ISampleVocabulary(
    interfaces.IVocabularyTokenized, interfaces.IVocabulary):
    pass
    
class SampleVocabularyQuery:
    implements(interfaces.IIterableVocabularyQuery)
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary    

class SampleVocabulary(vocabulary.SimpleVocabulary):
    implements(ISampleVocabulary)
    def getQuery(self):
        return SampleVocabularyQuery(self)
    
    
request = TestRequest()
sample = SampleObject()
vocab = SampleVocabulary([])
    

class Tests:
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
    
        >>> field = fields.Tuple()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, TupleSequenceWidget)
        True

    IList, IInputWidget -> ListSequenceWidget
    
        >>> field = fields.List()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, ListSequenceWidget)
        True

    IPassword, IInputWidget -> PasswordWidget
    
        >>> field = fields.Password()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, PasswordWidget)
        True

    IEnumeratedTextLine, IInputWidget -> EnumeratedTextWidget
    
        >>> field = fields.EnumeratedTextLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, EnumeratedTextWidget)
        True

    IEnumeratedInt, IInputWidget -> EnumeratedIntWidget
    
        >>> field = fields.EnumeratedInt()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, EnumeratedIntWidget)
        True

    IEnumeratedFloat, IInputWidget -> EnumeratedFloatWidget
    
        >>> field = fields.EnumeratedFloat()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, EnumeratedFloatWidget)
        True

    IEnumeratedDatetime, IInputWidget -> EnumeratedDatetimeWidget
    
        >>> field = fields.EnumeratedDatetime()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, EnumeratedDatetimeWidget)
        True

    IEnumeratedDate, IInputWidget -> EnumeratedDateWidget
    
        >>> field = fields.EnumeratedDate()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, EnumeratedDateWidget)
        True

        
    Vocabulary Widgets
    ------------------------------------------------------------------------
    The relationships between vocabulary fields and widgets are listed
    below. Note that the actual widgets returned are for IVocabulary object,
    not IVocabularyField objects.

    IVocabularyField, IDisplayWidget -> VocabularyDisplayWidget
    
        >>> field = vocabulary.VocabularyField(vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyDisplayWidget)
        True
                
    IVocabularyField, IInputWidget = VocabularyEditWidget
    
        >>> field = vocabulary.VocabularyField(vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyEditWidget)
        True

    IVocabularyBagField, IDisplayWidget -> VocabularyBagDisplayWidget
    
        >>> field = vocabulary.VocabularyBagField(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyBagDisplayWidget)
        True
        
    IVocabularyListField, IDisplayWidget -> VocabularyListDisplayWidget
    
        >>> field = vocabulary.VocabularyListField(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyListDisplayWidget)
        True
        
    IVocabularyListField, IInputWidget -> VocabularyListEditWidget
    
        >>> field = vocabulary.VocabularyListField(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyMultiEditWidget)
        True
        
    IVocabularySetField, IDisplayWidget -> VocabularyBagDisplayWidget
    
        >>> field = vocabulary.VocabularySetField(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyBagDisplayWidget)
        True
        
    IVocabularyUniqueListField, IDisplayWidget -> VocabularyListDisplayWidget
    
        >>> field = vocabulary.VocabularyUniqueListField(vocabulary=vocab)
        >>> field = field.bind(sample)
        >>> widget = zapi.getViewProviding(field, IDisplayWidget, request)
        >>> isinstance(widget, vocabwidgets.VocabularyListDisplayWidget)
        True
        
    """

def test_suite():    
    return doctest.DocTestSuite()

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
