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
"""testObjectHub

Revision information:
$Id: test_objecthub.py,v 1.7 2003/03/21 15:29:09 alga Exp $
"""

import unittest, sys
from zope.app.services.tests.objecthubsetup import ObjectHubSetup

from zope.app.interfaces.event\
        import IObjectAddedEvent, IObjectRemovedEvent, IObjectModifiedEvent,\
               IObjectMovedEvent
from zope.app.event.objectevent\
        import ObjectAddedEvent, ObjectModifiedEvent, ObjectRemovedEvent,\
               ObjectMovedEvent, ObjectCreatedEvent
from zope.app.interfaces.services.hub import ObjectHubError
from zope.app.interfaces.services.hub import \
     IObjectRemovedHubEvent, IObjectModifiedHubEvent, \
     IObjectMovedHubEvent, IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent

from zope.app.services.hub \
        import ObjectModifiedHubEvent, ObjectRemovedHubEvent, \
        ObjectMovedHubEvent, ObjectRegisteredHubEvent, \
        ObjectUnregisteredHubEvent

from zope.exceptions import NotFoundError
from types import StringTypes

from zope.app.traversing import traverse, canonicalPath

# while these tests don't really test much of the placeful aspect of the
# object hub, they do at least test basic functionality.

# we'll need real tests of the placeful aspects, but for now a basic
# test happens simply by virtue of the testHubEvent module in this
# directory

class TransmitHubEventTest(ObjectHubSetup, unittest.TestCase):
    hubid = 23
    location = '/foo/bar'
    obj = object()
    # Don't test the HubEvent base class.
    # See below for testing subclasses / subinterfaces
    # klass = HubEvent
    # interface = IHubEvent

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpLoggingSubscriber()
        self.hub_event = self.klass(self.object_hub,
                                    self.hubid,
                                    self.location,
                                    self.obj)

    def testTransmittedEvent(self):
        # Test that the HubEvents are transmitted by the notify method
        self.object_hub.notify(self.hub_event)

        self.subscriber.verifyEventsReceived(self, [
                (self.interface, self.hubid, self.location)
            ])

class TransmitObjectRemovedHubEventTest(TransmitHubEventTest):
    interface = IObjectRemovedHubEvent
    klass = ObjectRemovedHubEvent

class TransmitObjectModifiedHubEventTest(TransmitHubEventTest):
    interface = IObjectModifiedHubEvent
    klass = ObjectModifiedHubEvent

class TransmitObjectMovedHubEventTest(TransmitHubEventTest):
    interface = IObjectMovedHubEvent
    klass = ObjectMovedHubEvent

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpLoggingSubscriber()
        self.hub_event = self.klass(
                self.object_hub, self.hubid,
                '/old/location', self.location, self.obj)

class TransmitObjectRegisteredHubEventTest(TransmitHubEventTest):
    interface = IObjectRegisteredHubEvent
    klass = ObjectRegisteredHubEvent

class TransmitObjectUnregisteredHubEventTest(TransmitHubEventTest):
    interface = IObjectUnregisteredHubEvent
    klass = ObjectUnregisteredHubEvent

class BasicHubTest(ObjectHubSetup, unittest.TestCase):
    location = '/foo/bar'
    obj = object()
    new_location = '/baz/spoo'

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpLoggingSubscriber()
        self.setEvents()

    def setEvents(self):
        self.created_event = ObjectCreatedEvent(object())
        self.added_event = ObjectAddedEvent(self.obj, self.location)
        self.added_new_location_event = ObjectAddedEvent(
            self.obj, self.new_location)
        self.removed_event = ObjectRemovedEvent(self.obj, self.location)
        self.modified_event = ObjectModifiedEvent(self.obj, self.location)
        self.moved_event = ObjectMovedEvent(self.obj,
                                            self.location,
                                            self.new_location)

class TestRegistrationEvents(BasicHubTest):
    def testRegistration(self):
        self.assertRaises(NotFoundError,
                          self.object_hub.unregister,
                          self.location)
        self.assertRaises(NotFoundError, self.object_hub.unregister, 42)

        hubid = self.object_hub.register(self.location)
        hubid2 = self.object_hub.register(self.new_location)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectRegisteredHubEvent, hubid, self.location),
                (IObjectRegisteredHubEvent, hubid2, self.new_location)
            ])

        # register again and check for error
        self.assertRaises(ObjectHubError,
                          self.object_hub.register,
                          self.location)

        # unregister first object by location
        self.object_hub.unregister(self.location)
        self.subscriber.verifyEventsReceived(self, [
                (IObjectUnregisteredHubEvent, hubid, self.location)
            ])
        # unregister second object by hub id
        self.object_hub.unregister(hubid2)
        self.subscriber.verifyEventsReceived(self, [
                (IObjectUnregisteredHubEvent, hubid2, self.new_location)
            ])

    def testRegistrationRelativeLocation(self):
        self.assertRaises(ValueError, self.object_hub.register, 'foo/bar')

class TestSearchRegistrations(BasicHubTest):
    locations = (
        '/',
        '/foo',
        '/foo/baq',
        '/foo/baq/baz',
        '/foo/bar',
        '/foo/bar/baz',
        '/foo/bar2/baz',
        '/foo/bar/baz2',
        '/foo/bar/baz3',
        '/foo/bas',
        '/foo/bas/baz',
        )

    def setUp(self):
        ObjectHubSetup.setUp(self)

    def testSearchAll(self):
        object_hub = self.object_hub
        location_hubid = [(location,
                           object_hub.register(location))
                          for location in self.locations]
        location_hubid.sort()

        r = list(object_hub.iterRegistrations())
        self.assertEqual(r, location_hubid)

    def testSearchSome(self):
        object_hub = self.object_hub
        location_hubid= [(location,
                           object_hub.register(location))
                          for location in self.locations
                          if location.startswith('/foo/bar/')]
        location_hubid.sort()

        r = list(object_hub.iterRegistrations('/foo/bar'))
        self.assertEqual(r, location_hubid)

    def testIterObjectRegistrations(self):
        class FakeObject:
            def __init__(self, location):
                self.location = location
            def __str__(self):
                return 'FakeObject at %s' % self.location
            def __eq__(self, other):
                return self.location == other.location

        def fake_object_for_location(location):
            return FakeObject(canonicalPath(location))

        from zope.app.interfaces.traversing import ITraverser
        class DummyTraverser:
            __implements__ = ITraverser
            def __init__(self, context):
                pass
            def traverse(self, location):
                return fake_object_for_location(location)

        from zope.component.adapter import provideAdapter
        provideAdapter(None, ITraverser, DummyTraverser)

        object_hub = self.object_hub
        location_hubid_object = [(location,
                                  object_hub.register(location),
                                  fake_object_for_location(location)
                                 )
                                 for location in self.locations]
        location_hubid_object.sort()

        r = [loc_id for loc_id in object_hub.iterObjectRegistrations()]
        r.sort()
        self.assertEqual(r, location_hubid_object)

class TestNoRegistration(BasicHubTest):

    def testAddWithoutRegistration(self):
        # Test that no HubIdEvents are generated if there is no registration
        hub = self.object_hub
        event = self.added_event
        location = self.location

        hub.notify(event)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
            ])


class TestObjectCreatedEvent(BasicHubTest):
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpRegistrationSubscriber()
        self.setEvents()

    def testLookingUpLocation(self):
        hub = self.object_hub
        event = self.created_event
        location = None

        hub.notify(event)

        self.assertEqual(location_from_hub, location)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectCreatedEvent, location),
            ])

    def testLookupUpAbsentLocation(self):
        # Test that we don't find an hub id for location that we haven't added.
        hub = self.object_hub
        event = self.added_event
        location = self.location

        # Do not add the location to the hub
        # hub.notify(event)

        self.assertRaises(NotFoundError, hub.getHubId, location)

        self.subscriber.verifyEventsReceived(self, [])

class TestObjectAddedEvent(BasicHubTest):
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpRegistrationSubscriber()
        self.setEvents()

    def testLookingUpLocation(self):
        # Test that the location is in the lookup
        # Compare getHubIdForLocation and getLocationForHubId
        # Checks the sequence of events
        hub = self.object_hub
        event = self.added_event
        location = self.location

        hub.notify(event)

        hubid = hub.getHubId(location)
        # check that hub id is an int
        self.failUnless(isinstance(hubid, int)) # int(hubid)

        location_from_hub = hub.getPath(hubid)

        self.assertEqual(location_from_hub, location)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, hubid, location),
            ])

    def testLookupUpAbsentLocation(self):
        # Test that we don't find an hub id for location that we haven't added.
        hub = self.object_hub
        event = self.added_event
        location = self.location

        # Do not add the location to the hub
        # hub.notify(event)

        self.assertRaises(NotFoundError, hub.getHubId, location)

        self.subscriber.verifyEventsReceived(self, [])

    def testLookupUpAbsentHubId(self):
        # Test that we don't find a location for an hub id that isn't there.
        hub = self.object_hub
        event = self.added_event

        # Do not add the location to the hub
        # hub.notify(event)

        absent_hubid = 12

        self.assertRaises(NotFoundError, hub.getPath, absent_hubid)

        self.subscriber.verifyEventsReceived(self, [])


class TestObjectRemovedEvent(BasicHubTest):
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpRegistrationSubscriber()
        self.setEvents()

    def testRemovedLocation(self):
        # Test that a location that is added then removed is actually gone.
        hub = self.object_hub
        added_event = self.added_event
        removed_event = self.removed_event
        location = self.location
        obj = self.obj

        hub.notify(added_event)

        hubid = hub.getHubId(location)

        # check that hubid is an int
        self.failUnless(isinstance(hubid, int)) # int(hubid)

        hub.notify(removed_event)

        self.assertRaises(NotFoundError, hub.getHubId, location)
        self.assertRaises(NotFoundError, hub.getPath, hubid)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, hubid, location),
                (IObjectRemovedEvent, location),
                (IObjectRemovedHubEvent, hubid, location, obj),
            ])


    def testRemovedAbsentLocation(self):
        # Test that removing an absent location is silently ignored.
        hub = self.object_hub
        added_event = self.added_event
        removed_event = self.removed_event
        location = self.location

        # Do not add location
        # hub.notify(added_event)

        hub.notify(removed_event)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectRemovedEvent, location),
            ])


class TestObjectModifiedEvent(BasicHubTest):
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpRegistrationSubscriber()
        self.setEvents()

    def testModifiedLocation(self):
        # Test that lookup state does not change after an object modify event.
        hub = self.object_hub
        added_event = self.added_event
        modified_event = self.modified_event
        location = self.location

        hub.notify(added_event)

        hubid = hub.getHubId(location)
        # check that hubid is an int
        self.failUnless(isinstance(hubid, int)) # int(hubid)

        location_from_hub = hub.getPath(hubid)
        self.assertEqual(location_from_hub, location)

        hub.notify(modified_event)

        hubid2 = hub.getHubId(location)
        location_from_hub2 = hub.getPath(hubid2)

        self.assertEqual(location_from_hub, location_from_hub2)
        self.assertEqual(hubid, hubid2)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, hubid, location),
                (IObjectModifiedEvent, location),
                (IObjectModifiedHubEvent, hubid, location)
            ])


    def testModifiedAbsentLocation(self):
        # Test that lookup state does not change after an object modify event.
        # In this case, modify of an absent location is a noop.
        hub = self.object_hub
        added_event = self.added_event
        modified_event = self.modified_event
        location = self.location

        # Do not add location
        # hub.notify(added_event)

        hub.notify(modified_event)
        self.assertRaises(NotFoundError, hub.getHubId, location)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectModifiedEvent, location),
            ])


class TestObjectMovedEvent(BasicHubTest):
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpRegistrationSubscriber()
        self.setEvents()

    def testMovedLocation(self):
        # Test that the location does indeed change after a move.
        hub = self.object_hub
        added_event = self.added_event
        moved_event = self.moved_event
        location = self.location
        new_location = self.new_location

        hub.notify(added_event)
        hubid = hub.getHubId(location)

        hub.notify(moved_event)

        location_from_hub = hub.getPath(hubid)

        self.assertEqual(location_from_hub, new_location)
        self.assertRaises(NotFoundError, hub.getHubId, location)

        hubid2 = hub.getHubId(new_location)
        self.assertEqual(hubid2, hubid)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, hubid, location),
                (IObjectMovedEvent, new_location),
                (IObjectMovedHubEvent, hubid, new_location)
            ])


    def testMovedAbsentLocation(self):
        # Test that moving an absent location is a no-op.
        hub = self.object_hub
        added_event = self.added_event
        moved_event = self.moved_event
        location = self.location
        new_location = self.new_location

        # Do not add location
        # hub.notify(added_event)

        hub.notify(moved_event)
        self.assertRaises(NotFoundError, hub.getHubId, location)
        self.assertRaises(NotFoundError, hub.getHubId, new_location)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectMovedEvent, new_location),
                ])


    def testMovedToExistingLocation(self):
        # Test that moving to an existing location raises ObjectHubError.
        hub = self.object_hub
        added_event = self.added_event
        added_event2 = self.added_new_location_event
        moved_event = self.moved_event
        location = self.location
        new_location = self.new_location

        hub.notify(added_event)
        hub.notify(added_event2)

        self.assertRaises(ObjectHubError, hub.notify, moved_event)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, None, location),
                (IObjectAddedEvent, new_location),
                (IObjectRegisteredHubEvent, None, new_location),
                (IObjectMovedEvent, new_location),
            ])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TransmitObjectRemovedHubEventTest),
        unittest.makeSuite(TransmitObjectModifiedHubEventTest),
        unittest.makeSuite(TransmitObjectMovedHubEventTest),
        unittest.makeSuite(TransmitObjectRegisteredHubEventTest),
        unittest.makeSuite(TransmitObjectUnregisteredHubEventTest),
        unittest.makeSuite(TestRegistrationEvents),
        unittest.makeSuite(TestNoRegistration),
        unittest.makeSuite(TestSearchRegistrations),
        unittest.makeSuite(TestObjectAddedEvent),
        unittest.makeSuite(TestObjectRemovedEvent),
        unittest.makeSuite(TestObjectModifiedEvent),
        unittest.makeSuite(TestObjectMovedEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
