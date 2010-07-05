################################################################
# zopyx.versioning
# (C) 2010, ZOPYX Ltd, D-72070 Tuebingen
# Published under the Zope Public License 2.1
################################################################

"""
MongoDB storage tests
"""

import unittest2
import anyjson

from zope.interface.verify import verifyClass

from zopyx.versioning import errors
from zopyx.versioning.storages.mongodb.storage import MongoDBStorage
from zopyx.versioning.interfaces import IVersionStorage

class StorageTests(unittest2.TestCase):

    def setUp(self):
        self.storage = MongoDBStorage('localhost', 10200, 'test-db')
        self.storage.clear()

    def testClear(self):
        self.assertEqual(self.storage.metadata.find().count(), 0)
        self.assertEqual(self.storage.revisions.find().count(), 0)
        self.assertEqual(self.storage.collections.find().count(), 0)

    def testInterface(self):
        verifyClass(IVersionStorage, MongoDBStorage)

    def testRetrievalNonExistingDocuments(self):
        with self.assertRaises(errors.NoDocumentFound):
            self.storage.retrieve('42', 42)

    def testStore(self):
        version_data = {'text' : u'hello world', 'subject' : [u'kw1', u'kw2']}
        for i in range(5):
            self.storage.store('42', anyjson.serialize(version_data), anyjson.serialize({}))
        revisions = self.storage.list_revisions('42')
        self.assertEqual(revisions, [0,1,2,3,4])

    def testListRevisionsNonExistingID(self):
        with self.assertRaises(errors.NoDocumentFound):
            revisions = self.storage.list_revisions('do.such.document')

    def testRemoveNonExistingDocument(self):
        with self.assertRaises(errors.NoDocumentFound):
            self.storage.remove('do.such.document')

    def testRemoveExistingDocument(self):
        version_data = {'text' : u'hello world', 'subject' : [u'kw1', u'kw2']}
        self.storage.store('42', anyjson.serialize(version_data), anyjson.serialize({}))
        self.storage.remove('42')
        with self.assertRaises(errors.NoDocumentFound):
            self.storage.remove('42')

    def testStoreCollection(self):

        # two objects first
        no_data = anyjson.serialize({})
        rev1 = self.storage.store('child1', no_data, no_data)
        rev2 = self.storage.store('child2', no_data, no_data)
        rev3 = self.storage.store('child3', no_data, no_data)

        self.assertEqual(self.storage.revisions.find().count(), 3)

        version_data = {'text' : u'hello world', 'subject' : [u'kw1', u'kw2']}
        self.storage.store('folder',
                           anyjson.serialize(version_data),
                           anyjson.serialize({}),
                           [dict(_oid='child1', _rev=rev1),
                            dict(_old='child2', _rev=rev2),
                            dict(_old='child3', _rev=rev3),
                           ]) 
        self.assertEqual(self.storage.collections.find().count(), 1)

        self.storage.remove('folder')
        self.assertEqual(self.storage.collections.find().count(), 0)
