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
"""Tests of the example vocabularies provided for functional tests.

$Id$
"""
import unittest
# 
# from zope.app.form.browser.complexsample import vocabulary
# 
# 
# class QueryTests(unittest.TestCase):
#     createQuery = vocabulary.SampleVocabularyQuery
# 
#     def setUp(self):
#         self.vocab = vocabulary.SampleVocabulary()
#         self.queryobj = self.createQuery(self.vocab)
# 
#     def test_null_query(self):
#         results = self.queryobj.query('')
#         self.assertEqual(results.terms, self.vocab.terms)
# 
#     def test_simple_query(self):
#         results = self.queryobj.query('bravo')
#         self.assertEqual(len(results), 3)
#         for term in results.terms:
#             self.assert_('bravo' in term.keywords)
# 
# 
# class FancyQueryTests(QueryTests):
#     createQuery = vocabulary.FancySampleVocabularyQuery
# 
#     def test_query_by_group(self):
#         results = self.queryobj.query('', "3. final third")
#         self.assertEqual(len(results), len(vocabulary.allTerms) // 3)
#         for term in results:
#             self.assert_(term.group == "3. final third")
# 
#     def test_query_including_group(self):
#         results = self.queryobj.query('bravo', "3. final third")
#         for term in results:
#             self.assert_(term.group == "3. final third")
#             self.assert_('bravo' in term.keywords)
# 
# 
def test_suite():
    #suite = unittest.makeSuite(QueryTests)
    #suite.addTest(unittest.makeSuite(FancyQueryTests))
    #return suite
    return unittest.TestSuite()

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
