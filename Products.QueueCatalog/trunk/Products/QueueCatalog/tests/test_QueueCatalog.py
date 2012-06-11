##############################################################################
#
# Copyright (c) 2002-2006 Zope Foundation and Contributors.
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
"""QueueCatalog tests.

$Id$
"""

import logging
import unittest
import cStringIO

import Testing
import Zope2
Zope2.startup()

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.QueueCatalog.QueueCatalog import QueueCatalog
from OFS.Folder import Folder
from Testing.ZopeTestCase.base import TestCase 

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

    def testLogCatalogErrors(self):
        # Mutilate the logger so we can capture output silently
        from Products.QueueCatalog.QueueCatalog import logger
        logger.propagate = 0
        fake_file = cStringIO.StringIO()
        fake_log_handler = logging.StreamHandler(fake_file)
        logger.addHandler(fake_log_handler)

        # Now do our bidding
        app = self.app
        app.f1 = Folder()
        app.f1.id = 'f1'
        app.queue_cat.catalog_object(app.f1)
        app.real_cat.catalog_object = lambda : None # raises TypeError
        app.queue_cat.process()
        del app.real_cat.catalog_object

        # See what the fake file contains, and then rewind for reuse
        output = fake_file.getvalue()
        self.failUnless(output.startswith('error cataloging object'))
        fake_file.seek(0)
        
        app.queue_cat.setImmediateRemoval(False)
        app.queue_cat.uncatalog_object(app.queue_cat.uidForObject(app.f1))
        app.real_cat.uncatalog_object = lambda : None # raises TypeError
        app.queue_cat.process()
        del app.real_cat.uncatalog_object

        # See what the fake file contains, and then rewind for reuse
        output = fake_file.getvalue()
        self.failUnless(output.startswith('error uncataloging object'))
        fake_file.close()

        # cleanup the logger
        fake_log_handler.close()
        logger.removeHandler(fake_log_handler)
        logger.propagate = 1

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
        app.test_cat = QueueCatalog(1000)  # 1000 buckets to prevent collisions
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
        # "Delete" one. This should be processed immediately (including 
        # the add-event)
        app.test_cat.uncatalog_object(getattr(app, 'f1').getPhysicalPath())
        self.assertEqual(app.test_cat.manage_size(), 19)
        del app.test_cat


def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(QueueCatalogTests),
                    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

