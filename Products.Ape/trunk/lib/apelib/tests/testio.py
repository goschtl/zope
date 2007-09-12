##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests of apelib.core.io

$Id$
"""

import unittest

import ZODB
from Persistence import PersistentMapping

from apelib.core import io
from apelib.core.interfaces import IObjectDatabase
from serialtestbase import SerialTestBase, TestObject


class TestObjectDatabase:
    __implements__ = IObjectDatabase

    def get(self, oid, hints=None):
        raise NotImplementedError

    def identify(self, obj):
        raise NotImplementedError

    def new_oid(self):
        raise NotImplementedError
    
    def get_class(self, module, name):
        m = __import__(module)
        return getattr(m, name)



class ApeIOTests(SerialTestBase, unittest.TestCase):

    def get_object_database(self):
        return TestObjectDatabase()

    def test_impl(self):
        # Test of test :-)
        from Interface.Verify import verifyClass
        verifyClass(IObjectDatabase, TestObjectDatabase)

    def test_serialize_and_deserialize(self):
        ob = TestObject()
        ob.strdata = '345'
        ob['a'] = 'b'
        ob['c'] = 'd'
        oid = 'test'
        obj_db = self.get_object_database()
        obsys = io.ObjectSystemIO(self.conf, obj_db)
        event, classification, state = obsys.serialize(oid, ob)

        ob2 = obsys.new_instance(oid, classification)
        obsys.deserialize(oid, ob2, classification, state)
        self.assertEqual(ob.strdata, ob2.strdata)
        self.assertEqual(ob.data, ob2.data)


    def test_store_and_load(self):
        # Tests both serialization and storage
        ob = TestObject()
        ob.strdata = '345'
        ob['a'] = 'b'
        ob['c'] = 'd'
        oid = 'test'
        obj_db = self.get_object_database()
        obsys = io.ObjectSystemIO(self.conf, obj_db)
        gwsys = io.GatewayIO(self.conf, self.conns)
        event, classification, state = obsys.serialize(oid, ob)
        gwsys.store(oid, classification, state, True)

        event, classification, state, hash_value = gwsys.load(oid)
        ob2 = obsys.new_instance(oid, classification)
        obsys.deserialize(oid, ob2, classification, state)
        self.assertEqual(ob.strdata, ob2.strdata)
        self.assertEqual(ob.data, ob2.data)


    def test_export_import(self):
        root = PersistentMapping()

        test1 = TestObject()
        test1.strdata = '345'
        test1['a'] = 'b'
        test1['c'] = 'd'
        root['TestRoot'] = test1
        test2 = TestObject()
        test2.leftover = 'oops'
        test2['true'] = 'undecided'
        root['TestRoot2'] = test2

        oid = ''
        exporter = io.ExportImport(self.conf, self.conns)
        exporter.export_object(root, oid)

        importer = io.ExportImport(self.conf, self.conns)
        roota = importer.import_object(oid)
        self.assert_(root is not roota)
        self.assert_(root['TestRoot'] is not roota['TestRoot'])
        self.assert_(root['TestRoot2'] is not roota['TestRoot2'])
        self.assertEqual(root['TestRoot'].data, roota['TestRoot'].data)
        self.assertEqual(root['TestRoot2'].data, roota['TestRoot2'].data)
        self.assertEqual(root['TestRoot'].strdata, roota['TestRoot'].strdata)
        self.assertEqual(root['TestRoot2'].leftover,
                         roota['TestRoot2'].leftover)



if __name__ == '__main__':
    unittest.main()
