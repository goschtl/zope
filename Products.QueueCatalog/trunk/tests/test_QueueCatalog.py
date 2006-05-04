##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""QueueCatalog tests.

$Id$
"""

import os
import shutil
import tempfile
import unittest

import Testing
import transaction
import Zope2
Zope2.startup()

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.QueueCatalog.QueueCatalog import QueueCatalog
from OFS.Application import Application
from OFS.Folder import Folder
from Testing.ZopeTestCase.base import TestCase 
from ZODB.POSException import ConflictError 

class QueueCatalogTests(TestCase):

    def afterSetUp(self):
        self.app.real_cat = ZCatalog('real_cat')
        self.app.real_cat.addIndex('id', 'FieldIndex')
        self.app.real_cat.addIndex('title', 'FieldIndex')
        self.app.real_cat.addIndex('meta_type', 'FieldIndex')
        self.app.queue_cat = QueueCatalog(3) # 3 buckets
        self.app.queue_cat.id = 'queue_cat'
        self.app.queue_cat.manage_edit(location='/real_cat',
                                  immediate_indexes=['id', 'title'])

    def testAddObject(self):
        app = self.app
        app.f1 = Folder()
        app.f1.id = 'f1'
        self.assertEqual(app.queue_cat.manage_size(), 0)
        self.assertEqual(len(app.real_cat), 0)
        app.queue_cat.catalog_object(app.f1)
        self.assertEqual(app.queue_cat.manage_size(), 1)
        self.assertEqual(len(app.real_cat), 1)

    def testDeferMostIndexes(self):
        app = self.app
        app.f1 = Folder()
        app.f1.id = 'f1'
        app.queue_cat.catalog_object(app.f1)
        # The 'id' index gets updated immediately.
        res = app.queue_cat.searchResults(id='f1')
        self.assertEqual(len(res), 1)
        # In this test, the 'meta_type' index gets updated later.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 0)
        # Process the queue.
        app.queue_cat.process()
        # Now that the queue has been processed, the item shows up.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 1)

    def testPinpointIndexes(self):
        app = self.app
        app.queue_cat.setImmediateMetadataUpdate(True)
        app.queue_cat.setProcessAllIndexes(False)
        app.f1 = Folder()
        app.f1.id = 'f1'
        app.f1.title = 'Joe'
        app.queue_cat.catalog_object(app.f1, idxs=['id'])
        # The 'id' index gets updated immediately.
        res = app.queue_cat.searchResults(id='f1')
        self.assertEqual(len(res), 1)
        res = app.queue_cat.searchResults(title='Joe')
        self.assertEqual(len(res), 1)
        # even though we requested that only 'id' and title be updated, 
        # because this is a new entry, it should still be in the queue.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 0)
        app.queue_cat.process()
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 1)
        # Now we will change both the title and the meta_type but only ask the
        # title to be indexed
        app.f1.meta_type = 'Duck'
        app.f1.title = 'Betty'
        app.queue_cat.catalog_object(app.f1, idxs=['title'])
        res = app.queue_cat.searchResults(title='Joe')
        self.assertEqual(len(res), 0)
        res = app.queue_cat.searchResults(title='Betty')
        self.assertEqual(len(res), 1)
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 1)
        app.queue_cat.process()
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 1)
        res = app.queue_cat.searchResults(meta_type='Duck')
        self.assertEqual(len(res), 0)
        # now we will change the title again but only ask that the meta_type
        # be indexed.  All deferred indexes will index, but not title
        app.f1.title = 'Susan'
        app.queue_cat.catalog_object(app.f1, idxs=['meta_type'])
        res = app.queue_cat.searchResults(title='Betty')
        self.assertEqual(len(res), 1) # no change
        res = app.queue_cat.searchResults(meta_type='Duck')
        self.assertEqual(len(res), 0) # no change
        app.queue_cat.process()
        res = app.queue_cat.searchResults(meta_type='Duck')
        self.assertEqual(len(res), 1) # change!

    def testIndexOnce(self):
        # this behavior is important to reduce conflict errors.
        app = self.app
        app.queue_cat.setImmediateMetadataUpdate(True)
        app.queue_cat.setProcessAllIndexes(False)
        app.f1 = Folder()
        app.f1.id = 'f1'
        app.f1.title = 'Joe'
        app.queue_cat.catalog_object(app.f1)
        res = app.queue_cat.searchResults(title='Joe')
        self.assertEqual(len(res), 1)
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 0)
        app.f1.title = 'Missed me'
        app.queue_cat.process()
        res = app.queue_cat.searchResults(title='Joe')
        self.assertEqual(len(res), 1) # already indexed
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 1)

    def testMetadataOnce(self):
        # this behavior is important to reduce conflict errors.
        app = self.app
        app.queue_cat.setImmediateMetadataUpdate(True)
        app.queue_cat.setProcessAllIndexes(False)
        app.real_cat.addColumn('title')
        app.f1 = Folder()
        app.f1.id = 'f1'
        app.f1.title = 'Joe'
        app.queue_cat.catalog_object(app.f1) # metadata should change
        res = app.queue_cat.searchResults(id='f1')[0]
        self.assertEqual(res.title, 'Joe')
        app.f1.title = 'Betty'
        app.queue_cat.process() # metadata should not change
        res = app.queue_cat.searchResults(id='f1')[0]
        self.assertEqual(res.title, 'Joe')
        # now we'll change the policy
        app.queue_cat.setImmediateMetadataUpdate(False)
        app.queue_cat.catalog_object(app.f1) # metadata should not change
        res = app.queue_cat.searchResults(id='f1')[0]
        self.assertEqual(res.title, 'Joe')
        app.queue_cat.process() # metadata should change
        res = app.queue_cat.searchResults(id='f1')[0]
        self.assertEqual(res.title, 'Betty')

    #def testLogCatalogErrors(self):
    #    app = self.app
    #    app.f1 = Folder()
    #    app.f1.id = 'f1'
    #    app.queue_cat.catalog_object(app.f1)
    #    app.real_cat.catalog_object = lambda : None # raises TypeError
    #    app.queue_cat.process()
    #    del app.real_cat.catalog_object
    #    app.queue_cat.setImmediateRemoval(False)
    #    app.queue_cat.uncatalog_object(app.queue_cat.uidForObject(app.f1))
    #    app.real_cat.uncatalog_object = lambda : None # raises TypeError
    #    app.queue_cat.process()
    #    del app.real_cat.uncatalog_object
    #    f = self.getLogFile()
    #    self.verifyEntry(f, subsys="QueueCatalog",
    #                     summary="error cataloging object")
    #    # the verify method in the log tests is broken :-(
    #    l = f.readline()
    #    marker = "------\n"
    #    while l != marker:
    #        l = f.readline()
    #        if not l:
    #            self.fail('could not find next log entry')
    #    f.seek(f.tell() - len(marker))
    #    self.verifyEntry(f, subsys="QueueCatalog",
    #                     summary="error uncataloging object")

    def testQueueProcessingLimit(self):
        # Don't try to process too many items at once.
        app = self.app
        for n in range(100):
            f = Folder()
            f.id = 'f%d' % n
            setattr(app, f.id, f)
            f = getattr(app, f.id)
            app.queue_cat.catalog_object(f)
        # None of the items should be in the meta_type index yet.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 0)
        # Process only 10 of the items.
        app.queue_cat.process(max=10)
        # There should now be 10 items in the results.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 10)
        # Process another 25.
        app.queue_cat.process(max=25)
        # There should now be 35 items in the results.
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 35)
        # Finish.
        app.queue_cat.process()
        res = app.queue_cat.searchResults(meta_type='Folder')
        self.assertEqual(len(res), 100)


    def testGetIndexInfo(self):
        info = self.app.queue_cat.getIndexInfo()
        self.assertEqual(len(info), 3)
        self.assert_({'id': 'id', 'meta_type': 'FieldIndex'} in info)
        self.assert_({'id': 'meta_type', 'meta_type': 'FieldIndex'} in info)
        self.assert_({'id': 'title', 'meta_type': 'FieldIndex'} in info)
        
    
    def testRealCatSpecifiesUids(self):
        def stupidUidMaker(self, obj):
            return '/stupid/uid'
        ZCatalog.uidForObject = stupidUidMaker # monkey patch
        self.assertEqual(self.app.queue_cat.uidForObject(None), '/stupid/uid')

    def testImmediateDeletion(self):
        app = self.app
        app.test_cat = QueueCatalog(1000)  # 1000 buckets. I don't want collisions here.
        app.test_cat.id = 'test_cat'
        app.test_cat.manage_edit(location='/real_cat',
                                  immediate_indexes=['id'], immediate_removal=1)
        for n in range(20):
            f = Folder()
            f.id = 'f%d' % n
            setattr(app, f.id, f)
            f = getattr(app, f.id)
            app.test_cat.catalog_object(f)
        self.assertEqual(app.test_cat.manage_size(), 20)
        # "Delete" one. This should be processed immediately (including the add-event)
        app.test_cat.uncatalog_object(getattr(app, 'f1').getPhysicalPath())
        self.assertEqual(app.test_cat.manage_size(), 19)
        del app.test_cat


class QueueConflictTests(unittest.TestCase):

    def openDB(self):
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        self.dir = tempfile.mkdtemp()
        self.storage = FileStorage(os.path.join(self.dir, 'testQCConflicts.fs'))
        self.db = DB(self.storage)

    def setUp(self):
        self.openDB()
        app = Application()

        tm1 = transaction.TransactionManager()
        conn1 = self.db.open(transaction_manager=tm1)
        r1 = conn1.root()
        r1["Application"] = app
        del app
        self.app = r1["Application"]
        tm1.commit()

        self.app.real_cat = ZCatalog('real_cat')
        self.app.real_cat.addIndex('id', 'FieldIndex')
        self.app.real_cat.addIndex('title', 'FieldIndex')
        self.app.real_cat.addIndex('meta_type', 'FieldIndex')
        self.app.queue_cat = QueueCatalog(3) # 3 buckets
        self.app.queue_cat.id = 'queue_cat'
        self.app.queue_cat.manage_edit(location='/real_cat',
                                  immediate_indexes=[])

        # Create stuff to catalog
        for n in range(10):
            f = Folder()
            f.id = 'f%d' % n
            self.app._setOb(f.id, f)
            g = Folder()
            g.id = 'g%d' % n
            self.app._setOb(g.id, g)

        # Make sure everything is committed so the second connection sees it
        tm1.commit()

        tm2 = transaction.TransactionManager()
        conn2 = self.db.open(transaction_manager=tm2)
        r2 = conn2.root()
        self.app2 = r2["Application"]
        ignored = dir(self.app2)    # unghostify

    def tearDown(self):
        transaction.abort()
        del self.app
        if self.storage is not None:
            self.storage.close()
            self.storage.cleanup()
            shutil.rmtree(self.dir)

    def test_rig(self):
        # Test the test rig
        self.assertEqual(self.app._p_serial, self.app2._p_serial)

    def test_simpleConflict(self):
        # Using the first connection, index 10 folders
        for n in range(10):
            f = getattr(self.app, 'f%d' % n) 
            self.app.queue_cat.catalog_object(f)
        self.app._p_jar.transaction_manager.commit()

        # After this run, the first connection's queuecatalog has 10
        # entries, the second has none.
        self.assertEqual(self.app.queue_cat.manage_size(), 10)
        self.assertEqual(self.app2.queue_cat.manage_size(), 0)

        # Using the second connection, index the other 10 folders
        for n in range(10):
            g = getattr(self.app2, 'g%d' % n) 
            self.app2.queue_cat.catalog_object(g)

        # Now both connections' queuecatalogs have 10 entries each, but
        # for differrent objects
        self.assertEqual(self.app.queue_cat.manage_size(), 10)
        self.assertEqual(self.app2.queue_cat.manage_size(), 10)

        # Now we commit. Conflict resolution on the catalog queue should
        # kick in because both connections have changes. Since none of the
        # events collide, we should end up with 20 entries in our catalogs.
        self.app2._p_jar.transaction_manager.commit()
        self.app._p_jar.sync()
        self.app2._p_jar.sync()
        self.assertEqual(self.app.queue_cat.manage_size(), 20)
        self.assertEqual(self.app2.queue_cat.manage_size(), 20)

    def test_unresolved_add_after_delete(self):
        # If a DELETE event is encountered for an object and other events
        # happen afterwards, we have entered the twilight zone and give up.

        # Taking one item and cataloging it in the first connection, then
        # uncataloging it. There should be 1 event in the queue left
        # afterwards, for uncataloging the content item (DELETE)
        f0 = getattr(self.app, 'f0')
        self.app.queue_cat.catalog_object(f0)
        self.app._p_jar.transaction_manager.commit()
        self.app.queue_cat.uncatalog_object('/f0')
        self.app._p_jar.transaction_manager.commit()
        self.assertEqual(self.app.queue_cat.manage_size(), 1)

        # In the second connection, I will newly catalog the same folder again
        # in order to provoke insane state (ADD after DELETE)
        self.app2.queue_cat.catalog_object(f0)

        # This commit should now raise a conflict
        self.assertRaises( ConflictError
                         , self.app2._p_jar.transaction_manager.commit
                         )


def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(QueueCatalogTests),
            unittest.makeSuite(QueueConflictTests),
                    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

