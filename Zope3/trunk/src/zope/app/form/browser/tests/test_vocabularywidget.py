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
"""Tests of the vocabulary field widget machinery.

$Id: test_vocabularywidget.py,v 1.1 2004/03/14 01:11:37 srichter Exp $
"""

import unittest

from zope.app.tests import ztapi
from zope.app.form.browser import vocabularywidget
from zope.app.form.browser.tests import support
from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.browser.interfaces import IVocabularyQueryView
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getView
from zope.interface.declarations import implements
from zope.publisher.browser import TestRequest

from zope.schema.interfaces import IVocabulary, IVocabularyQuery
from zope.schema.interfaces import IVocabularyField, IVocabularyListField
from zope.schema.interfaces import IIterableVocabularyQuery
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema import vocabulary


class ISampleVocabulary(IVocabularyTokenized, IVocabulary):
    """Specialized interface so we can hook views onto a vocabulary."""


class SampleVocabulary(vocabulary.SimpleVocabulary):
    """Vocabulary used to test vocabulary-based specialization of widgets."""
    implements(ISampleVocabulary)


class SampleDisplayWidget(vocabularywidget.VocabularyWidgetBase):
    """Widget used to test that vocabulary-based specialization works.

    This is not intended to be a useful widget.
    """
    implements(IBrowserWidget)

    def __call__(self):
        return "foo"


class SampleContent:
    """Stub content object used by makeField()."""


class QueryVocabulary(vocabulary.SimpleVocabulary):
    """Vocabulary that offer simple query support."""

    def getQuery(self):
        return MyVocabularyQuery(self)


class IMyVocabularyQuery(IVocabularyQuery):
    """Specialized query type."""


class MyVocabularyQuery:
    """Vocabulary query object which query views can be registered for."""

    implements(IMyVocabularyQuery)

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary


class MyQueryViewSingle(vocabularywidget.VocabularyQueryViewBase):
    """Single-selection vocabulary query view."""

    implements(IVocabularyQueryView)

    label = "single"

    def getResults(self):
        return self.request.form.get(self.name)

    def renderQueryInput(self):
        return "this-is-query-input"

    def renderQueryResults(self, results, value):
        return "query-results-go-here"


class MyQueryViewMulti(MyQueryViewSingle):
    """Multi-selection vocabulary query view."""

    label = "multi"


class VocabularyWidgetTestBase(PlacelessSetup,
                               support.VerifyResults,
                               unittest.TestCase):
    """Base class for all the vocabulary widget tests.

    This class provides version helper methods.
    """

    def setUp(self):
        super(VocabularyWidgetTestBase, self).setUp()
        self.registerViews()

    # makeField() uses the following class variables:
    _marker = object()
    # defaultFieldValue -- default value for the field on the content object
    # fieldClass -- class for the vocabulary field (VocabularyField or
    #               VocabularyMultiField)

    def makeField(self, vocabulary=None, value=_marker, required=False):
        """Create and return a bound vocabulary field."""
        if vocabulary is None:
            vocabulary = self.sampleVocabulary
        field = self.fieldClass(vocabulary=vocabulary, __name__="f",
                                required=required)
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


class SingleSelectionViews:
    """Mixin that registers single-selection views."""

    def registerViews(self):
        # This is equivalent to the default configuration for
        # vocabulary field view registration from configure.zcml.
        # Single-selection views only.
        ztapi.browserView(
            IVocabularyField,
            "display",
            vocabularywidget.VocabularyFieldDisplayWidget)
        ztapi.browserView(
            IVocabularyField,
            "edit",
            vocabularywidget.VocabularyFieldEditWidget)
        # Register the "basic" widgets:
        ztapi.browserView(
            IVocabularyTokenized,
            "field-display-widget",
            vocabularywidget.VocabularyDisplayWidget)
        ztapi.browserView(
            IVocabularyTokenized,
            "field-edit-widget",
            # XXX indirect through a derived class to allow
            # testing of multiple concrete widgets
            self.singleSelectionEditWidget)
        ztapi.browserView(
            IIterableVocabularyQuery,
            "widget-query-helper",
            vocabularywidget.IterableVocabularyQueryView)
        # The following widget registration supports the specific
        # sample vocabulary we're using, used to demonstrate how to
        # override widget selection based on vocabulary:
        ztapi.browserView(ISampleVocabulary,
                    "field-display-widget",
                                        SampleDisplayWidget)


class MultiSelectionViews:

    def registerViews(self):
        # This is equivalent to the default configuration for
        # vocabulary field view registration from configure.zcml.
        # Multi-selection views only.
        ztapi.browserView(
            IVocabularyListField,
            "display",
            vocabularywidget.VocabularyListFieldDisplayWidget)
        ztapi.browserView(
            IVocabularyListField,
            "edit",
            vocabularywidget.VocabularyListFieldEditWidget)
        # Bind widgets to the vocabulary fields:
        ztapi.browserView(
            IVocabularyTokenized,
            "field-display-list-widget",
            vocabularywidget.VocabularyListDisplayWidget)
        ztapi.browserView(
            IVocabularyTokenized,
            "field-edit-list-widget",
            vocabularywidget.VocabularyMultiEditWidget)
        ztapi.browserView(
            IIterableVocabularyQuery,
            "widget-query-list-helper",
            vocabularywidget.IterableVocabularyQueryMultiView)
        # The following widget registration supports the specific
        # sample vocabulary we're using, used to demonstrate how to
        # override widget selection based on vocabulary:
        ztapi.browserView(ISampleVocabulary,
                    "field-display-list-widget",
                                        SampleDisplayWidget)


class SelectionTestBase(VocabularyWidgetTestBase):
    """Base class for the general widget tests (without query support)."""

    def test_vocabulary_specialization(self):
        bound = self.makeField(SampleVocabulary.fromValues(["frobnication"]))
        w = getView(bound, "display", self.makeRequest())
        self.assertEqual(w(), "foo")


class SingleSelectionTestsBase(SingleSelectionViews, SelectionTestBase):
    """Test cases for basic single-selection widgets."""

    defaultFieldValue = "splat"
    fieldClass = vocabulary.VocabularyField

    sampleVocabulary = vocabulary.SimpleVocabulary.fromValues(
        ["splat", "foobar"])

    def test_display(self):
        bound = self.makeField()
        w = getView(bound, "display", self.makeRequest())
        w.setRenderedValue(bound.context.f)
        self.assertEqual(w(), "splat")

    def test_display_with_form_value(self):
        bound = self.makeField()
        request = self.makeRequest('field.f=foobar')
        w = getView(bound, "display", request)
        self.assert_(w.hasInput())
        self.assertEqual(w(), "foobar")

    def setup_edit(self, bound):
        w = getView(bound, "edit", self.makeRequest())
        w.setRenderedValue(bound.context.f)
        self.assert_(not w.hasInput())
        return w

    def test_edit(self, extraChecks=[]):
        w = self.setup_edit(self.makeField())
        self.assertEqual(w.getInputValue(), None)
        self.verifyResult(w(), [
            'selected="selected"',
            'id="field.f"',
            'name="field.f"',
            'value="splat"',
            '>splat<',
            'value="foobar"',
            '>foobar<',
            ] + extraChecks)
        s0, s1, s2 = w.renderItems("foobar")
        self.verifyResult(s0, [
            "value=''",
            "no value",
            ])
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

    def test_edit_required(self, extraChecks=[]):
        w = self.setup_edit(self.makeField(required=True))
        self.verifyResult(w(), [
            'selected="selected"',
            'id="field.f"',
            'name="field.f"',
            'value="splat"',
            '>splat<',
            'value="foobar"',
            '>foobar<',
            ] + extraChecks)
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
        bound = self.makeField()
        request = self.makeRequest('field.f=foobar')
        w = getView(bound, "edit", request)
        self.assert_(w.hasInput())
        self.assertEqual(w.getInputValue(), "foobar")
        self.assert_(isinstance(w, vocabularywidget.VocabularyEditWidget))

    def test_edit_with_modified_empty_value(self):
        # This tests that emptying a value via the form when there's a
        # non-empty value for the field on the content object will
        # report hasInput() properly.
        bound = self.makeField()
        bound.context.f = "splat"
        w = getView(bound, "edit", self.makeRequest(
            'field.f-empty-marker='))
        self.assert_(w.hasInput())
        self.assertEqual(w.getInputValue(), None) # XXX might be []...

class SingleSelectionTests(SingleSelectionTestsBase):
    """Test single-selection with the selection-box widget."""

    singleSelectionEditWidget = vocabularywidget.SelectListWidget


class RadioSelectionTests(SingleSelectionTests):
    
    singleSelectionEditWidget = vocabularywidget.RadioWidget

    # override three tests

    def test_edit_with_form_value(self):
        bound = self.makeField()
        request = self.makeRequest('field.f=foobar')
        w = getView(bound, "edit", request)
        self.assert_(w.hasInput())
        self.assertEqual(w.getInputValue(), "foobar")
        self.assert_(isinstance(w, vocabularywidget.RadioWidget))

    def test_edit(self, extraChecks=[]):
        w = self.setup_edit(self.makeField())
        self.assertEqual(w.getInputValue(), None)
        self.verifyResult(w(), [
            'checked="checked"',
            'id="field.f"',
            'name="field.f"',
            'value="splat"',
            '&nbsp;splat',
            'value="foobar"',
            '&nbsp;foobar',
            ] + extraChecks)
        s0, s1, s2 = w.renderItems("foobar")
        self.verifyResult(s0, [
            'value=""',
            "no value",
            ])
        self.verifyResult(s1, [
            'value="splat"',
            '&nbsp;splat',
            ])
        self.assert_(s1.find('selected') < 0)
        self.verifyResult(s2, [
            'checked="checked"',
            'value="foobar"',
            '&nbsp;foobar',
            ])

    def test_edit_required(self, extraChecks=[]):
        w = self.setup_edit(self.makeField(required=True))
        self.verifyResult(w(), [
            'checked="checked"',
            'id="field.f"',
            'name="field.f"',
            'value="splat"',
            '&nbsp;splat',
            'value="foobar"',
            '&nbsp;foobar',
            ] + extraChecks)
        s1, s2 = w.renderItems("foobar")
        self.verifyResult(s1, [
            'value="splat"',
            '&nbsp;splat',
            ])
        self.assert_(s1.find('selected') < 0)
        self.verifyResult(s2, [
            'checked="checked"',
            'value="foobar"',
            '&nbsp;foobar',
            ])

class DropdownSelectionTests(SingleSelectionTestsBase):
    """Test single-selection with the dropdown-list widget."""

    singleSelectionEditWidget = vocabularywidget.DropdownListWidget

    def test_edit(self):
        SingleSelectionTestsBase.test_edit(self, extraChecks=['size="1"'])

    def test_edit_required(self):
        SingleSelectionTestsBase.test_edit_required(
            self, extraChecks=['size="1"'])


class MultiSelectionTests(MultiSelectionViews, SelectionTestBase):
    """Test cases for basic multi-selection widgets."""

    defaultFieldValue = ["splat"]
    fieldClass = vocabulary.VocabularyListField
    sampleVocabulary = vocabulary.SimpleVocabulary.fromValues(
        ["splat", "foobar", "frob"])

    def test_display_without_value(self):
        bound = self.makeField()
        del bound.context.f
        w = getView(bound, "display", self.makeRequest())
        self.assert_(not w.hasInput())
        self.assertEqual(w(), "")

    def test_display_with_value(self):
        bound = self.makeField(value=["foobar", "frob"])
        w = getView(bound, "display", self.makeRequest())
        w.setRenderedValue(bound.context.f)
        self.assert_(not w.hasInput())
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
        bound = self.makeField(value=["foobar", "frob"])
        request = self.makeRequest('field.f:list=splat')
        w = getView(bound, "display", request)
        self.assert_(w.hasInput())
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
        bound = self.makeField()
        w = getView(bound, "edit", self.makeRequest())
        self.assert_(not w.hasInput())
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
        bound = self.makeField()
        request = self.makeRequest('field.f:list=foobar&field.f:list=splat')
        w = getView(bound, "edit", request)
        self.assert_(w.hasInput())
        L = w.getInputValue()
        L.sort()
        self.assertEqual(L, ["foobar", "splat"])


class QuerySupportTestBase(VocabularyWidgetTestBase):
    """Base class defining tests that can be used for both single- and
    multi-select query support.

    Derived classes must specialize to support specific selection
    mechanics.
    """

    sampleVocabulary = QueryVocabulary.fromValues(
        ["splat", "foobar", "frob"])

    def test_get_query_helper(self):
        bound = self.makeField()
        request = self.makeRequest()
        w = getView(bound, "edit", request)
        self.assert_(isinstance(w.query, MyVocabularyQuery))
        self.assert_(w.queryview.widget is w)
        self.assertEqual(w.queryview.name, w.name + "-query")
        self.assertEqual(w.queryview.label, self.queryViewLabel)

    def test_query_input_section(self):
        bound = self.makeField()
        w = getView(bound, "edit", self.makeRequest())
        w.setRenderedValue(bound.context.f)
        checks = [
            "this-is-query-input",
            ]
        self.verifyResult(w.queryview.renderInput(), checks)
        self.verifyResult(w(), checks + ['class="queryinput"'])

    def test_query_output_section_without_results(self):
        bound = self.makeField()
        w = getView(bound, "edit", self.makeRequest())
        w.setRenderedValue(bound.context.f)
        checks = [
            "query-results-go-here",
            ]
        self.verifyResultMissing(w.queryview.renderResults([]), checks)
        self.verifyResultMissing(w(), checks + ['class="queryresults"'])

    def test_query_output_section_with_results(self):
        bound = self.makeField()
        w = getView(bound, "edit", self.makeRequest("field.f-query=foo"))
        w.setRenderedValue(bound.context.f)
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
    singleSelectionEditWidget = vocabularywidget.VocabularyEditWidget

    def registerViews(self):
        SingleSelectionViews.registerViews(self)
        ztapi.browserView(IMyVocabularyQuery,
                          "widget-query-helper",
                          MyQueryViewSingle)


class MultiSelectionQuerySupportTests(MultiSelectionViews,
                                      QuerySupportTestBase):
    """Query support tests for multi-selection widgets."""

    defaultFieldValue = ["splat"]
    fieldClass = vocabulary.VocabularyListField
    queryViewLabel = "multi"

    def registerViews(self):
        MultiSelectionViews.registerViews(self)
        ztapi.browserView(IMyVocabularyQuery,
                          "widget-query-list-helper",
                          MyQueryViewMulti)


def test_suite():
    suite = unittest.makeSuite(SingleSelectionTests)
    suite.addTest(unittest.makeSuite(RadioSelectionTests))
    suite.addTest(unittest.makeSuite(DropdownSelectionTests))
    suite.addTest(unittest.makeSuite(MultiSelectionTests))
    suite.addTest(unittest.makeSuite(SingleSelectionQuerySupportTests))
    suite.addTest(unittest.makeSuite(MultiSelectionQuerySupportTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
