import unittest, doctest

from zope.interface import implements
from zope.app import zapi
from zope.publisher.browser import TestRequest

import zope.schema as fields
from zope.schema import interfaces
from zope.schema import vocabulary

import zope.app.form.browser.vocabularywidget as vocabwidgets
import zope.app.form.browser.widget as widgets
from zope.app.form.browser import enumerated

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
        >>> isinstance(widget, widgets.DisplayWidget)
        True
        
    ITextLine, IInputWidget -> TextWidget 
        
        >>> field = fields.TextLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.TextWidget)
        True
        
    IText, IInputWidget -> TextAreaWidget
    
        >>> field = fields.Text()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.TextAreaWidget)
        True
        
    ISourceText, IInputWidget -> TextAreaWidget
    
        >>> field = fields.SourceText()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.TextAreaWidget)
        True

    IBytesLine, IInputWidget -> BytesWidget
    
        >>> field = fields.BytesLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.BytesWidget)
        True

    IBytes, IInputWidget -> FileWidget
    
        >>> field = fields.Bytes()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.FileWidget)
        True
        
    IASCII, IInputWidget -> BytesAreaWidget
    
        >>> field = fields.ASCII()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.BytesAreaWidget)
        True
        
    IInt, IInputWidget -> IntWidget
    
        >>> field = fields.Int()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.IntWidget)
        True
        
    IFloat, IInputWidget -> FloatWidget
    
        >>> field = fields.Float()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.FloatWidget)
        True
        
    IDatetime, IInputWidget -> DatetimeWidget
    
        >>> field = fields.Datetime()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.DatetimeWidget)
        True
        
    IDate, IInputWidget -> DateWidget
    
        >>> field = fields.Date()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.DateWidget)
        True
        
    IBool, IInputWidget -> CheckBoxWidget
    
        >>> field = fields.Bool()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.CheckBoxWidget)
        True
        
    ITuple, IInputWidget -> TupleSequenceWidget
    
        >>> field = fields.Tuple()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.TupleSequenceWidget)
        True

    IList, IInputWidget -> ListSequenceWidget
    
        >>> field = fields.List()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.ListSequenceWidget)
        True

    IPassword, IInputWidget -> PasswordWidget
    
        >>> field = fields.Password()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, widgets.PasswordWidget)
        True

    IEnumeratedTextLine, IInputWidget -> EnumeratedTextWidget
    
        >>> field = fields.EnumeratedTextLine()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, enumerated.EnumeratedTextWidget)
        True

    IEnumeratedInt, IInputWidget -> EnumeratedIntWidget
    
        >>> field = fields.EnumeratedInt()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, enumerated.EnumeratedIntWidget)
        True

    IEnumeratedFloat, IInputWidget -> EnumeratedFloatWidget
    
        >>> field = fields.EnumeratedFloat()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, enumerated.EnumeratedFloatWidget)
        True

    IEnumeratedDatetime, IInputWidget -> EnumeratedDatetimeWidget
    
        >>> field = fields.EnumeratedDatetime()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, enumerated.EnumeratedDatetimeWidget)
        True

    IEnumeratedDate, IInputWidget -> EnumeratedDateWidget
    
        >>> field = fields.EnumeratedDate()
        >>> widget = zapi.getViewProviding(field, IInputWidget, request)
        >>> isinstance(widget, enumerated.EnumeratedDateWidget)
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
