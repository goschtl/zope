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

import os
import shutil
import tempfile
import unittest

import Testing
import transaction
import Zope2
Zope2.startup()

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.QueueCatalog.CatalogEventQueue import CatalogEventQueue
from Products.QueueCatalog.CatalogEventQueue import ADDED
from Products.QueueCatalog.CatalogEventQueue import CHANGED
from Products.QueueCatalog.CatalogEventQueue import CHANGED_ADDED
from Products.QueueCatalog.CatalogEventQueue import REMOVED
from Products.QueueCatalog.CatalogEventQueue import SAFE_POLICY
from Products.QueueCatalog.CatalogEventQueue import ALTERNATIVE_POLICY
from Products.QueueCatalog.QueueCatalog import QueueCatalog
from OFS.Application import Application
from OFS.Folder import Folder
from Testing.ZopeTestCase.base import TestCase 
from ZODB.POSException import ConflictError 


class QueueConflictTests(unittest.TestCase):

    def _setAlternativePolicy(self):
        # Apply the alternative conflict resolution policy
        self.queue._conflict_policy = ALTERNATIVE_POLICY
        self.queue._p_jar.transaction_manager.commit()
        self.queue2._p_jar.sync()

        self.assertEquals(self.queue._conflict_policy, ALTERNATIVE_POLICY)
        self.assertEquals(self.queue2._conflict_policy, ALTERNATIVE_POLICY)
 

    def _insane_update(self, queue, uid, etype):
        # Queue update method that allows insane state changes, needed
        # to provoke pathological queue states
        data = queue._data
        current = data.get(uid)
        if current is not None:
            generation, current = current

            if ((current is ADDED or current is CHANGED_ADDED)
                and etype is CHANGED):
                etype = CHANGED_ADDED
        else:
            generation = 0

        data[uid] = generation+1, etype

        queue._p_changed = 1

    def openDB(self):
        from ZODB.FileStorage import FileStorage
        from ZODB.DB import DB
        self.dir = tempfile.mkdtemp()
        self.storage = FileStorage(os.path.join(self.dir, 'testQCConflicts.fs'))
        self.db = DB(self.storage)

    def setUp(self):
        self.openDB()
        queue = CatalogEventQueue()

        tm1 = transaction.TransactionManager()
        self.conn1 = self.db.open(transaction_manager=tm1)
        r1 = self.conn1.root()
        r1["queue"] = queue
        del queue
        self.queue = r1["queue"]
        tm1.commit()

        tm2 = transaction.TransactionManager()
        self.conn2 = self.db.open(transaction_manager=tm2)
        r2 = self.conn2.root()
        self.queue2 = r2["queue"]
        ignored = dir(self.queue2)    # unghostify

    def tearDown(self):
        transaction.abort()
        del self.queue
        del self.queue2
        if self.storage is not None:
            self.storage.close()
            self.storage.cleanup()
            shutil.rmtree(self.dir)

    def test_rig(self):
        # Test the test rig
        self.assertEqual(self.queue._p_serial, self.queue2._p_serial)

    def test_simpleConflict(self):
        # Using the first connection, index 10 paths
        for n in range(10):
            self.queue.update('/f%i' % n, ADDED)
        self.queue._p_jar.transaction_manager.commit()

        # After this run, the first connection's queuecatalog has 10
        # entries, the second has none.
        self.assertEqual(len(self.queue), 10)
        self.assertEqual(len(self.queue2), 0)

        # Using the second connection, index the other 10 folders
        for n in range(10):
            self.queue2.update('/g%i' % n, ADDED)

        # Now both connections' queuecatalogs have 10 entries each, but
        # for differrent objects
        self.assertEqual(len(self.queue), 10)
        self.assertEqual(len(self.queue2), 10)

        # Now we commit. Conflict resolution on the catalog queue should
        # kick in because both connections have changes. Since none of the
        # events collide, we should end up with 20 entries in our catalogs.
        self.queue2._p_jar.transaction_manager.commit()
        self.queue._p_jar.sync()
        self.queue2._p_jar.sync()
        self.assertEqual(len(self.queue), 20)
        self.assertEqual(len(self.queue2), 20)

    def test_unresolved_add_after_something(self):
        # If an  event is encountered for an object and we are trying to
        # commit an ADDED event, a conflict is encountered

        # Mutilate the logger so we don't see complaints about the 
        # conflict we are about to provoke
        from Products.QueueCatalog.QueueCatalog import logger
        logger.disabled = 1

        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self.queue2.update('/f0', ADDED)
        self.queue2.update('/f0', CHANGED)
        self.queue2._p_jar.transaction_manager.commit()

        self._insane_update(self.queue, '/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self._insane_update(self.queue2, '/f0', ADDED)
        self.assertRaises( ConflictError
                         , self.queue2._p_jar.transaction_manager.commit
                         )

        # cleanup the logger
        logger.disabled = 0

    def test_resolved_add_after_nonremoval(self):
        # If an  event is encountered for an object and we are trying to
        # commit an ADDED event while the conflict resolution policy is
        # NOT the SAFE_POLICY, we won't get a conflict.
        self._setAlternativePolicy()
        
        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self.queue2.update('/f0', ADDED)
        self.queue2.update('/f0', CHANGED)
        self.queue2._p_jar.transaction_manager.commit()

        self._insane_update(self.queue, '/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        # If we had a conflict, this would blow up
        self._insane_update(self.queue2, '/f0', ADDED)
        self.queue2._p_jar.transaction_manager.commit()

        # After the conflict has been resolved, we expect the queues to
        # containa a CHANGED_ADDED event.
        self.queue._p_jar.sync()
        self.queue2._p_jar.sync()
        self.assertEquals(len(self.queue), 1)
        self.assertEquals(len(self.queue2), 1)
        event1 = self.queue.getEvent('/f0')
        event2 = self.queue2.getEvent('/f0')
        self.failUnless(event1 == event2 == CHANGED_ADDED)

    def test_resolved_add_after_removal(self):
        # If a REMOVED event is encountered for an object and we are trying to
        # commit an ADDED event while the conflict resolution policy is
        # NOT the SAFE_POLICY, we won't get a conflict.
        self._setAlternativePolicy()
        
        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self.queue2.update('/f0', ADDED)
        self.queue2.update('/f0', CHANGED)
        self.queue2._p_jar.transaction_manager.commit()

        self.queue.update('/f0', REMOVED)
        self.queue._p_jar.transaction_manager.commit()

        # If we had a conflict, this would blow up
        self._insane_update(self.queue2, '/f0', ADDED)
        self.queue2._p_jar.transaction_manager.commit()

        # After the conflict has been resolved, we expect the queue to
        # contain a REMOVED event.
        self.queue._p_jar.sync()
        self.queue2._p_jar.sync()
        self.assertEquals(len(self.queue), 1)
        self.assertEquals(len(self.queue2), 1)
        event1 = self.queue.getEvent('/f0')
        event2 = self.queue2.getEvent('/f0')
        self.failUnless(event1 == event2 == REMOVED)

    def test_unresolved_new_old_current_all_different(self):
        # If the events we get from the current, new and old states are
        # all different, we throw in the towel in the form of a conflict.
        # This test relies on the fact that no OLD state is de-facto treated
        # as a state.

        # Mutilate the logger so we don't see complaints about the 
        # conflict we are about to provoke
        from Products.QueueCatalog.QueueCatalog import logger
        logger.disabled = 1

        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        # This commit should now raise a conflict
        self._insane_update(self.queue2, '/f0', REMOVED)
        self.assertRaises( ConflictError
                         , self.queue2._p_jar.transaction_manager.commit
                         )

        # cleanup the logger
        logger.disabled = 0

    def test_resolved_new_old_current_all_different(self):
        # If the events we get from the current, new and old states are
        # all different and the SAFE_POLICY conflict resolution policy is 
        # not enforced, the conflict resolves without bloodshed.
        # This test relies on the fact that no OLD state is de-facto treated
        # as a state.
        self._setAlternativePolicy()
 
        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        # This commit should not raise a conflict
        self._insane_update(self.queue2, '/f0', REMOVED)
        self.queue2._p_jar.transaction_manager.commit()

        # In this scenario (the incoming new state has a REMOVED event), 
        # the new state is disregarded and the old state is used. We are 
        # left with a CHANGED_ADDED event. (see queue.update method; ADDED
        # plus CHANGED results in CHANGED_ADDED)
        self.queue._p_jar.sync()
        self.queue2._p_jar.sync()
        self.assertEquals(len(self.queue), 1)
        self.assertEquals(len(self.queue2), 1)
        event1 = self.queue.getEvent('/f0')
        event2 = self.queue2.getEvent('/f0')
        self.failUnless(event1 == event2 == CHANGED_ADDED)

    def test_unresolved_new_old_current_all_different_2(self):
        # If the events we get from the current, new and old states are
        # all different, we throw in the towel in the form of a conflict.
        # This test relies on the fact that no OLD state is de-facto treated
        # as a state.

        # Mutilate the logger so we don't see complaints about the 
        # conflict we are about to provoke
        from Products.QueueCatalog.QueueCatalog import logger
        logger.disabled = 1

        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self.queue2.update('/f0', ADDED)
        self.queue2.update('/f0', CHANGED)
        self.queue2._p_jar.transaction_manager.commit()

        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        # This commit should now raise a conflict
        self._insane_update(self.queue2, '/f0', REMOVED)
        self.assertRaises( ConflictError
                         , self.queue2._p_jar.transaction_manager.commit
                         )

        # cleanup the logger
        logger.disabled = 0

    def test_resolved_new_old_current_all_different_2(self):
        # If the events we get from the current, new and old states are
        # all different and the SAFE_POLICY conflict resolution policy is 
        # not enforced, the conflict resolves without bloodshed.
        self._setAlternativePolicy()
 
        self.queue.update('/f0', ADDED)
        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        self.queue2.update('/f0', ADDED)
        self.queue2.update('/f0', CHANGED)
        self.queue2._p_jar.transaction_manager.commit()

        self.queue.update('/f0', CHANGED)
        self.queue._p_jar.transaction_manager.commit()

        # This commit should not raise a conflict
        self._insane_update(self.queue2, '/f0', REMOVED)
        self.queue2._p_jar.transaction_manager.commit()

        # In this scenario (the incoming new state has a REMOVED event), 
        # we will take the new state to resolve the conflict, because its
        # generation number is higher then the oldstate and current state.
        self.queue._p_jar.sync()
        self.queue2._p_jar.sync()
        self.assertEquals(len(self.queue), 1)
        self.assertEquals(len(self.queue2), 1)
        event1 = self.queue.getEvent('/f0')
        event2 = self.queue2.getEvent('/f0')
        self.failUnless(event1 == event2 == REMOVED)


def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(QueueConflictTests),
                    ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

