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
"""Serialization tests

$Id$
"""

import unittest

import ZODB
from Persistence import PersistentMapping

from apelib.core.events \
     import LoadEvent, StoreEvent, SerializationEvent, DeserializationEvent
from apelib.core.interfaces import SerializationError
from serialtestbase import SerialTestBase, TestObject


class SimpleClass:
    """Represents second-class persistent objects.
    """
    def __init__(self, data):
        self.data = data


class MockObjectDatabase:
    """Implements only enough to satisfy testCatchExtraAttribute
    """
    def identify(self, obj):
        return None


class SerializationTests(SerialTestBase, unittest.TestCase):
    """Tests of basic events, serializers, and gateways.

    No connections or object databases are provided.
    """

    def test_serialize_and_deserialize(self):
        classification = None
        ob = TestObject()
        ob['a'] = 'b'
        ob['c'] = 'd'
        obj_db = None
        m = self.conf.mappers["tm"]
        event = SerializationEvent(
            self.conf, m, '', classification, obj_db, ob)
        full_state = m.serializer.serialize(event)
        ob2 = TestObject()
        event = DeserializationEvent(
            self.conf, m, '', classification, obj_db, ob2)
        m.serializer.deserialize(event, full_state)
        self.assertEqual(ob.strdata, ob2.strdata)
        self.assertEqual(ob.data, ob2.data)

    def test_store_and_load(self):
        classification = None
        ob = TestObject()
        ob.strdata = '345'
        ob['a'] = 'b'
        ob['c'] = 'd'
        obj_db = None
        m = self.conf.mappers["tm"]
        event = SerializationEvent(
            self.conf, m, '', classification, obj_db, ob)
        full_state = m.serializer.serialize(event)
        event = StoreEvent(
            self.conf, m, '', classification, self.conns, True)
        m.gateway.store(event, full_state)

        event = LoadEvent(
            self.conf, m, '', classification, self.conns)
        full_state, serial = m.gateway.load(event)
        ob2 = TestObject()
        event = DeserializationEvent(
            self.conf, m, '', classification, obj_db, ob2)
        m.serializer.deserialize(event, full_state)
        self.assertEqual(ob.strdata, ob2.strdata)
        self.assertEqual(ob.data, ob2.data)

    def test_catch_extra_attribute(self):
        # The mapper for PersistentMappings doesn't allow an
        # extra attribute.
        classification = None
        ob = PersistentMapping()
        ob.extra = '678'
        ob['a'] = 'b'
        ob['c'] = 'd'
        obj_db = MockObjectDatabase()
        m = self.conf.mappers["pm"]
        event = SerializationEvent(
            self.conf, m, '', classification, obj_db, ob)
        self.assertRaises(SerializationError, m.serializer.serialize, event)

    def test_shared_attribute(self):
        # Test of an attribute shared between a normal serializer and
        # a remainder serializer.
        classification = None
        ob = TestObject()
        data = SimpleClass('This is a shared piece of data')
        ob.extra = data
        ob['a'] = data
        obj_db = None
        m = self.conf.mappers["tm"]
        event = SerializationEvent(
            self.conf, m, '', classification, obj_db, ob)
        full_state = m.serializer.serialize(event)
        event = StoreEvent(
            self.conf, m, '', classification, self.conns, True)
        m.gateway.store(event, full_state)

        # Now load the state into a different object
        event = LoadEvent(
            self.conf, m, '', classification, self.conns)
        full_state, serial = m.gateway.load(event)
        ob2 = TestObject()
        event = DeserializationEvent(
            self.conf, m, '', classification, obj_db, ob2)
        m.serializer.deserialize(event, full_state)
        self.assertEqual(ob.extra.data, ob2.extra.data)
        self.assertEqual(ob.keys(), ob2.keys())

        # Check that both ways to access the SimpleClass instance
        # result in the same object.
        self.assert_(ob2['a'] is ob2.extra, (ob2['a'], ob2.extra))
        self.assert_(ob2['a'] is not data)  # Verify it didn't cheat somehow


if __name__ == '__main__':
    unittest.main()
