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
"""
$Id$
"""
# in this version of these tests, we are no longer using a fake
# ObjectHub, which makes these tests less pure...but still useful
# as a test for both the events and the object hub for now.

import unittest
from zope.app.hub.tests.objecthubsetup import ObjectHubSetup
from zope.app.hub import \
     ObjectRegisteredHubEvent, ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent, ObjectMovedHubEvent, ObjectRemovedHubEvent
from zope.app.traversing import getPath

class AbstractTestHubEvent(ObjectHubSetup, unittest.TestCase):

    klass = None

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub,
                                self.hubid,
                                self.location,
                                self.obj)

    def testGetLocation(self):
        # Test getLocation method
        self.assertEqual(self.event.location, self.location)

    def testGetHubId(self):
        # Test getHubId method
        self.assertEqual(self.event.hubid, self.hubid)

    def testGetObject(self):
        # Test getObject method
        self.assertEqual(self.event.object, self.obj)

class TestObjectRegisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectRegisteredHubEvent

class TestEmptyObjectRegisteredHubEvent(TestObjectRegisteredHubEvent):

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub, self.hubid)

class TestObjectUnregisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectUnregisteredHubEvent

class TestEmptyObjectUnregisteredHubEvent(TestObjectUnregisteredHubEvent):

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub, self.hubid, self.location)

class TestObjectModifiedHubEvent(AbstractTestHubEvent):

    klass = ObjectModifiedHubEvent

class TestEmptyObjectModifiedHubEvent(TestObjectModifiedHubEvent):

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub, self.hubid)

class TestObjectMovedHubEvent(AbstractTestHubEvent):

    fromLocation = '/old/location'

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub,
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
        ObjectHubSetup.setUp(self)
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPath(self.obj)
        self.event = self.klass(self.object_hub,
                                self.hubid,
                                self.fromLocation)

class TestObjectRemovedHubEvent(AbstractTestHubEvent):

    klass = ObjectRemovedHubEvent

# Hooked empty object removed not needed

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
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
