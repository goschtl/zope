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
$Id: test_objecthub.py,v 1.13 2003/09/21 17:33:15 jim Exp $
"""

import unittest
from zope.app import zapi
from zope.app.services.tests.objecthubsetup import ObjectHubSetup

from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.container import IObjectAddedEvent
from zope.app.interfaces.container import IObjectRemovedEvent
from zope.app.interfaces.container import IObjectMovedEvent

from zope.app.container.contained import ObjectAddedEvent, ObjectRemovedEvent
from zope.app.container.contained import ObjectMovedEvent
from zope.app.event.objectevent import ObjectModifiedEvent, ObjectCreatedEvent

from zope.app.interfaces.services.hub import ObjectHubError
from zope.app.interfaces.services.hub import IObjectRemovedHubEvent
from zope.app.interfaces.services.hub import IObjectModifiedHubEvent
from zope.app.interfaces.services.hub import IObjectMovedHubEvent
from zope.app.interfaces.services.hub import IObjectRegisteredHubEvent
from zope.app.interfaces.services.hub import IObjectUnregisteredHubEvent

from zope.app.services.hub import ObjectModifiedHubEvent, ObjectRemovedHubEvent
from zope.app.services.hub import ObjectMovedHubEvent, ObjectRegisteredHubEvent
from zope.app.services.hub import ObjectUnregisteredHubEvent

from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.location import Location

from zope.exceptions import NotFoundError

from zope.app.traversing import canonicalPath, traverse

from zope.interface import implements, directlyProvides

from zope.app.container.contained import Contained

# while these tests don't really test much of the placeful aspect of the
# object hub, they do at least test basic functionality.

# we'll need real tests of the placeful aspects, but for now a basic
# test happens simply by virtue of the testHubEvent module in this
# directory

class TransmitHubEventTest(ObjectHubSetup, unittest.TestCase):
    hubid = 23
    location = '/folder1/folder1_1'
    # Don't test the HubEvent base class.
    # See below for testing subclasses / subinterfaces
    # klass = HubEvent
    # interface = IHubEvent

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpLoggingSubscriber()
        self.obj = zapi.traverse(self.rootFolder, self.location)
        
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
        self.obj = zapi.traverse(self.rootFolder, self.location)
        self.hub_event = self.klass(
                self.object_hub, self.hubid,
                '/old/location', self.location, self.obj)

class TransmitObjectRegisteredHubEventTest(TransmitHubEventTest):
    interface = IObjectRegisteredHubEvent
    klass = ObjectRegisteredHubEvent

class TransmitObjectUnregisteredHubEventTest(TransmitHubEventTest):
    interface = IObjectUnregisteredHubEvent
    klass = ObjectUnregisteredHubEvent

class Folder(Location):
    pass

class BasicHubTest(ObjectHubSetup, unittest.TestCase):
    location = '/folder1/folder1_1'
    new_location = '/folder2/folder2_1'

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.setUpLoggingSubscriber()
        self.obj = zapi.traverse(self.rootFolder, self.location)
        self.setEvents()

    def setEvents(self):
        obj = self.obj
        self.created_event = ObjectCreatedEvent(obj)
        self.added_event = ObjectAddedEvent(obj)
        newobj = zapi.traverse(self.rootFolder, self.new_location)
        self.added_new_location_event = ObjectAddedEvent(newobj)
        self.removed_event = ObjectRemovedEvent(obj)
        self.modified_event = ObjectModifiedEvent(obj)
        self.moved_event = ObjectMovedEvent(
            obj,
            obj.__parent__, obj.__name__,
            newobj.__parent__, newobj.__name__,
            )

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
        from zope.app.traversing.adapters import Traverser
        class DummyTraverser(Traverser):
            implements(ITraverser)
            def traverse(self, location, *args, **kw):
                if location in TestSearchRegistrations.locations:
                    return fake_object_for_location(location)
                else:
                    return Traverser.traverse(self, location, *args, **kw)

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
        self.obj = zapi.traverse(self.rootFolder, self.location)
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
        self.obj = zapi.traverse(self.rootFolder, self.location)
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
        self.obj = zapi.traverse(self.rootFolder, self.location)
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
        self.obj = zapi.traverse(self.rootFolder, self.location)
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

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, hubid, location),
            ])

        # simulate moving the object
        self.obj.__parent__ = zapi.traverse(self.rootFolder, "folder2")
        self.obj.__name__ = "folder2_1"

        hub.notify(moved_event)

        location_from_hub = hub.getPath(hubid)

        self.assertEqual(location_from_hub, new_location)
        self.assertRaises(NotFoundError, hub.getHubId, location)

        hubid2 = hub.getHubId(new_location)
        self.assertEqual(hubid2, hubid)

        self.subscriber.verifyEventsReceived(self, [
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

        # simulate moving the object
        self.obj.__parent__ = zapi.traverse(self.rootFolder, "folder2")
        self.obj.__name__ = "folder2_1"

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

        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IObjectRegisteredHubEvent, None, location),
                (IObjectAddedEvent, new_location),
                (IObjectRegisteredHubEvent, None, new_location),
            ])

        # simulate moving the object
        self.obj.__parent__ = zapi.traverse(self.rootFolder, "folder2")
        self.obj.__name__ = "folder2_1"

        self.assertRaises(ObjectHubError, hub.notify, moved_event)

        self.subscriber.verifyEventsReceived(self, [
                (IObjectMovedEvent, new_location),
            ])


class TestLazyUnregistration(BasicHubTest):
    """For the time being, the hub isn't notified of objects removed as
    a result of their parent being deleted. E.g. the hub does not receive
    notification of folder content removal when the folder is deleted.

    These tests confirm that the hub will behave as expected even when it
    contains references to missing objects.

    There is only one method that lazily unregisters objects:

        getObject

    iterObjectRegistrations would be a candidate for lazy unregistration,
    but it is currently implemented using yield, which prevents objects
    from being unregistered during iteration.

    The other object hub methods will reflect the invalid data without
    unregistering. Each of the tests in this class documents the expected
    behavior of each of the object hub methods wrt lazy unregistration.
    """

    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.rootFolder['deleted'] = Contained()
        self.deleted_obj = self.rootFolder['deleted']
        self.deleted_path = '/deleted'
        self.rootFolder['valid'] = Contained()
        self.valid_obj = self.rootFolder['valid']
        self.valid_path = '/valid'

        # register the objects
        self.deleted_hubid = self.object_hub.register(self.deleted_obj)
        self.valid_hubid = self.object_hub.register(self.valid_obj)
        self.assertEqual(self.object_hub.numRegistrations(), 2)

        # delete an object - it should still be reigstered with the hub
        del self.rootFolder['deleted']
        self.assertRaises(NotFoundError, traverse, self.rootFolder, 'deleted')
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def _verifyUnregistered(self):
        # confirm that deleted is not registered
        self.assertRaises(NotFoundError, self.object_hub.getObject, 
            self.deleted_hubid)
        self.assertEqual(self.object_hub.numRegistrations(), 1)

        # confirm that valid object wasn't effected by lazy unregistration
        self.assertEqual(self.object_hub.getHubId(self.valid_obj), 
            self.valid_hubid)
        self.assertEqual(self.object_hub.getHubId(self.valid_path),
            self.valid_hubid)
        self.assertEqual(self.object_hub.getPath(self.valid_hubid),
            self.valid_path)


    def testGetHubId(self):
        # no lazy unregistration
        self.assert_(self.object_hub.getHubId(self.deleted_path))
        #self.assert_(self.object_hub.getHubId(self.deleted_obj))
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def testGetPath(self):
        # no lazy unregistration
        self.assertEqual(self.object_hub.getPath(self.deleted_hubid),
            self.deleted_path)
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def testGetObject(self):
        # lazy unregistration
        self.assertRaises(NotFoundError, self.object_hub.getObject, 
            self.deleted_hubid)
        self._verifyUnregistered()


    def testRegister(self):
        # no lazy unregistration - currently, registration doesn't check
        # for valid paths, so it doesn't make sense to unregister
        self.assertRaises(ObjectHubError, self.object_hub.register, 
            self.deleted_path)

        # The deleted object now (after parentgeddon) has no path, so
        # this assertion no longer makes sense.
##         self.assertRaises(ObjectHubError, self.object_hub.register, 
##             self.deleted_obj)


    # We can't unregister an object *after* it has been deleted, because
    # it has no location at that point.
##     def testUnregister(self):
##         # no lazy unregistration
##         self.object_hub.unregister(self.deleted_obj)
##         self.assertEqual(self.object_hub.numRegistrations(), 1)


    def numRegistrations(self):
        # no lazy unregistration
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def testIterRegistrations(self):
        # no lazy iteration
        regs = list(self.object_hub.iterRegistrations())
        self.assertEqual(len(regs), 2)
        self.assert_((self.deleted_path, self.deleted_hubid) in regs)
        self.assert_((self.valid_path, self.valid_hubid) in regs)
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def testIterObjectRegistrations(self):
        # no lazy unregistration - however, missing objects are returned
        # as None in the tuple
        objects = list(self.object_hub.iterObjectRegistrations())
        self.assertEqual(len(objects), 2)
        self.assert_(
            (self.deleted_path, self.deleted_hubid, None) in objects)
        self.assert_((
            self.valid_path, 
            self.valid_hubid, 
            self.object_hub.getObject(self.valid_hubid)) in objects)
        self.assertEqual(self.object_hub.numRegistrations(), 2)


    def testUnregisterMissingObjects(self):
        missing = self.object_hub.unregisterMissingObjects()
        self.assertEqual(missing, 1)
        self._verifyUnregistered()



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
        unittest.makeSuite(TestLazyUnregistration),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
