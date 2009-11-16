##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
from zope.testing import doctest
import unittest
import zc.bsddbstorage
import ZODB.tests.BasicStorage
import ZODB.tests.ConflictResolution
import ZODB.tests.HistoryStorage
import ZODB.tests.IteratorStorage
import ZODB.tests.IteratorStorage
import ZODB.tests.MTStorage
import ZODB.tests.PackableStorage
import ZODB.tests.PersistentStorage
import ZODB.tests.ReadOnlyStorage
import ZODB.tests.RevisionStorage
import ZODB.tests.StorageTestBase
import ZODB.tests.Synchronization
import ZODB.tests.testblob

class BSDDBStorageTests(
    ZODB.tests.StorageTestBase.StorageTestBase,
    ZODB.tests.BasicStorage.BasicStorage,
    ZODB.tests.RevisionStorage.RevisionStorage,
    ZODB.tests.PackableStorage.PackableStorageWithOptionalGC,
    ZODB.tests.Synchronization.SynchronizedStorage,
    ZODB.tests.ConflictResolution.ConflictResolvingStorage,
    ZODB.tests.HistoryStorage.HistoryStorage,
    ZODB.tests.IteratorStorage.IteratorStorage,
    ZODB.tests.IteratorStorage.ExtendedIteratorStorage,
    ZODB.tests.PersistentStorage.PersistentStorage,
    ZODB.tests.MTStorage.MTStorage,
    ZODB.tests.ReadOnlyStorage.ReadOnlyStorage
    ):

    def open(self, **kwargs):
        self._storage = zc.bsddbstorage.BSDDBStorage(
            'storage', **kwargs)

    def setUp(self):
        StorageTestBase.StorageTestBase.setUp(self)
        self.open(create=1)

def test_suite():
    suite = unittest.TestSuite()
    for klass in [
        BSDDBStorageTests,
        ]:
        suite.addTest(unittest.makeSuite(klass, "check"))
    suite.addTest(ZODB.tests.testblob.storage_reusable_suite(
        'BlobBSDDBStorage',
        lambda name, blob_dir:
        zc.bsddbstorage.BSDDBStorage(name, blob_dir=blob_dir),
        test_blob_storage_recovery=True,
        test_packing=True,
        ))
    suite.addTest(ZODB.tests.PackableStorage.IExternalGC_suite(
        lambda : zc.bsddbstorage.BSDDBStorage(
            'data', blob_dir='blobs')))
    return suite
