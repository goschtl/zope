"""
MongoDB storage tests
"""

from cjson import encode as json_encode
from cjson import decode as json_decode

import unittest2

from zope.interface.verify import verifyClass

from zopyx.versioning import errors
from zopyx.versioning.storages.mongodb.storage import MongoDBStorage
from zopyx.versioning.interfaces import IVersionStorage

class StorageTests(unittest2.TestCase):

    def setUp(self):
        self.storage = MongoDBStorage('localhost', 10200, 'test-db')
        self.storage.clear()

    def testInterface(self):
        verifyClass(IVersionStorage, MongoDBStorage)

    def testRetrievalNonExistingDocuments(self):
        with self.assertRaises(errors.NoDocumentFound):
            self.storage.retrieve('42', 42)

    def testStore(self):
        version_data = {'text' : u'hello world', 'subject' : [u'kw1', u'kw2']}
        for i in range(5):
            self.storage.store('42', json_encode(version_data), 'ajung')
        revisions = self.storage.list_revisions('42')
        self.assertEqual(revisions, [0,1,2,3,4])

    def testListRevisionsNonExistingID(self):
        with self.assertRaises(errors.NoDocumentFound):
            revisions = self.storage.list_revisions('do.such.document')

