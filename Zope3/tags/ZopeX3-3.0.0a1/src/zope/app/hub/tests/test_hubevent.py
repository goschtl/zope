##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
$Id$
"""
import unittest

from zope.app.hub import \
     ObjectRegisteredHubEvent, ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent, ObjectMovedHubEvent, \
     ObjectRemovedHubEvent

from zope.exceptions import NotFoundError

class DummyObjectHub:

    def __init__(self, ruid, obj, location):
        self.ruid = ruid
        self.obj = obj
        self.location = location


    def getObject(self, ruid):
        if ruid==self.ruid:
            return self.obj

        raise NotFoundError

    def getPath(self, ruid):
        if ruid==self.ruid:
            return self.location

        raise NotFoundError


class AbstractTestHubEvent(unittest.TestCase):

    location = '/some/location'
    hubid = 23
    obj = object()
    klass = None

    def setUp(self):
        self.hub = DummyObjectHub(self.hubid, self.obj, self.location)
        self.event = self.klass(self.hub, self.hubid, self.location, self.obj)

    def testGetHub(self):
        self.assertEqual(self.event.hub, self.hub)

    def testGetLocation(self):
        self.assertEqual(self.event.location, self.location)

    def testGetHubId(self):
        # Test hubid
        self.assertEqual(self.event.hubid, self.hubid)

    def testGetObject(self):
        self.assertEqual(self.event.object, self.obj)

class TestObjectRegisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectRegisteredHubEvent

class TestEmptyObjectRegisteredHubEvent(TestObjectRegisteredHubEvent):

    def setUp(self):
        self.hub = DummyObjectHub(self.hubid, self.obj, self.location)
        self.event = self.klass(self.hub, self.hubid)

class TestObjectUnregisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectUnregisteredHubEvent

class TestEmptyObjectUnregisteredHubEvent(unittest.TestCase):

    location = '/some/location'
    hubid = 23
    obj = object()
    klass = None

    klass = ObjectUnregisteredHubEvent

    def testRaisesTypeError(self):
        self.assertRaises(TypeError,
                          self.klass,
                          DummyObjectHub(self.hubid,
                                         self.obj,
                                         self.location),
                          self.hubid)

class TestObjectModifiedHubEvent(AbstractTestHubEvent):

    klass = ObjectModifiedHubEvent

class TestEmptyObjectModifiedHubEvent(TestObjectModifiedHubEvent):

    def setUp(self):
        self.hub = DummyObjectHub(self.hubid, self.obj, self.location)
        self.event = self.klass(self.hub, self.hubid)

class TestObjectMovedHubEvent(AbstractTestHubEvent):

    fromLocation = '/old/location'

    def setUp(self):
        self.hub = DummyObjectHub(self.hubid, self.obj, self.location)
        self.event = self.klass(self.hub,
                                self.hubid,
                                self.fromLocation,
                                self.location,
                                self.obj)

    def testGetFromLocation(self):
        # Test from location
        self.assertEqual(self.event.fromLocation, self.fromLocation)

    klass = ObjectMovedHubEvent

class TestEmptyObjectMovedHubEvent(TestObjectMovedHubEvent):

    def setUp(self):
        self.hub = DummyObjectHub(self.hubid, self.obj, self.location)
        self.event = self.klass(self.hub,
                                self.hubid,
                                self.fromLocation)

class TestObjectRemovedHubEvent(AbstractTestHubEvent):

    klass = ObjectRemovedHubEvent

class TestEmptyObjectRemovedHubEvent(TestEmptyObjectUnregisteredHubEvent):

    klass = ObjectRemovedHubEvent

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectRegisteredHubEvent),
        unittest.makeSuite(TestEmptyObjectRegisteredHubEvent),
        unittest.makeSuite(TestObjectUnregisteredHubEvent),
        unittest.makeSuite(TestEmptyObjectUnregisteredHubEvent),
        unittest.makeSuite(TestObjectModifiedHubEvent),
        unittest.makeSuite(TestEmptyObjectModifiedHubEvent),
        unittest.makeSuite(TestObjectMovedHubEvent),
        unittest.makeSuite(TestEmptyObjectMovedHubEvent),
        unittest.makeSuite(TestObjectRemovedHubEvent),
        unittest.makeSuite(TestEmptyObjectRemovedHubEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
