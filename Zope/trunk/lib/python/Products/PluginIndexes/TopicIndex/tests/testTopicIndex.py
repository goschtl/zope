##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################


import Zope
import os,sys,re,unittest
from Products.PluginIndexes.TopicIndex.TopicIndex import TopicIndex
from Products.ZCatalog.ZCatalog import ZCatalog


class Obj:
    
    def __init__(self,id,meta_type=''):
        self.id        = id
        self.meta_type = meta_type
    
    def getId(self): return self.id 
    def getPhysicalPath(self):  return self.id



class TestBase(unittest.TestCase):

    def _searchAnd(self,query,expected):
        return self._search(query,'and',expected)

    def _searchOr(self,query,expected):
        return self._search(query,'or',expected)


    def _search(self,query,operator,expected):

        res = self.TI._apply_index({'topic':{'query':query,'operator':operator}})
        rows = list(res[0])
        rows.sort()
        expected.sort()

        self.assertEqual(rows,expected,query)

        return rows
        

class TestTopicIndex(TestBase):

    def setUp(self):
        self.TI = TopicIndex("topic")
        self.TI.addFilteredSet("doc1","PythonFilteredSet","o.meta_type=='doc1'")
        self.TI.addFilteredSet("doc2","PythonFilteredSet","o.meta_type=='doc2'")
        
        self.TI.index_object(0 , Obj('0',))
        self.TI.index_object(1 , Obj('1','doc1'))
        self.TI.index_object(2 , Obj('2','doc1'))
        self.TI.index_object(3 , Obj('3','doc2'))
        self.TI.index_object(4 , Obj('4','doc2'))
        self.TI.index_object(5 , Obj('5','doc3'))
        self.TI.index_object(6 , Obj('6','doc3'))


    def testOr(self):
        """ test 1 """

        self._searchOr('doc1',[1,2])
        self._searchOr(['doc1'],[1,2])
        self._searchOr('doc2',[3,4]),
        self._searchOr(['doc2'],[3,4])
        self._searchOr(['doc1','doc2'], [1,2,3,4])


    def testAnd(self):
        """ test 1 """

        self._searchAnd('doc1',[1,2])
        self._searchAnd(['doc1'],[1,2])
        self._searchAnd('doc2',[3,4])
        self._searchAnd(['doc2'],[3,4])
        self._searchAnd(['doc1','doc2'],[])


class ZCatalogTopicTests(TestBase):


    def setUp(self):
        
        self.cat = ZCatalog('catalog')
        self.cat.addColumn('id')
        self.cat.addIndex('topic','TopicIndex')
        self.TI = self.cat._catalog.indexes['topic']

        self.TI.addFilteredSet("doc1","PythonFilteredSet","o.meta_type=='doc1'")
        self.TI.addFilteredSet("doc2","PythonFilteredSet","o.meta_type=='doc2'")
        
        self.cat.catalog_object(Obj('0'))
        self.cat.catalog_object(Obj('1','doc1'))
        self.cat.catalog_object(Obj('2','doc1'))
        self.cat.catalog_object(Obj('3','doc2'))
        self.cat.catalog_object(Obj('4','doc2'))
        self.cat.catalog_object(Obj('5','doc3'))
        self.cat.catalog_object(Obj('6','doc3'))


    def testOr(self):
        """ testing or (catalog)"""
        self._searchOr('doc1',[1,2])
        self._searchOr('doc2',[3,4])
        self._searchOr(['doc1','doc2'],[1,2,3,4])


    def testAnd(self):
        """ testing And (catalog)"""
        self._searchAnd('doc1',[1,2])
        self._searchAnd('doc2',[3,4])
        self._searchAnd(['doc1','doc2'],[])


    def _search(self,query,operator,expected):

        res = self.cat.searchResults({'topic':{'query':query,'operator':operator}})
        
        rows = [int(x.id)  for x in res ]
        rows.sort()
        expected.sort()

        self.assertEqual(rows,expected,query)

        return rows,res


def test_suite():

    return unittest.TestSuite( (
        unittest.makeSuite(TestTopicIndex),
        unittest.makeSuite(ZCatalogTopicTests),
        ))


def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
    
