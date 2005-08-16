##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests of the vocabulary queries.

$Id$
"""
import unittest
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.publisher.browser import IBrowserRequest
from zope.schema import vocabulary, Choice, List
from zope.schema.interfaces import IVocabularyQuery, IChoice, ICollection

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.app.form.browser import DropdownWidget, MultiSelectWidget
from zope.app.form.browser.interfaces import IVocabularyQueryView
from zope.app.form.browser.vocabularyquery import VocabularyQueryViewBase
from zope.app.form.browser.tests import support


def provideMultiView(for_, factory, providing, name='', layer="default"):
    s = zapi.getGlobalService(zapi.servicenames.Presentation)
    return s.provideAdapter(IBrowserRequest, factory, name, for_,
                            providing, layer)

_marker = object()

class SampleContent:
    """Stub content object used by makeField()."""
    def __init__(self, value):
        self.f = value


class SampleQueryVocabulary(vocabulary.SimpleVocabulary):
    """Vocabulary that offer simple query support."""

    def getQuery(self):
        return SampleVocabularyQuery(self)


class ISampleVocabularyQuery(IVocabularyQuery):
    """Specialized query type."""


class SampleVocabularyQuery:
    """Vocabulary query object which query views can be registered for."""

    implements(ISampleVocabularyQuery)

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary


class SampleQueryViewSingle(VocabularyQueryViewBase):
    """Single-selection vocabulary query view."""

    implements(IVocabularyQueryView)

    label = "single"

    def _getResults(self):
        return self.request.form.get(self.name)

    def _renderQueryInput(self):
        return "this-is-query-input"

    def _renderQueryResults(self, results, value):
        return "query-results-go-here"


class SampleQueryViewMulti(SampleQueryViewSingle):
    """Multi-selection vocabulary query view."""

    label = "multi"


class QuerySupportTestBase(PlacelessSetup,
                           support.VerifyResults,
                           unittest.TestCase):
    """Base class defining tests that can be used for both single- and
    multi-select query support.

    Derived classes must specialize to support specific selection
    mechanics.
    """
    _marker = object()
    defaultFieldValue = None

    _sampleVocabulary = SampleQueryVocabulary.fromValues(
        ["splat", "foobar", "frob"])
    _widgetFactory = None

    def setUp(self):
        super(QuerySupportTestBase, self).setUp()
        self.registerViews()

    def _makeWidget(self, form={}):
        vocab = self._sampleVocabulary
        bound = self.makeField(vocabulary=vocab)
        widget = self._widgetFactory(bound, vocab, TestRequest(form=form))
        return widget

    def test_get_query_helper(self):
        widget = self._makeWidget()
        self.assert_(
            isinstance(widget.queryview.context, SampleVocabularyQuery))
        self.assert_(widget.queryview.widget is widget)
        self.assertEqual(widget.queryview.name, widget.name + "-query")
        self.assertEqual(widget.queryview.label, self.queryViewLabel)

    def test_query_input_section(self):
        widget = self._makeWidget()
        widget.setRenderedValue(self.defaultFieldValue)
        checks = [
            "this-is-query-input",
            ]
        self.verifyResult(widget.queryview.renderInput(), checks)
        self.verifyResult(widget(), checks + ['class="queryinput"'])

    def test_query_output_section_without_results(self):
        widget = self._makeWidget()
        widget.setRenderedValue(self.defaultFieldValue)
        checks = [
            "query-results-go-here",
            ]
        self.verifyResultMissing(widget.queryview.renderResults([]), checks)
        self.verifyResultMissing(widget(), checks + ['class="queryresults"'])

    def test_query_output_section_with_results(self):
        widget = self._makeWidget({'field.f-query': 'foo'})
        widget.setRenderedValue(self.defaultFieldValue)
        checks = [
            "query-results-go-here",
            ]
        self.verifyResult(widget.queryview.renderResults([]), checks)
        self.verifyResult(widget(), checks + ['class="queryresults"'])


class SingleSelectionQuerySupportTests(QuerySupportTestBase):
    """Query support tests for single-selection widgets."""

    defaultFieldValue = "splat"
    fieldClass = Choice
    queryViewLabel = "single"
    _widgetFactory = DropdownWidget

    def makeField(self, vocabulary=None, value=_marker, required=False):
        """Create and return a bound vocabulary field."""
        if vocabulary is None:
            vocabulary = self._sampleVocabulary
        field = Choice(vocabulary=vocabulary, __name__="f",
                                 required=required)
        if value is self._marker:
            value = self.defaultFieldValue
        content = SampleContent(value)
        return field.bind(content)

    def registerViews(self):
        provideMultiView((ISampleVocabularyQuery, IChoice),
                         SampleQueryViewSingle, IVocabularyQueryView)


class MultiSelectionQuerySupportTests(QuerySupportTestBase):
    """Query support tests for multi-selection widgets."""

    defaultFieldValue = ["splat"]
    fieldClass = List
    queryViewLabel = "multi"
    _widgetFactory = MultiSelectWidget

    def makeField(self, vocabulary=None, value=[], required=False):
        """Create and return a bound vocabulary field."""
        if vocabulary is None:
            vocabulary = self._sampleVocabulary
        field = List(__name__="f",
                     value_type=Choice(vocabulary=vocabulary,
                                       required=required))
        if value is self._marker:
            value = self.defaultFieldValue
        content = SampleContent(value)
        return field.bind(content)

    def registerViews(self):
        provideMultiView((ISampleVocabularyQuery, ICollection),
                         SampleQueryViewMulti, IVocabularyQueryView)


def test_suite():
    suite = unittest.makeSuite(SingleSelectionQuerySupportTests)
    suite.addTest(unittest.makeSuite(MultiSelectionQuerySupportTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
