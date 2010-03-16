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
""" Tests for Products.RecentItemsIndex.index
"""
import unittest

class RecentItemsIndexTest(unittest.TestCase):

    def _getTargetClass(self):
        from Products.RecentItemsIndex.index import RecentItemsIndex
        return RecentItemsIndex

    def _makeOne(self,
                 id='test',
                 field_name='type',
                 date_name='date',
                 max_length=10,
                 *args, **kw):
        catalog = self._makeCatalog()
        klass = self._getTargetClass()
        index = klass(id, field_name, date_name, max_length, *args, **kw)
        return index.__of__(catalog)

    def _makeDoc(self, **kw):

        class Doc:
            def __init__(self, **kw):
                self.__dict__.update(kw)
        return Doc(**kw)

    def _makeCatalog(self):
        from OFS.SimpleItem import SimpleItem

        class DummyCatalog(SimpleItem):

            def __init__(self):
                self.docs = {}

            def __getitem__(self, item):
                return self.docs[item]

        return DummyCatalog()

    def _makeViewable(self, id='test_viewable'):
        from OFS.SimpleItem import SimpleItem
        from DateTime.DateTime import DateTime

        class Viewable(SimpleItem):

            date = DateTime('2/21/2004')
            type = 'Viewable'

            def __init__(self, role=None):
                self._addRole(role)
                if role is not None:
                    self.manage_permission('View', [role])

        return Viewable(id)

    def _makeAndIndexOneDoc(self, index):
        from DateTime.DateTime import DateTime
        doc = self._makeDoc(type='fluke', date=DateTime('1/1/2004'))
        return index.index_object(1, doc)

    def _makeAndIndexDocs(self, index):
        from Acquisition import aq_parent
        from DateTime.DateTime import DateTime
        types = ['huey', 'dooey', 'looey', 'dooey'] * 15
        date = DateTime('1/1/2004')
        docs = {}
        for docid, typ in zip(range(len(types)), types):
            if not docid % 3:
                date = date + 1
            if not docid % 7:
                date = date - (docid % 3)
            doc = docs[docid] = self._makeDoc(docid=docid, type=typ, date=date)
            index.index_object(docid, doc)
        aq_parent(index).docs = docs
        return docs

    def test_class_conforms_to_IPluggableIndex(self):
        from zope.interface.verify import verifyClass
        from Products.PluginIndexes.interfaces import IPluggableIndex
        verifyClass(IPluggableIndex, self._getTargetClass())

    def test_instance_conforms_to_IPluggableIndex(self):
        from zope.interface.verify import verifyObject
        from Products.PluginIndexes.interfaces import IPluggableIndex
        index = self._makeOne()
        verifyObject(IPluggableIndex, index)

    def test_class_conforms_to_IUniqueValueIndex(self):
        from zope.interface.verify import verifyClass
        from Products.PluginIndexes.interfaces import IUniqueValueIndex
        verifyClass(IUniqueValueIndex, self._getTargetClass())

    def test_instance_conforms_to_IUniqueValueIndex(self):
        from zope.interface.verify import verifyObject
        from Products.PluginIndexes.interfaces import IUniqueValueIndex
        index = self._makeOne()
        verifyObject(IUniqueValueIndex, index)

    def test_construct_with_extra(self):
        # Simulate instantiating from ZCatalog
        class extra:
            field_name = 'bruford'
            date_name = 'wakeman'
            max_length = 25
            guard_roles = ['Anonymous']
            guard_permission = 'View'
        index = self._getTargetClass()('extra', extra=extra)
        self.assertEqual(index.getId(), 'extra')
        self.assertEqual(index.field_name, 'bruford')
        self.assertEqual(index.date_name, 'wakeman')
        self.assertEqual(index.max_length, 25)
        self.assertEqual(tuple(index.guard_roles), ('Anonymous',))
        self.assertEqual(index.guard_permission, 'View')

    def test_construct_with_no_classifier_or_guard(self):
        # Simulate instantiating from ZCatalog
        class extra:
            date_name = 'modified'
            max_length = 30
        index = self._getTargetClass()('nuttin', extra=extra)
        self.assertEqual(index.getId(), 'nuttin')
        self.assertEqual(index.date_name, 'modified')
        self.assertEqual(index.max_length, 30)

    def test_construct_with_bogus_max_length(self):
        self.assertRaises(
            Exception, self._getTargetClass(), 'test', 'type', 'date', 0)
        self.assertRaises(
            Exception, self._getTargetClass(), 'test', 'type', 'date', -20)

    def test_index_object_skips_obj_without_field_or_date(self):
        index = self._makeOne()
        doc = self._makeDoc()
        self.failIf(index.index_object(1, doc))
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})

    def test_index_object_skips_obj_without_date(self):
        index = self._makeOne()
        doc = self._makeDoc(type='cheetos')
        self.failIf(index.index_object(1, doc))
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})

    def test_index_object_skips_obj_without_field(self):
        from DateTime.DateTime import DateTime
        index = self._makeOne()
        doc = self._makeDoc(date=DateTime('4/17/2004'))
        self.failIf(index.index_object(1, doc))
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})

    def test_index_single(self):
        index = self._makeOne()
        result = self._makeAndIndexOneDoc(index)
        self.failUnless(result)
        self.assertEqual(index.numObjects(), 1)
        self.assertEqual(index.getItemCounts(), {'fluke': 1})

    def test_unindex_single(self):
        index = self._makeOne()
        result = self._makeAndIndexOneDoc(index)
        self.failUnless(index.unindex_object(1))
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})

    def test_index_many(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        maxlen = index.max_length
        self.assertEqual(index.getItemCounts(),
                         {'huey': maxlen, 'dooey':maxlen, 'looey':maxlen})
        self.assertEqual(index.numObjects(), maxlen*3)

    def test_index_many_no_classifier(self):
        index = self._makeOne('test', None, 'date', 10)
        docs = self._makeAndIndexDocs(index)
        maxlen = index.max_length
        self.assertEqual(index.getItemCounts(), {None: maxlen,})
        self.assertEqual(index.numObjects(), maxlen)

    def test_unindex_one_type(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        for docid, doc in docs.items():
            if doc.type == 'looey':
                index.unindex_object(docid)
        self.assertEqual(index.numObjects(), 20)
        self.assertEqual(index.getItemCounts(), {'huey': 10, 'dooey':10})

    def test_unindex_all(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        for docid in docs.keys():
            index.unindex_object(docid)
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})
        self.assertEqual(list(index.uniqueValues()), [])

    def _get_top_docs(self, docs):
        top = {'huey':[], 'dooey':[], 'looey':[]}
        for doc in docs.values():
            top[doc.type].append((doc.date.timeTime(), doc.docid))
        for typ, docs in top.items():
            docs.sort()
            top[typ] = docs[-10:]
        return top

    def test_getEntryForObject(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        for docid, doc in docs.items():
            entry = index.getEntryForObject(docid)
            if entry is not None:
                self.assertEqual(entry,
                    {'value': doc.type, 'date': doc.date.timeTime()})
            else:
                self.failIf((doc.date.timeTime(), doc.docid) in top[doc.type])

    def test_unindex_most_recent(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        item_counts = index.getItemCounts()
        total_count = 30
        for i in range(10):
            for typ in ('huey', 'dooey', 'looey'):
                nil, byebyeid = top[typ].pop()
                self.failUnless(index.unindex_object(byebyeid))
                item_counts[typ] -= 1
                if not item_counts[typ]:
                    del item_counts[typ]
                total_count -= 1
                self.assertEqual(index.getItemCounts(), item_counts)
                self.assertEqual(index.numObjects(), total_count)
        self.assertEqual(index.numObjects(), 0)
        self.assertEqual(index.getItemCounts(), {})

    def test_unindex_bogus_rid(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        self.failIf(index.unindex_object(-2000))

    def _get_indexed_doc(self, index, fromtop=0):
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        items = docs.items()
        if fromtop:
            items.reverse()
        for docid, doc in items:
            entry = index.getEntryForObject(docid)
            if entry is not None:
                break
        else:
            self.fail('No objects in index')
        self.assertEqual(entry, {'value':doc.type, 'date':doc.date.timeTime()})
        return doc

    def test_reindex_no_change(self):
        # reindex with no change should be a no-op
        index = self._makeOne()
        doc = self._get_indexed_doc(index)
        self.failIf(index.index_object(doc.docid, doc))
        self.assertEqual(index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})

    def test_reindex_change_date(self):
        index = self._makeOne()
        doc = self._get_indexed_doc(index)
        doc.date = doc.date + 10
        self.failUnless(index.index_object(doc.docid, doc))
        self.assertEqual(index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})

    def test_reindex_change_value(self):
        index = self._makeOne()
        doc = self._get_indexed_doc(index, fromtop=1)
        oldtype = doc.type
        for typ in index.uniqueValues():
            if typ != oldtype:
                doc.type = typ
                break
        self.failUnless(index.index_object(doc.docid, doc))
        self.assertEqual(index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})

    def test_reindex_change_date_and_value(self):
        index = self._makeOne()
        doc = self._get_indexed_doc(index, fromtop=1)
        doc.date = doc.date + 4
        oldtype = doc.type
        for typ in index.uniqueValues():
            if typ != oldtype:
                doc.type = typ
                break
        self.failUnless(index.index_object(doc.docid, doc))
        self.assertEqual(index.getEntryForObject(doc.docid),
                         {'value':doc.type, 'date':doc.date.timeTime()})

    def test_query_empty_index(self):
        index = self._makeOne()
        result = index.query('foobar')
        self.failIf(result)

    def test_simple_query(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query('huey')
        expected = [docid for nil, docid in top['huey']]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected)

    def test_query_bogus_value(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        self.failIf(index.query('snacks'))

    def test_query_limit(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query('huey', limit=3)
        expected = [docid for nil, docid in top['huey']]
        expected.reverse()
        expected = expected[:3]
        self.assertEqual([doc.docid for doc in result], expected)

    def test_query_no_merge(self):
        from Acquisition import aq_parent
        index = self._makeOne()
        catalog = aq_parent(index)
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query('dooey', merge=0)
        expected = [(date, docid, catalog.__getitem__)
                    for date, docid in top['dooey']]
        expected.reverse()
        for rrow, erow in zip(result, expected):
           self.assertEqual(rrow[:2], erow[:2])

    def _getExpectedTopDocs(self, index, docs, limit=None):
        top = self._get_top_docs(docs)
        query = ['huey', 'dooey']
        if limit is None:
            result = index.query(query)
        else:
            result = index.query(query, limit=limit)
        expected = top['huey'] + top['dooey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        return result, expected

    def test_query_multiple_values(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        result, expected = self._getExpectedTopDocs(index, docs)
        self.assertEqual([doc.docid for doc in result], expected)

    def test_query_all_values(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query()
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected)
        return expected

    def test_query_no_classifier(self):
        index = self._makeOne('test', None, 'date', 10)
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query()
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected[:10])

    def test_query_no_classifier_ignores_value(self):
        index = self._makeOne('test', None, 'date', 10)
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query('ptooey')
        expected = top['huey'] + top['dooey'] + top['looey']
        expected.sort()
        expected = [docid for nil, docid in expected]
        expected.reverse()
        self.assertEqual([doc.docid for doc in result], expected[:10])

    def test_query_multiple_with_tuple(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        result, expected = self._getExpectedTopDocs(index, docs)
        self.assertEqual([doc.docid for doc in result], expected)

    def test_query_multiple_bogus_values(self):
        index = self._makeOne()
        self.failIf(index.query(['fooey', 'blooey']))
        result = index.query(['blooey', 'looey'])
        expected = index.query('looey')
        self.assertEqual(list(result), list(expected))

    def test_query_multiple_limit(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        result, expected = self._getExpectedTopDocs(index, docs, limit=4)
        expected = expected[:4]
        self.assertEqual([doc.docid for doc in result], expected)

    def test_query_multiple_no_merge(self):
        from Acquisition import aq_parent
        index = self._makeOne()
        catalog = aq_parent(index)
        docs = self._makeAndIndexDocs(index)
        top = self._get_top_docs(docs)
        result = index.query(['dooey', 'huey'], merge=0)
        expected = [(date, docid, catalog.__getitem__)
                    for date, docid in top['huey'] + top['dooey']]
        expected.sort()
        expected.reverse()
        for rrow, erow in zip(result, expected):
           self.assertEqual(rrow[:2], erow[:2])

    def test_apply_index(self):
        # _apply_index always returns none since recent items index
        # do not participate in the normal ZCatalog query as they
        # handle both intersection and sorting
        index = self._makeOne()
        self.failUnless(index._apply_index({}) is None)
        self.failUnless(index._apply_index({'query':'looey'}) is None)

    def test_uniqueValues(self):
        index = self._makeOne()
        self.failIf(index.uniqueValues('type'))
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        values = list(index.uniqueValues('type'))
        values.sort()
        self.assertEqual(values, ['dooey', 'huey', 'looey'])
        self.failIf(index.uniqueValues('carbtastic'))

    def test_hasUniqueValuesFor(self):
        index = self._makeOne()
        self.failUnless(index.hasUniqueValuesFor('type'))
        self.failIf(index.hasUniqueValuesFor('spork'))

    def test_numObjects(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        self.assertEqual(index.numObjects(), 30)

    def test_numObjects_small_maxlen(self):
        index = self._makeOne()
        index.max_length = 1
        docs = self._makeAndIndexDocs(index)
        self.assertEqual(index.numObjects(), 3)

    def test_numObjects_empty_index(self):
        index = self._makeOne()
        self.assertEqual(index.numObjects(), 0)

    def test_clear(self):
        index = self._makeOne()
        docs = self._makeAndIndexDocs(index)
        self.failUnless(index.numObjects())
        index.clear()
        self.assertEqual(index.numObjects(), 0)

    def test_role_permission_guard(self):
        index = self._makeOne(
            'test', 'type', 'date', 5, ['NerfHerder', 'Bloke'], 'View')
        viewable = self._makeViewable('NerfHerder')
        index.index_object(0, viewable)
        self.assertEqual(index.numObjects(), 1)
        notviewable = self._makeViewable()
        index.index_object(1, notviewable)
        self.assertEqual(index.numObjects(), 1)
        bloke = self._makeViewable('Bloke')
        index.index_object(2, bloke)
        self.assertEqual(index.numObjects(), 2)
        bloke.manage_permission('View', [])
        index.index_object(2, bloke)
        self.assertEqual(index.numObjects(), 1)
        dummy = self._makeViewable('Dummy')
        index.index_object(3, dummy)
        self.assertEqual(index.numObjects(), 1)
        viewable.manage_permission('View', [])
        index.index_object(0, viewable)
        self.assertEqual(index.numObjects(), 0)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RecentItemsIndexTest),
    ))
