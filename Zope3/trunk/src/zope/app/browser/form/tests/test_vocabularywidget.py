##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Tests of the vocabulary field widget machinery."""

import unittest

from zope.app.browser.form import vocabularywidget
from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.interfaces.browser.form import IVocabularyQueryView
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getView
from zope.component.view import provideView
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.schema.interfaces import IVocabulary, ITerm, IVocabularyQuery
from zope.schema.interfaces import IVocabularyField, IVocabularyMultiField
from zope.schema.interfaces import IIterableVocabularyQuery
from zope.schema.interfaces import IVocabularyTokenized, ITokenizedTerm
from zope.schema import vocabulary


class ISampleVocabulary(IVocabularyTokenized, IVocabulary):
    """Specialized interface so we can hook views onto a vocabulary."""

class SampleTerm(object):
    """Trivial ITerm implementation."""
    __implements__ = ITokenizedTerm

    def __init__(self, value):
        self.value = value
        self.token = value


class BasicVocabulary(object):
    """Simple vocabulary that uses terms from a passed-in list of values."""
    __implements__ = IVocabularyTokenized, IVocabulary

    def __init__(self, values):
        self._values = values

    def __contains__(self, value):
        return value in self._values

    def __iter__(self):
        return BasicIterator(self._values)

    def __len__(self):
        return len(self._values)

    def getQuery(self):
        return None

    def getTerm(self, value):
        if value in self._values:
            return SampleTerm(value)
        raise LookupError("%r not a vocabulary member" % value)

    def getTermByToken(self, token):
        for term in self._values:
            if term.token == token:
                return term
        raise LookupError("token %r not found in vocabulary" % token)

class BasicIterator(object):
    """Iterator that produces ITerm objects from vocabulary data."""

    def __init__(self, values):
        self._next = iter(values).next

    def __iter__(self):
        return self

    def next(self):
        return SampleTerm(self._next())

class SampleVocabulary(BasicVocabulary):
    """Vocabulary used to test vocabulary-based specialization of widgets."""
    __implements__ = ISampleVocabulary


class SampleDisplayWidget(vocabularywidget.VocabularyWidgetBase):
    """Widget used to test that vocabulary-based specialization works.

    This is not intended to be a useful widget.
    """
    __implements__ = IBrowserWidget

    def __call__(self):
        return "foo"


class SampleContent:
    """Stub content object used by makeField()."""


class QueryVocabulary(BasicVocabulary):
    """Vocabulary that offer simple query support."""

    def getQuery(self):
        return MyVocabularyQuery(self)


class IMyVocabularyQuery(IVocabularyQuery):
    """Specialized query type."""


class MyVocabularyQuery:
    """Vocabulary query object which query views can be registered for."""

    __implements__ = IMyVocabularyQuery

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary


class MyQueryViewBase(vocabularywidget.VocabularyQueryViewBase):
    """Base class for test query views."""

    def getResults(self):
        return self.request.form.get(self.name)

    def renderQueryInput(self):
        return "this-is-query-input"

    def renderQueryResults(self, results, value):
        return "query-results-go-here"


class MyQueryViewSingle(MyQueryViewBase):
    """Single-selection vocabulary query view."""

    __implements__ = IVocabularyQueryView

    def getLabel(self):
        return "single"


class MyQueryViewMulti(MyQueryViewBase):
    """Multi-selection vocabulary query view."""

    __implements__ = IVocabularyQueryView

    def getLabel(self):
        return "multi"


class VocabularyWidgetTestBase(PlacelessSetup, unittest.TestCase):
    """Base class for all the vocabulary widget tests.

    This class provides version helper methods.
    """

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.registerViews()

    # makeField() uses the following class variables:
    _marker = object()
    # defaultFieldValue -- default value for the field on the content object
    # fieldClass -- class for the vocabulary field (VocabularyField or
    #               VocabularyMultiField)

    def makeField(self, vocabulary, value=_marker):
        """Create and return a bound vocabulary field."""
        field = self.fieldClass(vocabulary=vocabulary, __name__="f")
        content = SampleContent()
        if value is self._marker:
            value = self.defaultFieldValue
        content.f = value
        return field.bind(content)

    def makeRequest(self, querystring=None):
        """Create and return a request.

        If querystring is not None, it is passed as the QUERY_STRING.
        """
        if querystring is None:
            return TestRequest()
        else:
            tr = TestRequest(QUERY_STRING=querystring)
            tr.processInputs()
            return tr

    # modified from test_browserwidget.BrowserWidgetTest:
    def verifyResult(self, result, check_list):
        """Ensure that each element of check_list is present in result."""
        for check in check_list:
            self.assert_(result.find(check) >= 0,
                         "%r not found in %r" % (check, result))

    def verifyResultMissing(self, result, check_list):
        """Ensure that each element of check_list is omitted from result."""
        for check in check_list:
            self.assert_(result.find(check) < 0,
                         "%r unexpectedly found in %r" % (check, result))


class SingleSelectionViews:
    """Mixin that registers single-selection views."""

    def registerViews(self):
        # This is equivalent to the default configuration for
        # vocabulary field view registration from configure.zcml.
        # Single-selection views only.
        provideView(IVocabularyField,
                    "display",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyFieldDisplayWidget)
        provideView(IVocabularyField,
                    "edit",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyFieldEditWidget)
        # Register the "basic" widgets:
        provideView(IVocabularyTokenized,
                    "field-display-widget",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyDisplayWidget)
        provideView(IVocabularyTokenized,
                    "field-edit-widget",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyEditWidget)
        provideView(IIterableVocabularyQuery,
                    "widget-query-helper",
                    IBrowserPresentation,
                    vocabularywidget.IterableVocabularyQueryView)
        # The following widget registration supports the specific
        # sample vocabulary we're using, used to demonstrate how to
        # override widget selection based on vocabulary:
        provideView(ISampleVocabulary,
                    "field-display-widget",
                    IBrowserPresentation,
                    SampleDisplayWidget)


class MultiSelectionViews:

    def registerViews(self):
        # This is equivalent to the default configuration for
        # vocabulary field view registration from configure.zcml.
        # Multi-selection views only.
        provideView(IVocabularyMultiField,
                    "display",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyMultiFieldDisplayWidget)
        provideView(IVocabularyMultiField,
                    "edit",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyMultiFieldEditWidget)
        # Bind widgets to the vocabulary fields:
        provideView(IVocabularyTokenized,
                    "field-display-multi-widget",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyMultiDisplayWidget)
        provideView(IVocabularyTokenized,
                    "field-edit-multi-widget",
                    IBrowserPresentation,
                    vocabularywidget.VocabularyMultiEditWidget)
        provideView(IIterableVocabularyQuery,
                    "widget-query-multi-helper",
                    IBrowserPresentation,
                    vocabularywidget.IterableVocabularyQueryMultiView)
        # The following widget registration supports the specific
        # sample vocabulary we're using, used to demonstrate how to
        # override widget selection based on vocabulary:
        provideView(ISampleVocabulary,
                    "field-display-multi-widget",
                    IBrowserPresentation,
                    SampleDisplayWidget)


class SelectionTestBase(VocabularyWidgetTestBase):
    """Base class for the general widget tests (without query support)."""

    def test_vocabulary_specialization(self):
        bound = self.makeField(SampleVocabulary(["frobnication"]))
        w = getView(bound, "display", self.makeRequest())
        self.assertEqual(w(), "foo")


class SingleSelectionTests(SingleSelectionViews, SelectionTestBase):
    """Test cases for basic single-selection widgets."""

    defaultFieldValue = "splat"
    fieldClass = vocabulary.VocabularyField

    def test_display(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar"]))
        w = getView(bound, "display", self.makeRequest())
        self.assertEqual(w(), "splat")

    def test_display_with_form_value(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar"]))
        request = self.makeRequest('field.f=foobar')
        w = getView(bound, "display", request)
        self.assert_(w.haveData())
        self.assertEqual(w(), "foobar")

    def test_edit(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar"]))
        w = getView(bound, "edit", self.makeRequest())
        self.assert_(not w.haveData())
        self.verifyResult(w(), [
            'selected="selected"',
            'id="field.f"',
            'name="field.f"',
            'value="splat"',
            '>splat<',
            'value="foobar"',
            '>foobar<',
            ])
        s1, s2 = w.renderItems("foobar")
        self.verifyResult(s1, [
            'value="splat"',
            '>splat<',
            ])
        self.assert_(s1.find('selected') < 0)
        self.verifyResult(s2, [
            'selected="selected"',
            'value="foobar"',
            '>foobar<',
            ])

    def test_edit_with_form_value(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar"]))
        request = self.makeRequest('field.f=foobar')
        w = getView(bound, "edit", request)
        self.assert_(w.haveData())
        self.assertEqual(w._showData(), "foobar")
        self.assert_(isinstance(w, vocabularywidget.VocabularyEditWidget))
        self.verifyResult(w.hidden(), [
            '<input',
            'id="field.f"',
            'name="field.f"',
            'value="foobar"',
            ])


class MultiSelectionTests(MultiSelectionViews, SelectionTestBase):
    """Test cases for basic multi-selection widgets."""

    defaultFieldValue = ["splat"]
    fieldClass = vocabulary.VocabularyMultiField

    def test_display_without_value(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar", "frob"]),
                               None)
        w = getView(bound, "display", self.makeRequest())
        self.assert_(not w.haveData())
        self.verifyResult(w(), [
            '<span',
            'id="field.f"',
            'name="field.f"',
            '</span>',
            ])

    def test_display_with_value(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar", "frob"]),
                               ["foobar", "frob"])
        w = getView(bound, "display", self.makeRequest())
        self.assert_(not w.haveData())
        self.verifyResult(w(), [
            '<ol',
            'id="field.f"',
            'name="field.f"',
            '</ol>',
            ])
        w.cssClass = 'test'
        items = w.renderItems(['foobar'])
        self.assertEqual(len(items), 1)
        self.verifyResult(items[0], [
            '<li',
            'class="test-item"',
            '>foobar<',
            '</li>',
            ])

    def test_display_with_form_data(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar", "frob"]),
                               ["foobar", "frob"])
        request = self.makeRequest('field.f:list=splat')
        w = getView(bound, "display", request)
        self.assert_(w.haveData())
        s = w()
        self.verifyResult(s, [
            '<ol',
            'id="field.f"',
            'name="field.f"',
            '<li',
            '>splat<',
            '</li>',
            '</ol>',
            ])
        self.assert_(s.find("foobar") < 0)
        self.assert_(s.find("frob") < 0)

    def test_edit(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar", "frob"]))
        w = getView(bound, "edit", self.makeRequest())
        self.assert_(not w.haveData())
        self.verifyResult(w(), [
            'id="field.f"',
            'name="field.f:list"',
            'value="splat"',
            '>splat<',
            'value="foobar"',
            '>foobar<',
            'value="frob"',
            '>frob<',
            ])
        s1, s2, s3 = w.renderItems(w._missing)
        self.verifyResult(s1, [
            'value="splat"',
            '>splat<',
            ])
        self.assert_(s1.find('selected') < 0)
        self.verifyResult(s2, [
            'value="foobar"',
            '>foobar<',
            ])
        self.assert_(s2.find('selected') < 0)
        self.verifyResult(s3, [
            'value="frob"',
            '>frob<',
            ])
        self.assert_(s3.find('selected') < 0)

    def test_edit_with_form_value(self):
        bound = self.makeField(BasicVocabulary(["splat", "foobar", "frob"]))
        request = self.makeRequest('field.f:list=foobar&field.f:list=splat')
        w = getView(bound, "edit", request)
        self.assert_(w.haveData())
        L = w._showData()
        L.sort()
        self.assertEqual(L, ["foobar", "splat"])
        s = w.hidden()
        self.verifyResult(s, [
            '<input',
            'type="hidden"',
            'name="field.f:list"',
            'value="foobar"',
            'value="splat"',
            ])
        self.assert_(s.find("frob") < 0)


class QuerySupportTestBase(VocabularyWidgetTestBase):
    """Base class defining tests that can be used for both single- and
    multi-select query support.

    Derived classes must specialize to support specific selection
    mechanics.
    """

    queryableVocabulary = QueryVocabulary(["splat", "foobar", "frob"])

    def test_get_query_helper(self):
        bound = self.makeField(self.queryableVocabulary)
        request = self.makeRequest()
        w = getView(bound, "edit", request)
        self.assert_(isinstance(w.query, MyVocabularyQuery))
        self.assertEqual(w.queryview.name, w.name + "-query")
        self.assertEqual(w.queryview.getLabel(), self.queryViewLabel)

    def test_query_input_section(self):
        bound = self.makeField(self.queryableVocabulary)
        w = getView(bound, "edit", self.makeRequest())
        checks = [
            "this-is-query-input",
            ]
        self.verifyResult(w.queryview.renderInput(), checks)
        self.verifyResult(w(), checks + ['class="queryinput"'])

    def test_query_output_section_without_results(self):
        bound = self.makeField(self.queryableVocabulary)
        w = getView(bound, "edit", self.makeRequest())
        checks = [
            "query-results-go-here",
            ]
        self.verifyResultMissing(w.queryview.renderResults([]), checks)
        self.verifyResultMissing(w(), checks + ['class="queryresults"'])

    def test_query_output_section_with_results(self):
        bound = self.makeField(self.queryableVocabulary)
        w = getView(bound, "edit", self.makeRequest("field.f-query=foo"))
        checks = [
            "query-results-go-here",
            ]
        self.verifyResult(w.queryview.renderResults([]), checks)
        self.verifyResult(w(), checks + ['class="queryresults"'])


class SingleSelectionQuerySupportTests(SingleSelectionViews,
                                       QuerySupportTestBase):
    """Query support tests for single-selection widgets."""

    defaultFieldValue = "splat"
    fieldClass = vocabulary.VocabularyField
    queryViewLabel = "single"

    def registerViews(self):
        SingleSelectionViews.registerViews(self)
        provideView(IMyVocabularyQuery,
                    "widget-query-helper",
                    IBrowserPresentation,
                    MyQueryViewSingle)


class MultiSelectionQuerySupportTests(MultiSelectionViews,
                                      QuerySupportTestBase):
    """Query support tests for multi-selection widgets."""

    defaultFieldValue = ["splat"]
    fieldClass = vocabulary.VocabularyMultiField
    queryViewLabel = "multi"

    def registerViews(self):
        MultiSelectionViews.registerViews(self)
        provideView(IMyVocabularyQuery,
                    "widget-query-multi-helper",
                    IBrowserPresentation,
                    MyQueryViewMulti)


def test_suite():
    suite = unittest.makeSuite(SingleSelectionTests)
    suite.addTest(unittest.makeSuite(MultiSelectionTests))
    suite.addTest(unittest.makeSuite(SingleSelectionQuerySupportTests))
    suite.addTest(unittest.makeSuite(MultiSelectionQuerySupportTests))
    return suite

if __name__ == '__main__':
    unittest.main()
