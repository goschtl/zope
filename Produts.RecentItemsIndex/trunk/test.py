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
"""Tests for RecentItemsIndex

$Id: test.py,v 1.5 2004/08/10 16:01:26 caseman Exp $"""

import os
from unittest import TestCase, TestSuite, main, makeSuite

import ZODB
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime


class Doc:
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        
class DummyCatalog(SimpleItem):
    
    docs = {}
    
    def __getitem__(self, item):
        return self.docs[item]

class Viewable(SimpleItem):
    
    date = DateTime('2/21/2004')
    type = 'Viewable'
    
    def __init__(self, role=None):
        self._addRole(role)
        if role is not None:
            self.manage_permission('View', [role])

class RecentItemsIndexTest(TestCase):

    def setUp(self):
        from Products.RecentItemsIndex.index import RecentItemsIndex
        self.test = DummyCatalog()
        self.test.index = RecentItemsIndex('test', 'type', 'date', 10)
        self.index = self.test.index
        
    def test_construct_with_extra(self):
        # Simulate instantiating from ZCatalog
        from Products.RecentItemsIndex.index import RecentItemsIndex
        class extra:
            field_name = 'bruford'
            date_name = 'wakeman'
            max_length = 25
            guard_roles = ['Anonymous']
            guard_permission = 'View'
        index = RecentItemsIndex('extra', extra=extra)
        self.assertEqual(index.getId(), 'extra')
        self.assertEqual(index.field_name, 'bruford')
        self.assertEqual(index.date_name, 'wakeman')
        self.assertEqual(index.max_length, 25)
        self.assertEqual(tuple(index.guard_roles), ('Anonymous',))
        self.assertEqual(index.guard_permission, 'View')
        
    def test_construct_with_no_classifier_or_guard(self):
        # Simulate instantiating from ZCatalog
        from Products.RecentItemsIndex.index import RecentItemsIndex
        class extra:
            date_name = 'modified'
            max_length = 30
        index = RecentItemsIndex('nuttin', extra=extra)
        self.assertEqual(index.getId(), 'nuttin')
        self.assertEqual(index.date_name, 'modified')
        self.assertEqual(index.max_length, 30)
    
    def test_construct_with_bogus_max_length(self):
        from Products.RecentItemsIndex.index import RecentItemsIndex
        self.assertRaises(
            Exception, RecentItemsIndex, 'test', 'type', 'date', 0)
        self.assertRaises(
            Exception, RecentItemsIndex, 'test', 'type', 'date', -20)

    def test_index_single(self):
        doc = Doc(type='fluke', date=DateTime('1/1/2004'))
        self.failUnless(self.index.index_object(1, doc))
        self.assertEqual(self.index.numObjects(), 1)
        self.assertEqual(self.index.getItemCounts(), {'fluke': 1})
    
    def test_exclude_obj_without_field_and_date(self):
        doc = Doc()
        self.failIf(self.index.index_object(1, doc))
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})
        doc = Doc(type='cheetos')
        self.failIf(self.index.index_object(1, doc))
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})
        doc = Doc(date=DateTime('4/17/2004'))
        self.failIf(self.index.index_object(1, doc))
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})         

    def test_unindex_single(self):
        self.test_index_single()
        self.failUnless(self.index.unindex_object(1))
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})
    
    def test_index_many(self):
        types = ['huey', 'dooey', 'looey', 'dooey'] * 15
        date = DateTime('1/1/2004')
        docs = {}
        for docid, typ in zip(range(len(types)), types):
            if not docid % 3:
                date = date + 1
            if not docid % 7:
                date = date - (docid % 3)
            doc = docs[docid] = Doc(docid=docid, type=typ, date=date)
            self.index.index_object(docid, doc)
        maxlen = self.index.max_length
        self.assertEqual(self.index.getItemCounts(), 
                         {'huey': maxlen, 'dooey':maxlen, 'looey':maxlen})
        self.assertEqual(self.index.numObjects(), maxlen*3)
        self.test.docs = docs
        return docs
    
    def test_index_many_no_classifier(self):
        from Products.RecentItemsIndex.index import RecentItemsIndex
        self.test.index = RecentItemsIndex('test', None, 'date', 10)
        self.index = self.test.index
        types = ['huey', 'dooey', 'looey', 'dooey'] * 15
        date = DateTime('1/1/2004')
        docs = {}
        for docid, typ in zip(range(len(types)), types):
            if not docid % 3:
                date = date + 1
            if not docid % 7:
                date = date - (docid % 3)
            doc = docs[docid] = Doc(docid=docid, type=typ, date=date)
            self.index.index_object(docid, doc)
        maxlen = self.index.max_length
        self.assertEqual(self.index.getItemCounts(), {None: maxlen,})
        self.assertEqual(self.index.numObjects(), maxlen)
        self.test.docs = docs
        return docs
    
    def test_unindex_one_type(self):
        docs = self.test_index_many()
        for docid, doc in docs.items():
            if doc.type == 'looey':
                self.index.unindex_object(docid)
        self.assertEqual(self.index.numObjects(), 20)
        self.assertEqual(self.index.getItemCounts(), {'huey': 10, 'dooey':10})           

    def test_unindex_all(self):
        docs = self.test_index_many()
        for docid in docs.keys():
            self.index.unindex_object(docid)
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})
        self.assertEqual(list(self.index.uniqueValues()), [])
    
    def _get_top_docs(self, docs):
        top = {'huey':[], 'dooey':[], 'looey':[]}        
        for doc in docs.values():
            top[doc.type].append((doc.date.timeTime(), doc.docid))
        for typ, docs in top.items():
            docs.sort()
            top[typ] = docs[-10:]
        return top
        
    def test_getEntryForObject(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        for docid, doc in docs.items():
            entry = self.index.getEntryForObject(docid)
            if entry is not None:
                self.assertEqual(entry, 
                    {'value': doc.type, 'date': doc.date.timeTime()})
            else:
                self.failIf((doc.date.timeTime(), doc.docid) in top[doc.type])
    
    def test_unindex_most_recent(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        item_counts = self.index.getItemCounts()
        total_count = 30
        for i in range(10):
            for typ in ('huey', 'dooey', 'looey'):
                nil, byebyeid = top[typ].pop()
                self.failUnless(self.index.unindex_object(byebyeid))
                item_counts[typ] -= 1
                if not item_counts[typ]:
                    del item_counts[typ]
                total_count -= 1
                self.assertEqual(self.index.getItemCounts(), item_counts)
                self.assertEqual(self.index.numObjects(), total_count)
        self.assertEqual(self.index.numObjects(), 0)
        self.assertEqual(self.index.getItemCounts(), {})
    
    def test_unindex_bogus_rid(self):
        self.test_index_many()
        self.failIf(self.index.unindex_object(-2000))
    
    def _get_indexed_doc(self, fromtop=0):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        items = docs.items()
        if fromtop:
            items.reverse()
        for docid, doc in items:
            entry = self.index.getEntryForObject(docid)
            if entry is not None:
                break
        else:
            self.fail('No objects in index')
        self.assertEqual(entry, {'value':doc.type, 'date':doc.date.timeTime()})
        return doc
    
    def test_reindex_no_change(self):
        # reindex with no change should be a no-op
        doc = self._get_indexed_doc()
        self.failIf(self.index.index_object(doc.docid, doc))
        self.assertEqual(self.index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})
    
    def test_reindex_change_date(self):
        doc = self._get_indexed_doc()
        doc.date = doc.date + 10
        self.failUnless(self.index.index_object(doc.docid, doc))
        self.assertEqual(self.index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})
    
    def test_reindex_change_value(self):
        doc = self._get_indexed_doc(fromtop=1)
        oldtype = doc.type
        for typ in self.index.uniqueValues():
            if typ != oldtype:
                doc.type = typ
                break
        self.failUnless(self.index.index_object(doc.docid, doc))
        self.assertEqual(self.index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})
    
    def test_reindex_change_date_and_value(self):
        doc = self._get_indexed_doc(fromtop=1)
        doc.date = doc.date + 4
        oldtype = doc.type
        for typ in self.index.uniqueValues():
            if typ != oldtype:
                doc.type = typ
                break
        self.failUnless(self.index.index_object(doc.docid, doc))
        self.assertEqual(self.index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})
    
    def test_query_empty_index(self):
        result = self.index.query('foobar')
        self.failIf(result)
        
    def test_simple_query(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query('huey')
        expected = [docid for nil, docid in top['huey']]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected)
    
    def test_query_bogus_value(self):
        docs = self.test_index_many()
        self.failIf(self.index.query('snacks'))
        
    def test_query_limit(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query('huey', limit=3)
        expected = [docid for nil, docid in top['huey']]
        expected.reverse()
        expected = expected[:3]
        self.assertEqual([doc.docid for doc in result], expected)
    
    def test_query_no_merge(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query('dooey', merge=0)
        expected = [(date, docid, self.test.__getitem__) 
                    for date, docid in top['dooey']]
        expected.reverse()
        for rrow, erow in zip(result, expected):
           self.assertEqual(rrow[:2], erow[:2])        
    
    def test_query_multiple_values(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query(['huey', 'dooey'])
        expected = top['huey'] + top['dooey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected)
        return expected
    
    def test_query_all_values(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query()
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected)
        return expected

    def test_query_no_classifier(self):
        docs = self.test_index_many_no_classifier()
        top = self._get_top_docs(docs)
        result = self.index.query()
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected[:10])

    def test_query_no_classifier_ignores_value(self):
        docs = self.test_index_many_no_classifier()
        top = self._get_top_docs(docs)
        result = self.index.query('ptooey')
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected[:10])
        
    def test_query_multiple_with_tuple(self):
        expected = self.test_query_multiple_values()
        result = self.index.query(('huey', 'dooey'))
        self.assertEqual([doc.docid for doc in result], expected)
        
    def test_query_multiple_bogus_values(self):
        self.failIf(self.index.query(['fooey', 'blooey']))
        result = self.index.query(['blooey', 'looey'])
        expected = self.index.query('looey')
        self.assertEqual(list(result), list(expected))
        
    def test_query_multiple_limit(self):
        expected = self.test_query_multiple_values()[:4]
        result = self.index.query(['huey', 'dooey'], limit=4)
        self.assertEqual([doc.docid for doc in result], expected)
    
    def test_query_multiple_no_merge(self):
        docs = self.test_index_many()
        top = self._get_top_docs(docs)
        result = self.index.query(['dooey', 'huey'], merge=0)
        expected = [(date, docid, self.test.__getitem__) 
                    for date, docid in top['huey'] + top['dooey']]
        expected.sort()
        expected.reverse()
        for rrow, erow in zip(result, expected):
           self.assertEqual(rrow[:2], erow[:2]) 
        
    def test_apply_index(self):
        # _apply_index always returns none since recent items index
        # do not participate in the normal ZCatalog query as they
        # handle both intersection and sorting
        self.failUnless(self.index._apply_index({}) is None)
        self.failUnless(self.index._apply_index({'query':'looey'}) is None)
    
    def test_uniqueValues(self):
        self.failIf(self.index.uniqueValues('type'))
        docs = self.test_index_many()
        values = list(self.index.uniqueValues('type'))
        values.sort()
        self.assertEqual(values, ['dooey', 'huey', 'looey'])
        self.failIf(self.index.uniqueValues('carbtastic'))
    
    def test_hasUniqueValuesFor(self):
        self.failUnless(self.index.hasUniqueValuesFor('type'))
        self.failIf(self.index.hasUniqueValuesFor('spork'))
    
    def test_numObjects(self):
        docs = self.test_index_many()
        self.assertEqual(self.index.numObjects(), 30)
    
    def test_numObjects_small_maxlen(self):
        self.index.max_length = 1
        docs = self.test_index_many()
        self.assertEqual(self.index.numObjects(), 3)
    
    def test_numObjects_empty_index(self):
        self.assertEqual(self.index.numObjects(), 0)
        
    def test_clear(self):
        self.test_index_many()
        self.failUnless(self.index.numObjects())
        self.index.clear()
        self.assertEqual(self.index.numObjects(), 0)
    
    def test_role_permission_guard(self):
        from Products.RecentItemsIndex.index import RecentItemsIndex
        index = RecentItemsIndex(
            'test', 'type', 'date', 5, ['NerfHerder', 'Bloke'], 'View')
        viewable = Viewable('NerfHerder')
        index.index_object(0, viewable)
        self.assertEqual(index.numObjects(), 1)
        notviewable = Viewable()
        index.index_object(1, notviewable)
        self.assertEqual(index.numObjects(), 1)
        bloke = Viewable('Bloke')
        index.index_object(2, bloke)
        self.assertEqual(index.numObjects(), 2)
        bloke.manage_permission('View', [])
        index.index_object(2, bloke)
        self.assertEqual(index.numObjects(), 1)
        dummy = Viewable('Dummy')
        index.index_object(3, dummy)
        self.assertEqual(index.numObjects(), 1)        
        viewable.manage_permission('View', [])
        index.index_object(0, viewable)
        self.assertEqual(index.numObjects(), 0)
        
def test_suite():
    return TestSuite((makeSuite(RecentItemsIndexTest),))

if __name__=='__main__':
    main(defaultTest='test_suite')
