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
"""Tests for the sample complex widgets.

$Id: test_widget.py,v 1.2 2004/04/24 23:19:37 srichter Exp $
"""
import unittest
# 
# from zope.app.tests import ztapi
# from zope.app.form.browser.tests import support
# from zope.app.form.browser import vocabularywidget
# from zope.app.form.interfaces import WidgetInputError
# from zope.app.tests.placelesssetup import PlacelessSetup
# from zope.component import getView
# from zope.interface.declarations import \
#      directlyProvides, providedBy, implements
# from zope.publisher.browser import TestRequest
# from zope.schema.interfaces import IVocabularyField
# from zope.schema.interfaces import IVocabularyUniqueListField
# from zope.schema import vocabulary
# 
# from zope.app.form.browser.complexsample import complexsample
# from zope.app.form.browser.complexsample.interfaces import \
#      ISampleVocabulary, ISampleVocabularyQuery, IFancySampleVocabularyQuery
# 
# from zope.configuration import xmlconfig
# 
# class MyTerm:
#     def __init__(self, value):
#         self.value = value
#         self.token = value
#         self.title = value.replace('/', ' ').strip()
#         self.getIcon = "my/icon/path"
# 
# class MyQuery:
#     implements(IFancySampleVocabularyQuery)
# 
#     def __init__(self, vocabulary):
#         self.vocabulary = vocabulary
# 
#     def getReferenceTypes(self):
#         return [MyTerm('abc'), MyTerm('def'), MyTerm('ghi')]
# 
#     def query(self, text, type=None):
#         indexes = map(int, text.split())
#         indexes.sort()
#         L = []
#         terms = list(self.vocabulary)
#         for x in indexes:
#             try:
#                 L.append(terms[x])
#             except IndexError:
#                 pass
#         return MySubsetVocabulary(L, self.vocabulary)
# 
# class MyVocabulary(vocabulary.SimpleVocabulary):
#     implements(ISampleVocabulary)
# 
#     def createTerm(cls, data):
#         return MyTerm(data)
#     createTerm = classmethod(createTerm)
# 
#     def getQuery(self):
#         return MyQuery(self)
# 
# class ProxyVocabulary:
#     def __init__(self, vocab):
#         self._vocab = vocab
#         directlyProvides(self, providedBy(vocab))
# 
#     def __contains__(self, value):
#         return value in self._vocab
# 
#     def __iter__(self):
#         return iter(self._vocab)
# 
#     def getQuery(self):
#         return self._vocab.getQuery()
# 
#     def getTerm(self, value):
#         return self._vocab.getTerm(value)
# 
#     def getTermByToken(self, token):
#         return self._vocab.getTermByToken(token)
# 
#     def getReferenceTypes(self):
#         return self._vocab.getReferenceTypes()
# 
#     def query(self, text, type=None):
#         return self._vocab.query(text, type)
# 
# 
# class QueryComplainer(MyQuery):
#     def query(self, text, type=None):
#         self.text = text
#         self.type = type
#         raise self
# 
# 
# class MySubsetVocabulary(MyVocabulary):
#     def __init__(self, values, master):
#         self._master = master
#         MyVocabulary.__init__(self, values)
# 
#     def getMasterVocabulary(self):
#         return self._master
# 
# 
# default_vocabulary = MyVocabulary.fromValues(["/a/path", "/b/path", "/c/path",
#                                               "/d/path", "/e/path", "/f/path",
#                                               "/g/path", "/h/path", "/i/path",
#                                               ])
# 
# 
# class TestBase(PlacelessSetup, support.VerifyResults, unittest.TestCase):
#     """Base class for all test classes."""
# 
#     def setUp(self):
#         super(TestBase, self).setUp()
#         # display
#         ztapi.browserView(
#             IVocabularyUniqueListField,
#             "display",
#             vocabularywidget.VocabularyUniqueListFieldDisplayWidget)
#         ztapi.browserView(
#             ISampleVocabulary,
#             "field-display-unique-list-widget",
#             complexsample.SampleListDisplay)
#         # edit
#         ztapi.browserView(
#             IVocabularyUniqueListField,
#             "edit",
#             vocabularywidget.VocabularyUniqueListFieldEditWidget)
#         ztapi.browserView(
#             ISampleVocabulary,
#             "field-edit-unique-list-widget",
#             complexsample.SampleUniqueListEdit)
#         # query support (edit only)
#         ztapi.browserView(
#             IFancySampleVocabularyQuery,
#             "widget-query-unique-list-helper",
#             complexsample.FancySampleUniqueListQueryView)
#         ztapi.browserView(
#             ISampleVocabularyQuery,
#             "widget-query-unique-list-helper",
#             complexsample.SampleUniqueListQueryView)
# 
#     def createWidget(self, **kw):
#         request = TestRequest(**kw)
#         request.processInputs()
#         return getView(self.bound, self.viewName, request)
# 
# 
# class SampleListTestBase(TestBase):
# 
#     unbound = vocabulary.VocabularyUniqueListField(
#         __name__="paths",
#         vocabulary=default_vocabulary,
#         required=False)
# 
#     def setUp(self):
#         TestBase.setUp(self)
#         self.bound = self.unbound.bind(object())
# 
#     def test_without_form_data(self):
#         w = self.createWidget()
#         self.assertEqual(w.getInputValue(), [])
#         self.failIf(w.hasInput())
#         self.verifyResult(w(), [
#             "no values",
#             ])
# 
#     def check_with_form_data(self, qs, value, extra_checks):
#         checks = [
#             "<" + self.topElementName,
#             'class="valueList"',
#             'id="field.paths"',
#             'value="/a/path"',
#             "a path",
#             "</%s>" % self.topElementName,
#             ]
#         w = self.createWidget(QUERY_STRING=qs)
#         self.assertEqual(w.getInputValue(), value)
#         self.assert_(w.hasInput())
#         self.verifyResult(w(), checks + extra_checks)
# 
#     def test_with_form_data_1(self):
#         self.check_with_form_data(
#             "field.paths-marker=x&field.paths=/a/path",
#             ["/a/path"],
#             [])
# 
#     def test_with_form_data_2(self):
#         self.check_with_form_data(
#             "field.paths-marker=x&field.paths=/a/path&field.paths=/c/path",
#             ["/a/path", "/c/path"],
#             ['value="/c/path"', "c path",]
#             )
# 
#     def test_with_bad_form_data(self):
#         w = self.createWidget(
#             QUERY_STRING="field.paths-marker=x&field.paths=/bad/path")
#         self.assertEqual(w.getInputValue(), ["/bad/path"])
#         self.assert_(w.hasInput())
#         self.verifyResult(w(), [
#             "<" + self.topElementName,
#             'class="valueList"',
#             'id="field.paths"',
#             'value="/bad/path"',
#             complexsample._msg_inaccessible_object.default,
#             "out-of-date value",
#             "</%s>" % self.topElementName,
#             ])
# 
# 
# class SampleListDisplayTests(SampleListTestBase):
# 
#     topElementName = 'ol'
#     viewName = 'display'
# 
# 
# class SampleListEditTests(SampleListTestBase):
# 
#     topElementName = 'div'
#     viewName = 'edit'
# 
#     def test_vocab_query(self):
#         # trivial test to make sure the sample vocabulary is working
#         # as expected
#         q = default_vocabulary.getQuery()
#         subset = q.query('1')
#         self.assertEqual(len(subset), 1)
#         subset = q.query('0 2')
#         self.assertEqual(len(subset), 2)
# 
#     def test_simple_query(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=1%202"
#                           "&field.paths-query.action-query=yep"))
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "class='results'",
#             "type='checkbox'", "value='/b/path'", "b path",
#             "type='checkbox'", "value='/c/path'", "c path",
#             ])
#         # Search index must be present:
#         self.verifyResult(r, [
#             "name='field.paths-query.start'",
#             "value='0'",
#             ], inorder=True)
#         self.verifyResultMissing(r, [
#             "type='radio'",
#             "value='/a/path'", "a path",
#             ])
# 
#     def test_simple_query_with_position_index_1(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.start=1"))
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "class='results'",
#             "type='checkbox'", "value='/b/path'", "b path",
#             "type='checkbox'", "value='/c/path'", "c path",
#             ], inorder=True)
#         self.verifyResult(r, [
#             "name='field.paths-query.start'",
#             "value='1'",
#             ], inorder=True)
#         self.verifyResultMissing(r, [
#             "value='/a/path'", "a path",
#             ])
# 
#     def test_simple_query_with_position_index_2(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.start=2"))
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "class='results'",
#             "type='checkbox'", "value='/c/path'", "c path",
#             ], inorder=True)
#         self.verifyResult(r, [
#             "name='field.paths-query.start'",
#             "value='2'",
#             ])
#         self.verifyResultMissing(r, [
#             "value='/a/path'", "a path",
#             "value='/b/path'", "b path",
#             ])
# 
#     def test_query_paging_1(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-query=yep"))
#         w.queryview.queryResultBatchSize = 2
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "class='results'",
#             "type='checkbox'", "value='/a/path'", "a path",
#             "type='checkbox'", "value='/b/path'", "b path",
#             "name='field.paths-query.action-adddone'",
#             "name='field.paths-query.action-addmore'",
#             "name='field.paths-query.action-more'",
#             "name='field.paths-query.action-dismiss'",
#             ])
#         self.verifyResultMissing(r, [
#             "type='radio'",
#             "value='/c/path'", "c path",
#             "value='/d/path'", "d path",
#             "value='/e/path'", "e path",
#             "value='/f/path'", "f path",
#             "value='/g/path'", "g path",
#             "value='/h/path'", "h path",
#             "value='/i/path'", "i path",
#             ])
# 
#     def test_query_paging_2(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path"
#                           "&field.paths-query=0%201%202"
#                           "&field.paths-query.action-more=more"
#                           "&field.paths-query.start=0"))
#         w.queryview.queryResultBatchSize = 2
#         value = w.getInputValue()
#         self.assertEqual(w.queryview.query_index, 2)
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "class='results'",
#             "value='/c/path'", "c path",
#             "name='field.paths-query.start'",
#             "value='2'",
#             ])
#         self.verifyResult(r, [
#             "name='field.paths-query.action-adddone'",
#             "name='field.paths-query.action-addmore'", "disabled",
#             "name='field.paths-query.action-more'", "disabled",
#             "name='field.paths-query.action-dismiss'",
#             ], inorder=True)
#         self.verifyResultMissing(r, [
#             # from the first page
#             "value='/a/path'", "a path",
#             "value='/b/path'", "b path",
#             # not in the query result
#             "value='/d/path'", "d path",
#             "value='/e/path'", "e path",
#             "value='/f/path'", "f path",
#             "value='/g/path'", "g path",
#             "value='/h/path'", "h path",
#             ])
# 
#     def test_selections(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths=/b/path"
#                           "&field.paths.picks=/b/path"))
#         value = w.getInputValue()
#         self.verifyResult(w.renderValueArea(value), [
#             "class='value'",
#             "value='/a/path'",
#             "</td>",
#             "value='/b/path'",
#             "checked",
#             "</table>",
#             ], inorder=True)
# 
#     def test_query_selections(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path"
#                           "&field.paths-query=0%201%202"
#                           "&field.paths.picks=/b/path"
#                           "&field.paths-query.start=0"
#                           "&field.paths-query.picks=/b/path"))
#         r = w.queryview.renderResults(w.getInputValue())
#         self.verifyResult(r, [
#             "<div",
#             "class='results'",
#             "value='/a/path'", # /a/path checked since it's in the value
#             "checked",
#             "disabled",        # but also disabled where supported
#             "value='/b/path'", # /b/path checked by the user
#             "checked",
#             "value='/c/path'", # make sure the 'checked' wasn't for /c/path
#             "</div>",
#             ], inorder=True)
# 
#     def test_new_query_resets_index(self):
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths-query=0%201%202"
#                           "&field.paths-query.start=1"
#                           "&field.paths-query.action-query=Search"))
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "<div",
#             "class='results'",
#             "value='/a/path'", "a path",
#             "value='/b/path'", "b path",
#             "value='/c/path'", "c path",
#             ])
#         # Search index must be present:
#         self.verifyResult(r, [
#             "name='field.paths-query.start'",
#             "value='0'",
#             ], inorder=True)
# 
#     def test_remove_0(self):
#         # submit a "remove" request with nothing selected from the value
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths.action-remove=Remove"
#                           "&field.paths-query.start=0"
#                           "&field.paths-query.picks=/b/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path'])
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         self.verifyResult(w.renderValueArea(value), [
#             "class='value'",
#             "value='/a/path'",
#             ])
#         self.verifyResult(w.queryview.renderResults(value), [
#             "<div",
#             "class='results'",
#             "value='/a/path'", # /a/path checked since it's in the value
#             "checked",
#             "disabled",        # but also disabled where supported
#             "value='/b/path'", # /b/path checked by the user
#             "checked",
#             "value='/c/path'", # make sure the 'checked' wasn't for /c/path
#             "</div>",
#             ], inorder=True)
# 
#     def test_remove_1(self):
#         # submit a "remove" request with one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths.action-remove=Remove"
#                           "&field.paths.picks=/a/path"
#                           "&field.paths-query.start=0"
#                           "&field.paths-query.picks=/b/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, [])
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         self.verifyResultMissing(w.renderValueArea(value), [
#             "value='/a/path'",
#             ])
#         self.verifyResult(w.queryview.renderResults(value), [
#             "class='results'",
#             "value='/a/path'", # /a/path still in result set
#             "value='/b/path'", # /b/path checked by the user
#             "checked",
#             "value='/c/path'", # make sure the 'checked' wasn't for /c/path
#             ], inorder=True)
# 
#     def test_remove_2(self):
#         # submit a "remove" request with more than one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths=/c/path"
#                           "&field.paths=/b/path"
#                           "&field.paths-query=0%201%202"
#                           "&field.paths-query.start=0"
#                           "&field.paths.action-remove=Remove"
#                           "&field.paths.picks=/a/path"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.picks=/b/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/b/path'])
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         text = w.renderValueArea(value)
#         self.verifyResult(text, [
#             "value='/b/path'", "b path",
#             ], inorder=True)
#         self.verifyResultMissing(text, [
#             "value='/a/path'", "a path",
#             "value='/c/path'", "c path",
#             ])
#         self.verifyResult(w.queryview.renderResults(value), [
#             "<div",
#             "class='results'",
#             "value='/a/path'", # /a/path still in result set
#             "value='/b/path'", # /b/path checked by the user
#             "checked",
#             "disabled",        # still in value
#             "value='/c/path'", # make sure the 'checked' wasn't for /c/path
#             ], inorder=True)
# 
#     def test_remove_missing_value(self):
#         # submit a "remove" request with value selected that isn't in the
#         # value any more (competing site users, etc.)
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/b/path&field.paths=/a/path"
#                           "&field.paths-query=0%201%202"
#                           "&field.paths.action-remove=Remove"
#                           "&field.paths.picks=/some/other/path"
#                           "&field.paths-query.picks=/b/path"))
#         self.assertEqual(w.getInputValue(), ["/b/path", "/a/path"])
# 
#     def test_add_0(self):
#         # submit an "add+done" request with nothing selected from the value
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-adddone=Add"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path'])
#         self.assert_(w.queryview.query_index is None)
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         self.verifyResult(w.renderValueArea(value), [
#             "class='value'",
#             "value='/a/path'", "a path",
#             ])
# 
#     def test_add_1(self):
#         # submit an "add+done" request with one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-adddone=Add"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.start=0"
#                           "&field.paths-query.picks=/b/path"))
#         value = w.getInputValue()
#         self.assertEqual(w.queryview.selections, ["/b/path"])
#         self.assertEqual(value, ['/a/path', '/b/path'])
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         text = w.renderValueArea(value)
#         self.verifyResult(text, [
#             "value='/a/path'", "a path",
#             "value='/b/path'","b path",
#             ])
#         self.verifyResultMissing(text, [
#             "value='/c/path'", "c path",
#             ])
#         self.assert_(w.queryview.query_index is None)
#         # force a query so we can check the interpretation of the results
#         w.queryview.query = "0 1 2"
#         w.queryview.query_index = 0
#         self.verifyResult(w.queryview.renderResults(value), [
#             "value='/a/path'", # /a/path in original value
#             "checked",
#             "disabled",
#             "value='/b/path'", # /b/path added by the user
#             "checked",
#             "disabled",
#             ], inorder=True)
# 
#     def test_add_2(self):
#         # submit an "add+done" request with one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-adddone=Add"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.picks=/b/path"
#                           "&field.paths-query.picks=/c/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path', '/b/path', '/c/path'])
#         # Make sure /a/path is still presented properly as part of the
#         # value, and receives the proper decorations in the query
#         # results:
#         self.verifyResult(w.renderValueArea(value), [
#             "value='/a/path'", "a path",
#             "value='/b/path'", "b path",
#             "value='/c/path'", "c path",
#             ])
#         self.assert_(w.queryview.query_index is None)
#         # force a query so we can check the interpretation of the results
#         w.queryview.query = "0 1 2"
#         w.queryview.query_index = 0
#         self.verifyResult(w.queryview.renderResults(value), [
#             "value='/a/path'", # /a/path in original value
#             "checked",
#             "disabled",
#             "value='/b/path'", # /b/path added by the user
#             "checked",
#             "disabled",
#             "value='/c/path'", # /b/path added by the user
#             "checked",
#             "disabled",
#             ], inorder=True)
# 
#     def test_add_unknown_value(self):
#         # test adding a value not in the vocabulary
#         qs = ("field.paths-marker=x"
#               "&field.paths=/a/path&field.paths-query=0%201%202"
#               "&field.paths-query.action-adddone=Add"
#               "&field.paths.picks=/c/path"
#               "&field.paths-query.picks=/not/a/path")
#         w = self.createWidget(QUERY_STRING=qs)
#         self.assertRaises(WidgetInputError, w.getInputValue)
# 
#     def test_add_duplicate(self):
#         # Submit an "add+more" request for a term that's already in the value.
#         # This is likely to happen with browsers that don't honor the
#         # "disabled" attribute for checkboxes (e.g., Netscape 4.79).
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-adddone=Add"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.picks=/a/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path'])
# 
#     def test_add_more_1(self):
#         # submit an "add+more" request with one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-addmore=Add"
#                           "&field.paths-query.start=0"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.picks=/b/path"))
#         w.queryview.queryResultBatchSize = 2
#         value = w.getInputValue()
#         query = w.queryview.query_text
#         self.assertEqual(value, ['/a/path', '/b/path'])
#         text = w.renderValueArea(value)
#         self.verifyResult(text, [
#             "value='/a/path'", "a path",
#             "value='/b/path'", "b path",
#             ])
#         self.verifyResultMissing(text, [
#             "value='/c/path'", "c path",
#             ])
#         # Be sure we didn't lose the query:
#         self.assertEqual(w.queryview.query_text, query)
#         text = w.queryview.renderResults(value)
#         self.verifyResult(text, [
#             "value='/c/path'", "c path",
#             ], inorder=True)
#         self.verifyResultMissing(text, [
#             "value='/a/path'",
#             "value='/b/path'",
#             "checked",
#             ])
# 
#     def test_dismiss(self):
#         # submit an "dismiss" request with one value selected
#         w = self.createWidget(
#             QUERY_STRING=("field.paths-marker=x"
#                           "&field.paths=/a/path&field.paths-query=0%201%202"
#                           "&field.paths-query.action-dismiss=Dismiss"
#                           "&field.paths-query.start=0"
#                           "&field.paths.picks=/c/path"
#                           "&field.paths-query.picks=/b/path"))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path'])
#         text = w.renderValueArea(value)
#         self.verifyResultMissing(text, [
#             "value='/b/path'", "b path",
#             "value='/c/path'", "c path",
#             ])
#         # Be sure the query was discarded:
#         text = w.queryview.renderResults(value)
#         self.assertEqual(text.strip(), "")
# 
#     def test_moveup_no_selections(self, direction="moveup"):
#         # move up request with nothing checked
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         value = w.getInputValue()
#         self.assertEqual(value, ['/a/path', '/b/path', '/c/path'])
# 
#     def test_movedown_no_selections(self):
#         self.test_moveup_no_selections("movedown")
# 
#     def check_move_leading_selections(self, direction, expected):
#         # move up request with only the leading values checked
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths.picks=/a/path"
#                                             "&field.paths.picks=/b/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         value = w.getInputValue()
#         self.assertEqual(value, expected)
# 
#     def test_moveup_leading_selections(self):
#         self.check_move_leading_selections("moveup",
#                                            ['/a/path', '/b/path', '/c/path'])
# 
#     def test_movedown_leading_selections(self):
#         self.check_move_leading_selections("movedown",
#                                            ['/c/path', '/a/path', '/b/path'])
# 
#     def check_move_middle_selection(self, direction, expected):
#         # move up request with only the middle value checked
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths.picks=/b/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         value = w.getInputValue()
#         self.assertEqual(value, expected)
# 
#     def test_moveup_middle_selection(self):
#         self.check_move_middle_selection("moveup",
#                                          ['/b/path', '/a/path', '/c/path'])
# 
#     def test_movedown_middle_selection(self):
#         self.check_move_middle_selection("movedown",
#                                          ['/a/path', '/c/path', '/b/path'])
# 
#     def check_move_trailing_selections(self, direction, expected):
#         # move up request with only the middle value checked
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths.picks=/b/path"
#                                             "&field.paths.picks=/c/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         value = w.getInputValue()
#         self.assertEqual(value, expected)
# 
#     def test_moveup_trailing_selections(self):
#         self.check_move_trailing_selections("moveup",
#                                             ['/b/path', '/c/path', '/a/path'])
# 
#     def test_movedown_trailing_selections(self):
#         self.check_move_trailing_selections("movedown",
#                                             ['/a/path', '/b/path', '/c/path'])
# 
#     def check_move_mixed_selections(self, direction, expected):
#         # move up request with selections from all over
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths=/d/path"
#                                             "&field.paths=/e/path"
#                                             "&field.paths=/f/path"
#                                             "&field.paths=/g/path"
#                                             "&field.paths=/h/path"
#                                             "&field.paths=/i/path"
#                                             "&field.paths.picks=/a/path"
#                                             "&field.paths.picks=/b/path"
#                                             "&field.paths.picks=/d/path"
#                                             "&field.paths.picks=/e/path"
#                                             "&field.paths.picks=/h/path"
#                                             "&field.paths.picks=/i/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         value = w.getInputValue()
#         self.assertEqual(value, expected)
# 
#     def test_moveup_mixed_selections(self):
#         self.check_move_mixed_selections(
#             "moveup", ['/a/path', '/b/path', '/d/path',
#                        '/e/path', '/c/path', '/f/path',
#                        '/h/path', '/i/path', '/g/path'])
# 
#     def test_movedown_mixed_selections(self):
#         self.check_move_mixed_selections(
#             "movedown", ['/c/path', '/a/path', '/b/path',
#                          '/f/path', '/d/path', '/e/path',
#                          '/g/path', '/h/path', '/i/path'])
# 
#     def check_move_missing_selections(self, direction):
#         # Selections aren't actually in the value list (i.e., bogus
#         # request, or competing site users).
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths=/c/path"
#                                             "&field.paths.picks=/this/path"
#                                             "&field.paths.picks=/that/path"
#                                             "&field.paths.action-%s=yep"
#                                             % direction))
#         self.assertEqual(w.getInputValue(), ["/a/path", "/b/path", "/c/path"])
# 
#     def test_moveup_missing_selections(self, direction="moveup"):
#         self.check_move_missing_selections("moveup")
# 
#     def test_movedown_missing_selections(self):
#         self.check_move_missing_selections("movedown")
# 
#     def test_query_form_without_type(self):
#         w = self.createWidget(QUERY_STRING="field.paths-query=0")
#         value = w.getInputValue()
#         text = w.queryview.renderInput()
#         self.verifyResult(text, [
#             "<select",
#             "name='field.paths-query.type'",
#             "<option", "value=''", "selected",
#             # We reach in here so we don't have to know the default
#             # text, or how the translation service is hooked in.
#             w.translate(complexsample._msg_any_content_type),
#             "<option", ">abc<",
#             "<option", ">def<",
#             "<option", ">ghi<",
#             "</select>",
#             ], inorder=True)
# 
# 
# class SampleListQueryTests(TestBase):
# 
#     viewName = "edit"
# 
#     def setUp(self):
#         TestBase.setUp(self)
#         vocab = ProxyVocabulary(default_vocabulary)
#         vocab.getQuery = lambda v=vocab: QueryComplainer(v)
#         unbound = vocabulary.VocabularyUniqueListField(__name__="paths",
#                                                        vocabulary=vocab,
#                                                        required=False)
#         self.bound = unbound.bind(object())
# 
#     def checkQuery(self, querytype, expectedtype):
#         qs = ("field.paths-query=1%202"
#               "&field.paths-query.start=0"
#               "&field.paths-query.action-query=yep")
#         if querytype is not None:
#             qs += "&field.paths-query.type=" + querytype
#         w = self.createWidget(QUERY_STRING=qs)
#         w.getInputValue()
#         try:
#             w.queryview.getResults()
#         except QueryComplainer, e:
#             self.assertEqual(e.text, "1 2")
#             self.assertEqual(e.type, expectedtype)
#         else:
#             self.fail("expected QueryComplainer.query to raise exception")
# 
#     def test_call_without_type(self):
#         self.checkQuery(None, None)
# 
#     def test_call_with_known_type(self):
#         self.checkQuery("abc", "abc")
# 
#     def test_call_with_unknown_type(self):
#         self.checkQuery("splay", None)
# 
#     def test_setRenderedValue_doesnt_suppress_supplemental_form_data_1(self):
#         w = self.createWidget(QUERY_STRING=("field.paths-marker=x"
#                                             "&field.paths=/a/path"
#                                             "&field.paths=/b/path"
#                                             "&field.paths.picks=/a/path"))
#         self.assertEqual(w.getInputValue(), ['/a/path','/b/path'])
#         self.assertEqual(w.selections, ['/a/path'])
# 
#     def test_setRenderedValue_doesnt_suppress_supplemental_form_data_2(self):
#         w = self.createWidget()
#         w.setRenderedValue(['/c/path'])
#         self.assertEqual(w.getInputValue(), ['/c/path'])
#         r = w()
#         self.verifyResult(r, ["/c/path"])
#         self.verifyResultMissing(r, ["/a/path", "/b/path"])
#         self.assertEqual(w.selections, [])
# 
# 
# class SingleSampleTests(TestBase):
# 
#     unbound = vocabulary.VocabularyField(
#         __name__="path",
#         vocabulary=default_vocabulary,
#         required=False)
# 
#     def setUp(self):
#         TestBase.setUp(self)
#         self.bound = self.unbound.bind(object())
#         # register the single-selection widgets
#         # display
#         ztapi.browserView(
#             IVocabularyField,
#             "display",
#             vocabularywidget.VocabularyFieldDisplayWidget)
#         ztapi.browserView(
#             ISampleVocabulary,
#             "field-display-widget",
#             complexsample.SampleDisplay)
#         # edit
#         ztapi.browserView(
#             IVocabularyField,
#             "edit",
#             vocabularywidget.VocabularyFieldEditWidget)
#         ztapi.browserView(
#             ISampleVocabulary,
#             "field-edit-widget",
#             complexsample.SampleEdit)
#         # query support (edit only) -- 
#         ztapi.browserView(
#             IFancySampleVocabularyQuery,
#             "widget-query-helper",
#             complexsample.FancySampleQueryView)
#         ztapi.browserView(
#             ISampleVocabularyQuery,
#             "widget-query-helper",
#             complexsample.SampleQueryView)
# 
#     def test_display_empty(self):
#         self.viewName = "display"
#         w = self.createWidget()
#         self.verifyResult(w(), ["no value"])
# 
#     def test_display_with_form_data(self):
#         self.viewName = "display"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path=/a/path"))
#         self.verifyResult(w(), ["/a/path"])
# 
#     def test_display_with_bad_form_data(self):
#         self.viewName = "display"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path=/invalid/path"))
#         self.verifyResult(w(), [
#             "out-of-date value",
#             "/invalid/path",
#             complexsample._msg_inaccessible_object.default,
#             ])
# 
#     def test_edit_without_form_data(self):
#         self.viewName = "edit"
#         w = self.createWidget()
#         self.assert_(not w.hasInput())
#         self.verifyResult(w(), [
#             "no value",
#             "field.path.action-clear",
#             "disabled",
#             ])
# 
#     def test_edit_with_empty_form_data(self):
#         self.viewName = "edit"
#         w = self.createWidget(QUERY_STRING="field.path-marker=x")
#         self.verifyResult(w(), [
#             "no value",
#             "field.path.action-clear",
#             "disabled",
#             ])
# 
#     def test_edit_select_clears_query(self):
#         self.viewName = "edit"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path-query.action-select=x"
#                                             "&field.path-query.picks=/a/path"
#                                             "&field.path-query=0%201"))
#         self.assertEqual(w.getInputValue(), "/a/path")
#         r = w()
#         self.verifyResult(r, [
#             "a path",
#             "/a/path",
#             "field.path.action-clear",
#             ])
#         self.verifyResultMissing(r, [
#             "disabled",
#             "field.path-query.start"
#             ])
# 
#     def test_edit_dismiss_clears_query(self):
#         self.viewName = "edit"
#         w = self.createWidget(
#             QUERY_STRING=("field.path-marker=x"
#                           "&field.path=/b/path"
#                           "&field.path-query.action-dismiss=x"
#                           "&field.path-query.picks=/a/path"
#                           "&field.path-query=0%201"))
#         self.assertEqual(w.getInputValue(), "/b/path")
#         r = w()
#         self.verifyResult(r, [
#             "b path",
#             "/b/path",
#             "field.path.action-clear",
#             ])
#         self.verifyResultMissing(r, [
#             "disabled",
#             "field.path-query.start"
#             ])
# 
#     def test_edit_clear_removes_value(self):
#         self.viewName = "edit"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path.action-clear=x"
#                                             "&field.path=/a/path"))
#         self.assertEqual(w.getInputValue(), None)
#         # Make sure Clear is disabled in the resulting form:
#         self.verifyResult(w(), [
#             "no value",
#             "field.path.action-clear",
#             "disabled",
#             ])
# 
#     def test_edit_with_form_data(self):
#         self.viewName = "edit"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path=/a/path"))
#         r = w()
#         self.verifyResult(r, [
#             "<input",
#             'value="/a/path"',
#             "/>",
#             ], inorder=True)
#         self.verifyResult(r, [
#             "<div",
#             "class='widget-work-area'",
#             "<div",
#             "class='query'",
#             "<table",
#             "Select content type",
#             "<select", "name='field.path-query.type'",
#             "<option", "value=''", "any", "</option>",
#             "<option", "value='abc'", ">abc", "</option>",
#             "<option", "value='def'", ">def", "</option>",
#             "<option", "value='ghi'", ">ghi", "</option>",
#             "</select>",
#             ], inorder=True)
#         self.verifyResult(r, [
#             "class='query'",
#             "<table",
#             "Search for",
#             "<input", "name='field.path-query'", "/>",
#             "</table>",
#             ], inorder=True)
# 
#     def test_edit_with_query(self):
#         self.viewName = "edit"
#         w = self.createWidget(QUERY_STRING=("field.path-marker=x"
#                                             "&field.path=/a/path"
#                                             "&field.path-query.start=0"
#                                             "&field.path-query=0%201"))
#         value = w.getInputValue()
#         r = w.queryview.renderResults(value)
#         self.verifyResult(r, [
#             "<input",
#             "name='field.path-query.start'",
#             "value='0'",
#             ])
#         self.verifyResult(r, [
#             # query results
#             "<div", "class='results'",
#             #   first item
#             "<input", "type='radio'", "value='/a/path'",
#             "name='field.path-query.picks'",
#             "checked", "a path",
#             #   second item
#             "<input", "type='radio'", "value='/b/path'",
#             "name='field.path-query.picks'",
#             "b path",
#             # end
#             "</div>",
#             ], inorder=True)
#         self.verifyResult(r, [
#             # query result actions
#             "<div", "class='results'",
#             "<input", "type='submit'", "name='field.path-query.action-select'",
#             "<input", "type='submit'", "name='field.path-query.action-more'",
#             "disabled",
#             "<input", "type='submit'", "name='field.path-query.action-dismiss'",
#             "</div>",
#             ], inorder=True)
# 
# 
# class ConfigurationTest(PlacelessSetup, unittest.TestCase):
# 
#     def test_load_zcml(self):
#         xmlconfig.string("""\
#         <configure xmlns='http://namespaces.zope.org/zope'>
#           <include package='zope.app.component' file='meta.zcml' />
#           <include package='zope.app.event' file='meta.zcml' />
#           <include package='zope.app.publisher.browser' file='meta.zcml' />
#           <include package='zope.app.schema' file='meta.zcml' />
# 
#           <include package='zope.app.form.browser.complexsample' />
#         </configure>
#         """)
# 
# 
# def show(s):
#     f = file("/dev/tty", "w")
#     print >>f
#     print >>f, s
#     f.close()


def test_suite():
    #suite = unittest.makeSuite(SampleListEditTests)
    #suite.addTest(unittest.makeSuite(SampleListQueryTests))
    #suite.addTest(unittest.makeSuite(SampleListDisplayTests))
    #suite.addTest(unittest.makeSuite(SingleSampleTests))
    #suite.addTest(unittest.makeSuite(ConfigurationTest))
    #return suite
    return unittest.TestSuite()

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
