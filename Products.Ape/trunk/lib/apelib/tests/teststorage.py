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
"""Storage tests (with data stored in simple mappings)

$Id$
"""

import unittest
from thread import start_new_thread, allocate_lock

from transaction import get as get_transaction
import ZODB
from Persistence import Persistent, PersistentMapping

from apelib.zodb3.db import ApeDB
from apelib.zodb3.storage import ApeStorage
from apelib.zodb3.resource import StaticResource
from apelib.zodb3.utils import zodb_copy
from apelib.core.interfaces import OIDConflictError
from serialtestbase import SerialTestBase, TestObject


def run_in_thread(f):
    """Calls a function in another thread and waits for it to finish."""
    lock = allocate_lock()
    def run(f=f, lock=lock):
        try:
            f()
        finally:
            lock.release()
    lock.acquire()
    start_new_thread(run, ())
    lock.acquire()
    lock.release()


class ApeStorageTests (SerialTestBase, unittest.TestCase):
    # Tests of ApeStorage and ApeConnection.

    def setUp(self):
        SerialTestBase.setUp(self)
        resource = StaticResource(self.conf)
        storage = ApeStorage(resource, self.conns)
        self.storage = storage
        db = ApeDB(storage, resource)
        self.db = db

    def tearDown(self):
        get_transaction().abort()
        self.db.close()
        SerialTestBase.tearDown(self)

    def test_store_and_load(self):
        ob = TestObject()
        ob.strdata = '345'
        ob['a'] = 'b'
        ob['c'] = 'd'

        conn1 = self.db.open()
        conn2 = None
        conn3 = None
        try:

            # Load the root and create a new object
            root = conn1.root()
            get_transaction().begin()
            root['TestRoot'] = ob
            get_transaction().commit()
            ob1 = conn1.root()['TestRoot']
            self.assertEqual(ob1.strdata, ob.strdata)
            self.assertEqual(ob1.items(), ob.items())

            # Verify a new object was stored and make a change
            get_transaction().begin()
            conn2 = self.db.open()
            ob2 = conn2.root()['TestRoot']
            self.assertEqual(ob2.strdata, ob.strdata)
            self.assertEqual(ob2.items(), ob.items())
            ob2.strdata = '678'
            get_transaction().commit()

            # Verify the change was stored and make another change
            conn3 = self.db.open()
            ob3 = conn3.root()['TestRoot']
            self.assertEqual(ob3.strdata, '678')
            self.assertEqual(ob3.items(), ob.items())
            ob3.strdata = '901'
            get_transaction().commit()
            conn3.close()
            conn3 = None
            conn3 = self.db.open()
            ob3 = conn3.root()['TestRoot']
            self.assertEqual(ob3.strdata, '901')

            # Verify we didn't accidentally change the original object
            self.assertEqual(ob.strdata, '345')

        finally:
            conn1.close()
            if conn2 is not None:
                conn2.close()
            if conn3 is not None:
                conn3.close()


    def test_unmanaged(self):
        ob = TestObject()
        ob['a'] = 'b'
        ob.stowaway = PersistentMapping()
        ob.stowaway['c'] = 'd'

        conn1 = self.db.open()
        conn2 = None
        conn3 = None
        try:

            # Load the root and create a new object
            root = conn1.root()
            get_transaction().begin()
            root['TestRoot2'] = ob
            get_transaction().commit()
            ob1 = conn1.root()['TestRoot2']
            self.assert_(ob1 is ob)
            self.assertEqual(ob1.items(), [('a', 'b')])
            self.assertEqual(ob1.stowaway.items(), [('c', 'd')])

            # Verify a new object was stored
            get_transaction().begin()
            conn2 = self.db.open()
            ob2 = conn2.root()['TestRoot2']
            self.assertEqual(ob2.items(), [('a', 'b')])
            self.assertEqual(ob2.stowaway.items(), [('c', 'd')])

            # Make a change only to the unmanaged persistent object
            # (the "stowaway").
            ob.stowaway['c'] = 'e'
            get_transaction().commit()

            # Verify the change was stored and make a change to the
            # managed persistent object.
            conn3 = self.db.open()
            ob3 = conn3.root()['TestRoot2']
            self.assertEqual(ob3.items(), [('a', 'b')])
            self.assertEqual(ob3.stowaway.items(), [('c', 'e')])
            ob3['a'] = 'z'
            get_transaction().commit()
            conn3.close()
            conn3 = None
            conn3 = self.db.open()
            ob3 = conn3.root()['TestRoot2']
            self.assertEqual(ob3['a'], 'z')
            self.assertEqual(ob3.stowaway.items(), [('c', 'e')])

            # Verify we didn't accidentally change the original object.
            self.assertEqual(ob['a'], 'b')

            # sync and verify the current state.
            conn1.sync()
            self.assertEqual(ob1.items(), [('a', 'z')])
            self.assertEqual(ob1.stowaway.items(), [('c', 'e')])

        finally:
            conn1.close()
            if conn2 is not None:
                conn2.close()
            if conn3 is not None:
                conn3.close()


    def test_store_and_load_binary(self):
        ob = TestObject()
        # strdata contains binary characters
        ob.strdata = ''.join([chr(n) for n in range(256)]) * 2

        conn1 = self.db.open()
        try:
            root = conn1.root()
            get_transaction().begin()
            root['TestRoot'] = ob
            get_transaction().commit()
            ob1 = conn1.root()['TestRoot']
            self.assertEqual(ob1.strdata, ob.strdata)
            self.assertEqual(ob1.items(), ob.items())
        finally:
            conn1.close()


    def _write_basic_object(self, conn):
        ob = TestObject()
        ob.strdata = 'abc'
        root = conn.root()
        get_transaction().begin()
        root['TestRoot'] = ob
        get_transaction().commit()
        return ob


    def _change_test_root(self):
        conn = self.db.open()
        try:
            ob = conn.root()['TestRoot']
            ob.strdata = 'ghi'
            get_transaction().commit()
        finally:
            conn.close()


    def test_conflict_detection(self):
        conn1 = self.db.open()
        try:
            ob1 = self._write_basic_object(conn1)
            ob1.strdata = 'def'
            run_in_thread(self._change_test_root)
            # Don't let the Connection generate the conflict.  This is
            # a test of the storage.
            conn1._invalidated.clear()
            # Verify that "def" doesn't get written, since it
            # conflicts with "ghi".
            self.assertRaises(ZODB.POSException.ConflictError,
                              get_transaction().commit)
            self.assertEqual(ob1.strdata, "ghi")
        finally:
            conn1.close()


    def test_debug_conflict_errors(self):
        # When debug_conflicts is on, ApeStorage generates a
        # RuntimeError with information instead of a simple
        # ConflictError, making it easier to pinpoint the problem.
        self.storage.set_debug_conflicts(1)
        conn1 = self.db.open()
        try:
            ob1 = self._write_basic_object(conn1)
            ob1.strdata = 'def'
            run_in_thread(self._change_test_root)
            # Don't let the Connection generate the conflict.  This is
            # a test of the storage.
            conn1._invalidated.clear()
            self.assertRaises(RuntimeError, get_transaction().commit)
        finally:
            conn1.close()


    def test_new_object_conflict_detection(self):
        # Verify a new object won't overwrite existing objects by accident
        conn1 = self.db.open()
        try:
            ob1 = self._write_basic_object(conn1)
            ob1.strdata = 'def'
            conn1._set_serial(ob1, '\0' * 8)  # Pretend that it's new
            self.assertRaises(OIDConflictError, get_transaction().commit)
        finally:
            conn1.close()


    def test_remainder_cyclic_reference_restoration(self):
        # test whether the remainder pickler properly stores cyclic references
        # back to the object itself.
        ob1 = TestObject()
        ob1.myself = ob1

        conn1 = self.db.open()
        try:
            root = conn1.root()
            get_transaction().begin()
            root['TestRoot2'] = ob1
            get_transaction().commit()

            conn2 = self.db.open()
            try:
                ob2 = conn2.root()['TestRoot2']
                self.assert_(ob2.myself is ob2)
                self.assert_(ob2 is not ob1)  # Verify it didn't cheat somehow
            finally:
                conn2.close()
        finally:
            conn1.close()


    def test_copy_of(self):
        # Verifies the functionality of zodb_copy().
        ob1 = PersistentMapping()
        ob1._p_oid = 'xxx'
        self.assertEqual(ob1._p_oid, 'xxx')  # Precondition
        ob1['fish'] = PersistentMapping()
        ob1['fish']['trout'] = 1
        ob1['fish']['herring'] = 2

        ob2 = zodb_copy(ob1)
        self.assert_(ob2 is not ob1)
        self.assert_(ob2['fish'] is not ob1['fish'])
        self.assert_(ob2._p_oid is None)
        self.assertEqual(list(ob2.keys()), ['fish'])
        self.assertEqual(len(ob2['fish'].keys()), 2)


    def test_copy_of_zclass_instance(self):
        # Verifies that zodb_copy() can copy instances that look like ZClass
        # instances.
        class weird_class (Persistent):
            pass
        weird_class.__module__ = '*IAmAZClassModule'
        self.assertEqual(weird_class.__module__, '*IAmAZClassModule')

        ob1 = PersistentMapping()
        ob1['fishy'] = weird_class()

        ob2 = zodb_copy(ob1)
        self.assert_(ob2 is not ob1)
        self.assert_(ob2['fishy'] is not ob1['fishy'])
        self.assert_(ob2['fishy'].__class__ is weird_class)


    def test_p_serial_untouched(self):
        # _p_serial isn't safe to use for hashes, since _p_mtime
        # interprets it as a date stamp.  Verify Ape doesn't
        # use _p_serial for hashes.
        conn1 = self.db.open()
        try:
            ob1 = self._write_basic_object(conn1)
            self.assertEqual(ob1._p_serial, "\0" * 8)
        finally:
            conn1.close()


    def test_get_serial(self):
        # Verifies the behavior of _get_serial().
        conn1 = self.db.open()
        try:
            new_ob = TestObject()
            self.assertEqual(conn1._get_serial(new_ob), '\0' * 8)
            ob1 = self._write_basic_object(conn1)
            self.assertNotEqual(conn1._get_serial(ob1), '\0' * 8)
        finally:
            conn1.close()


    def test_get_serial_detects_new_objects(self):
        # Verifies the behavior of _get_serial() and _set_serial().
        conn1 = self.db.open()
        try:
            ob = self._write_basic_object(conn1)
            self.assertNotEqual(conn1._get_serial(ob), '\0' * 8)
            # Replace the object and verify it gets a new serial.
            ob1 = PersistentMapping()
            ob1.strdata = 'cba'
            ob1._p_oid = conn1.root()['TestRoot']._p_oid
            conn1.root()['TestRoot'] = ob1
            self.assertEqual(conn1._get_serial(ob1), '\0' * 8)
        finally:
            conn1.close()


    def test_serial_cleanup(self):
        # Verify that _set_serial() cleans up.
        conn1 = self.db.open()
        try:
            conn1.serial_cleanup_threshold = 10
            for n in range(conn1.serial_cleanup_threshold + 1):
                new_ob = PersistentMapping()
                new_ob._p_oid = 'fake_oid_' + str(n)
                old_size = len(conn1._serials or ())
                conn1._set_serial(new_ob, '01234567')
                new_size = len(conn1._serials)
                if new_size < old_size:
                    # Cleaned up.  Success.
                    break
            else:
                self.fail("_set_serial() did not clean up")
        finally:
            conn1.close()


    def test_get_all_sources(self):
        root_oid = self.conf.oid_gen.root_oid
        sources = self.storage.get_all_sources([root_oid])
        self.assert_(not sources[root_oid])
        # The test passed, but check for a false positive.
        oid = 'nonexistent-oid'
        self.assertRaises(KeyError, self.storage.get_all_sources, [oid])


    def test_clean_changed(self):
        # Verify the storage discards the list of changed objects on
        # commit or abort.
        conn1 = self.db.open()
        try:
            ob1 = self._write_basic_object(conn1)
            self.assertEqual(len(self.storage.changed), 0)
            ob1.strdata = 'def'
            get_transaction().abort()
            self.assertEqual(len(self.storage.changed), 0)
        finally:
            conn1.close()


if __name__ == '__main__':
    unittest.main()
