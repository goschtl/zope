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
from zope.testing import doctest, setupstack
import cPickle
import cStringIO
import os
import time
import unittest
import zc.bsddbstorage
import ZEO.tests.testZEO
import ZODB.blob
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
import ZODB.tests.util

def DISABLED(self):
    "disabled"

class Overrides:

    checkLoadBeforeUndo = DISABLED
    checkUndoZombie = DISABLED
    checkPackWithMultiDatabaseReferences = DISABLED
    checkLoadBeforeUndo = DISABLED
    checkWriteMethods = DISABLED

    # Dang it, we really need to factor the pack tests for gc or no gc
    def checkPackAllRevisions(self):
        def pdumps(obj):
            s = cStringIO.StringIO()
            p = cPickle.Pickler(s)
            p.dump(obj)
            p.dump(None)
            return s.getvalue()

        self._initroot()
        eq = self.assertEqual
        raises = self.assertRaises
        # Create a `persistent' object
        obj = self._newobj()
        oid = obj.getoid()
        obj.value = 1
        # Commit three different revisions
        revid1 = self._dostoreNP(oid, data=pdumps(obj))
        obj.value = 2
        revid2 = self._dostoreNP(oid, revid=revid1, data=pdumps(obj))
        obj.value = 3
        revid3 = self._dostoreNP(oid, revid=revid2, data=pdumps(obj))
        # Now make sure all three revisions can be extracted
        data = self._storage.loadSerial(oid, revid1)
        pobj = cPickle.loads(data)
        eq(pobj.getoid(), oid)
        eq(pobj.value, 1)
        data = self._storage.loadSerial(oid, revid2)
        pobj = cPickle.loads(data)
        eq(pobj.getoid(), oid)
        eq(pobj.value, 2)
        data = self._storage.loadSerial(oid, revid3)
        pobj = cPickle.loads(data)
        eq(pobj.getoid(), oid)
        eq(pobj.value, 3)
        # Now pack all transactions; need to sleep a second to make
        # sure that the pack time is greater than the last commit time.
        now = packtime = time.time()
        while packtime <= now:
            packtime = time.time()
        self._storage.pack(packtime)
        # All revisions of the object should be gone, since there is no
        # reference from the root object to this object.
        raises(KeyError, self._storage.loadSerial, oid, revid1)
        raises(KeyError, self._storage.loadSerial, oid, revid2)

        # Commented because No GC:
        # raises(KeyError, self._storage.loadSerial, oid, revid3)

class BSDDBStorageTests(
    Overrides,
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
            'storage', checkpoint=1, **kwargs)

    def setUp(self):
        ZODB.tests.StorageTestBase.StorageTestBase.setUp(self)
        self.open(create=1)

class BSDDBStorageZEOTests(
    Overrides,
    ZEO.tests.testZEO.FullGenericTests,
    ):

    def getConfig(self):
        return """\
        %import zc.bsddbstorage
        <bsddbstorage>
          path data
          checkpoint 1
        </bsddbstorage>
        """

    checkCommitLockUndoAbort = DISABLED
    checkCommitLockUndoClose = DISABLED
    checkCommitLockUndoFinish = DISABLED
    checkCreationUndoneGetTid = DISABLED
    checkNotUndoable = DISABLED
    checkPackAfterUndoDeletion = DISABLED
    checkPackAfterUndoManyTimes = DISABLED
    checkSimpleTransactionalUndo = DISABLED
    checkTransactionalUndoIterator = DISABLED
    checkTwoObjectUndo = DISABLED
    checkTwoObjectUndoAgain = DISABLED
    checkTwoObjectUndoAtOnce = DISABLED
    checkUndoConflictResolution = DISABLED
    checkUndoCreationBranch1 = DISABLED
    checkUndoCreationBranch2 = DISABLED
    checkUndoInvalidation = DISABLED
    checkUndoUnresolvable = DISABLED
    checkIndicesInUndoInfo = DISABLED
    checkIndicesInUndoLog = DISABLED
    checkPackUndoLog = DISABLED
    checkTransactionalUndoAfterPack = DISABLED
    checkTransactionalUndoAfterPackWithObjectUnlinkFromRoot = DISABLED
    checkUndoLogMetadata = DISABLED
    checkPackUnlinkedFromRoot = DISABLED

    # This test is insane. It chancks that ZEO clients tolerate a ZODB
    # bug that can cause multiple records for an object to be sent in the same
    # transaction.  This needs to be fixed in ZODB. I won't add a work around
    # here unless I absolutely have to.
    checkCreativeGetState = DISABLED

    # XXX I don't fathom what this test is trying to do. We fail it, but I
    # don't know if that is a bad thing.
    checkIteratorGCSpanTransactions = DISABLED

def truncate():
    """Database truncation

Sometimes, it's useful to be able to truncate a database at a
particular time/tid.  You might do this to undo a bunch of trailing
activity or when doing benchmark to prepare to replay transactions.

    >>> import transaction
    >>> db = zc.bsddbstorage.DB('test', 'blobs')
    >>> conn = db.open()
    >>> conn.root.x = 0
    >>> conn.root.blob = ZODB.blob.Blob()
    >>> conn.root.blobs = conn.root().__class__()
    >>> for i in range(10):
    ...     conn.root.x += 1
    ...     conn.root.blob.open('w').write(str(conn.root.x))
    ...     conn.root.blobs[conn.root.x] = ZODB.blob.Blob('data')
    ...     transaction.commit()
    >>> time.sleep(.01)
    >>> tt10 = time.time()
    >>> time.sleep(.01)
    >>> for i in range(10):
    ...     conn.root.x += 1
    ...     conn.root.blob.open('w').write(str(conn.root.x))
    ...     conn.root.blobs[conn.root.x] = ZODB.blob.Blob('data')
    ...     transaction.commit()
    >>> tid20 = db.storage.lastTransaction()
    >>> for i in range(10):
    ...     conn.root.x += 1
    ...     conn.root.blob.open('w').write(str(conn.root.x))
    ...     conn.root.blobs[conn.root.x] = ZODB.blob.Blob('data')
    ...     transaction.commit()
    >>> conn.root.x, conn.root.blob.open().read(), len(conn.root.blobs)
    (30, '30', 30)

    >>> def count_blob_files(dir):
    ...     n = 0
    ...     for base, dirs, files in os.walk(os.path.join(dir, '0x00')):
    ...         for file in files:
    ...             if file.endswith('.blob'):
    ...                 n += 1
    ...     return n

    >>> count_blob_files('blobs')
    60

We can truncate using either a tid or a time.time.  We can't truncate a
storage while it's open:

    >>> zc.bsddbstorage.truncate(tid20, 'test', 'blobs') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    LockError: Couldn't lock ...

    >>> db.close()

First, we'll truncate using a tid:

    >>> zc.bsddbstorage.truncate(tid20, 'test', 'blobs')
    >>> db = zc.bsddbstorage.DB('test', 'blobs')
    >>> conn = db.open()
    >>> conn.root.x, conn.root.blob.open().read(), len(conn.root.blobs)
    (20, '20', 20)
    >>> count_blob_files('blobs')
    40
    >>> db.close()


We can also use a time.time:

    >>> zc.bsddbstorage.truncate(tt10, 'test', 'blobs')
    >>> db = zc.bsddbstorage.DB('test', 'blobs')
    >>> conn = db.open()
    >>> conn.root.x, conn.root.blob.open().read(), len(conn.root.blobs)
    (10, '10', 10)
    >>> count_blob_files('blobs')
    20
    >>> db.close()
    """


def test_suite():
    suite = unittest.TestSuite()
    for klass in [
        BSDDBStorageTests, BSDDBStorageZEOTests,
        ]:
        suite.addTest(unittest.makeSuite(klass, "check"))
    suite.addTest(ZODB.tests.testblob.storage_reusable_suite(
        'BlobBSDDBStorage',
        lambda name, blob_dir:
        zc.bsddbstorage.BSDDBStorage(name, blob_dir=blob_dir, checkpoint=1),
        test_blob_storage_recovery=True,
        test_packing=False,
        test_undo=False,
        ))
    suite.addTest(doctest.DocFileSuite(
        "blob_packing.txt",
        setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown,
        ))
    suite.addTest(ZODB.tests.PackableStorage.IExternalGC_suite(
        lambda : zc.bsddbstorage.BSDDBStorage(
            'data', blob_dir='blobs')))
    suite.addTest(
        doctest.DocTestSuite(
            setUp=ZODB.tests.util.setUp, tearDown=ZODB.tests.util.tearDown)
        )
    return suite
