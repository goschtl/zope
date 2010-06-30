"""
MongoDB storage tests
"""

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

