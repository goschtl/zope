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

Revision information:
$Id: testObjectHub.py,v 1.5 2002/06/25 15:10:49 gotcha Exp $
"""

import unittest, sys

from Zope.Event.IObjectEvent import IObjectAddedEvent, IObjectRemovedEvent
from Zope.Event.IObjectEvent import IObjectModifiedEvent, IObjectMovedEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent, ObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectRemovedEvent, ObjectMovedEvent
from Zope.Event.ISubscriber import ISubscriber

from Zope.ObjectHub.ObjectHub import ObjectHub, ObjectHubError
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectAddedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectRemovedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectModifiedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectContextChangedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectRegisteredEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectUnregisteredEvent

import Zope.ObjectHub.RuidObjectEvent as RuidObjectEvent

from Zope.Exceptions import NotFoundError
from types import StringTypes

from Zope.App.Traversing import locationAsUnicode

class LoggingSubscriber:

    __implements__ = ISubscriber
    
    def __init__(self):
        self.events_received = []
    
    def notify(self, event):
        self.events_received.append(event)
        # print 'notify :', id(self),self.__class__.__name__, event.__implements__.__name__

    # see ObjectHub._canonical
    def _canonical(location):
        return locationAsUnicode(location)

    _canonical = staticmethod(_canonical)
    
    def verifyEventsReceived(self, testcase, event_spec_list):
        # iterate through self.events_received and check
        # that each one implements the interface that is
        # in the same place, with the same location and ruid
        
        testcase.assertEqual(len(event_spec_list), len(self.events_received))
        
        for spec,event in zip(event_spec_list, self.events_received):
            if len(spec)==4:
                interface,ruid,location,obj = spec
            elif len(spec)==3:
                interface,ruid,location = spec
                obj = None
            elif len(spec)==2:
                interface, location = spec
                obj = None
                ruid = None
            location = self._canonical(location)
            testcase.assert_(interface.isImplementedBy(event), 'Interface %s' % interface.getName())
            testcase.assertEqual(event.getLocation(), location)
            
            if obj is not None:
                testcase.assertEqual(event.getObject(), obj)
            
            # Sometimes, the test won't care about the ruid. In this case,
            # it is passed into the spec as None.
            if ruid is not None:
                testcase.assertEqual(event.getRuid(), ruid)

        self.events_received = []

class RegistrationSubscriber(LoggingSubscriber):
    def __init__(self, objectHub):
        LoggingSubscriber.__init__(self)
        self.hub = objectHub
	
    def notify(self, event):
        LoggingSubscriber.notify(self, event)
        if IObjectAddedEvent.isImplementedBy(event):
            self.hub.register(event.getLocation())                  
        elif IObjectRemovedEvent.isImplementedBy(event):
            try:
                ruid = self.hub.lookupRuid(event.getLocation())
            except NotFoundError:
                pass
            else:   
                location = event.getLocation()
                obj = event.getObject()
                removeEvent = RuidObjectEvent.RuidObjectRemovedEvent(obj, ruid, location)
                self.hub.notify(removeEvent)
                self.hub.unregister(location)                  

class TransmitRuidObjectEventTest(unittest.TestCase):
    ruid = 23
    location = '/foo/bar'
    # Don't test the RuidObjectEvent base class.
    # See below for testing subclasses / subinterfaces
    # klass = RuidObjectEvent
    # interface = IRuidObjectEvent
    
    def setUp(self):
        self.object_hub = ObjectHub()
        self.ruidobject_event = self.klass(self.object_hub, self.ruid, self.location)

        self.subscriber = LoggingSubscriber()
        self.object_hub.subscribe(self.subscriber)

    def testTransmittedEvent(self):
        """Test that the RuidObjectEvents are transmitted by the notify method     
        """ 
        self.object_hub.notify(self.ruidobject_event)
       
        self.subscriber.verifyEventsReceived(self, [
                (self.interface, self.ruid, self.location)
            ])
   
class TransmitRuidObjectAddedEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectAddedEvent
    klass = RuidObjectEvent.RuidObjectAddedEvent

class TransmitRuidObjectRemovedEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectRemovedEvent
    klass = RuidObjectEvent.RuidObjectRemovedEvent

class TransmitRuidObjectModifiedEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectModifiedEvent
    klass = RuidObjectEvent.RuidObjectModifiedEvent

class TransmitRuidObjectContextChangedEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectContextChangedEvent
    klass = RuidObjectEvent.RuidObjectContextChangedEvent

class TransmitRuidObjectRegisteredEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectRegisteredEvent
    klass = RuidObjectEvent.RuidObjectRegisteredEvent

class TransmitRuidObjectUnregisteredEventTest(TransmitRuidObjectEventTest):
    interface = IRuidObjectUnregisteredEvent
    klass = RuidObjectEvent.RuidObjectUnregisteredEvent
    
class BasicHubTest(unittest.TestCase):

    location = '/foo/bar'
    obj = object()
    new_location = '/baz/spoo'

    def setUp(self):
        self.object_hub = ObjectHub()
        self.setEvents()
        self.subscriber = LoggingSubscriber()
        self.object_hub.subscribe(self.subscriber)


    def setEvents(self):
        self.added_event = ObjectAddedEvent(self.location)
        self.added_new_location_event = ObjectAddedEvent(self.new_location)
        self.removed_event = ObjectRemovedEvent(self.location, self.obj)
        self.modified_event = ObjectModifiedEvent(self.location)
        self.moved_event = ObjectMovedEvent(self.location,
                                            self.new_location)

class TestRegistrationEvents(BasicHubTest):
    def testRegistration(self):
        # check for notFoundError
        self.assertRaises(NotFoundError, self.object_hub.unregister, self.location)
        self.assertRaises(NotFoundError, self.object_hub.unregister, 42)

        ruid = self.object_hub.register(self.location)
        ruid2 = self.object_hub.register(self.new_location)

        self.subscriber.verifyEventsReceived(self, [
                (IRuidObjectRegisteredEvent, ruid, self.location),
                (IRuidObjectRegisteredEvent, ruid2, self.new_location)
            ])

        # register again and check for error
        self.assertRaises(ObjectHubError, self.object_hub.register, self.location)

        # unregister first object by location
        self.object_hub.unregister(self.location)
        self.subscriber.verifyEventsReceived(self, [
                (IRuidObjectUnregisteredEvent, ruid, self.location)
            ])
        # unregister second object by ruid
        self.object_hub.unregister(ruid2)
        self.subscriber.verifyEventsReceived(self, [
                (IRuidObjectUnregisteredEvent, ruid2, self.new_location)
            ])



        
class TestNoRegistration(BasicHubTest):
            
    def testAddWithoutRegistration(self):
        """Test that no RuidEvents are generated
        
        if there is no registration
        """
        hub = self.object_hub
        event = self.added_event
        location = self.location
        
        hub.notify(event)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
            ])


class TestObjectAddedEvent(BasicHubTest):
    def setUp(self):
        self.object_hub = ObjectHub()
        self.setEvents()
        self.subscriber = RegistrationSubscriber(self.object_hub)
        self.object_hub.subscribe(self.subscriber)
            
    def testLookingUpLocation(self):
        """Test that the location is in the lookup
        
        Compare getRuidForLocation and getLocationForRuid

        Checks the sequence of events
        
        """
        hub = self.object_hub
        event = self.added_event
        location = self.location
        
        hub.notify(event)
        
        ruid = hub.lookupRuid(location)
        # check that ruid is an int
        int(ruid)
        
        location_from_hub = hub.lookupLocation(ruid)

        self.assertEqual(location_from_hub, location)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IRuidObjectRegisteredEvent, ruid, location),
                (IRuidObjectAddedEvent, ruid, location),
            ])

        
    def testLookupUpAbsentLocation(self):
        """Test that we don't find an ruid for location
           that we haven't added.
        """
        hub = self.object_hub
        event = self.added_event
        location = self.location
        
        # Do not add the location to the hub
        # hub.notify(event)
        
        self.assertRaises(NotFoundError, hub.lookupRuid, location)

        self.subscriber.verifyEventsReceived(self, [])


        
    def testLookupUpAbsentRuid(self):
        """Test that we don't find a location for an ruid
           that isn't there.
        """
        hub = self.object_hub
        event = self.added_event
        
        # Do not add the location to the hub
        # hub.notify(event)
        
        absent_ruid = 12
        
        self.assertRaises(NotFoundError, hub.lookupLocation, absent_ruid)
        
        self.subscriber.verifyEventsReceived(self, [])

    


class TestObjectRemovedEvent(BasicHubTest):
    def setUp(self):
        self.object_hub = ObjectHub()
        self.setEvents()
        self.subscriber = RegistrationSubscriber(self.object_hub)
        self.object_hub.subscribe(self.subscriber)
          
    def testRemovedLocation(self):
        """Test that a location that is added then removed is
           actually gone.        
        """
        hub = self.object_hub
        added_event = self.added_event
        removed_event = self.removed_event
        location = self.location
        obj = self.obj
        
        hub.notify(added_event)
        
        ruid = hub.lookupRuid(location)
        
        # check that ruid is an int
        int(ruid)
        
        hub.notify(removed_event)
        
        self.assertRaises(NotFoundError, hub.lookupRuid, location)
        self.assertRaises(NotFoundError, hub.lookupLocation, ruid)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IRuidObjectRegisteredEvent, ruid, location),
                (IRuidObjectAddedEvent, ruid, location),
                (IObjectRemovedEvent, location),
                (IRuidObjectRemovedEvent, ruid, location, obj),
                (IRuidObjectUnregisteredEvent, ruid, location),
            ])
        
        
    def testRemovedAbsentLocation(self):
        """Test that removing an absent location is silently ignored.
        """
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
        self.object_hub = ObjectHub()
        self.setEvents()
        self.subscriber = RegistrationSubscriber(self.object_hub)
        self.object_hub.subscribe(self.subscriber)

    def testModifiedLocation(self):
        """Test that lookup state does not change after an object
        modify event.
        """
        hub = self.object_hub
        added_event = self.added_event
        modified_event = self.modified_event
        location = self.location
        
        hub.notify(added_event)
        
        ruid = hub.lookupRuid(location)
        # check that ruid is an int
        int(ruid)
        
        location_from_hub = hub.lookupLocation(ruid)
        self.assertEqual(location_from_hub, location)
        
        hub.notify(modified_event)
        
        ruid2 = hub.lookupRuid(location)
        location_from_hub2 = hub.lookupLocation(ruid2)
        
        self.assertEqual(location_from_hub, location_from_hub2)
        self.assertEqual(ruid, ruid2)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IRuidObjectRegisteredEvent, ruid, location),
                (IRuidObjectAddedEvent, ruid, location),
                (IObjectModifiedEvent, location),
                (IRuidObjectModifiedEvent, ruid, location)
            ])

        
    def testModifiedAbsentLocation(self):
        """Test that lookup state does not change after an object
        modify event. In this case, modify of an absent location is
        a noop.
        """
        hub = self.object_hub
        added_event = self.added_event
        modified_event = self.modified_event
        location = self.location
        
        # Do not add location
        # hub.notify(added_event)
        
        hub.notify(modified_event)
        self.assertRaises(NotFoundError, hub.lookupRuid, location)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectModifiedEvent, location),
            ])


class TestObjectMovedEvent(BasicHubTest):
    def setUp(self):
        self.object_hub = ObjectHub()
        self.setEvents()
        self.subscriber = RegistrationSubscriber(self.object_hub)
        self.object_hub.subscribe(self.subscriber)

    def testMovedLocation(self):
        """Test that the location does indeed change after a move.
        """
        hub = self.object_hub
        added_event = self.added_event
        moved_event = self.moved_event
        location = self.location
        new_location = self.new_location
        
        hub.notify(added_event)
        ruid = hub.lookupRuid(location)
        
        hub.notify(moved_event)
        
        location_from_hub = hub.lookupLocation(ruid)
                
        self.assertEqual(location_from_hub, new_location)
        self.assertRaises(NotFoundError, hub.lookupRuid, location)
                
        ruid2 = hub.lookupRuid(new_location)
        self.assertEqual(ruid2, ruid)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectAddedEvent, location),
                (IRuidObjectRegisteredEvent, ruid, location),
                (IRuidObjectAddedEvent, ruid, location),
                (IObjectMovedEvent, new_location),
                (IRuidObjectContextChangedEvent, ruid, new_location)
            ])


    def testMovedAbsentLocation(self):
        """Test that moving an absent location is a noop.
        """
        hub = self.object_hub
        added_event = self.added_event
        moved_event = self.moved_event
        location = self.location
        new_location = self.new_location
        
        # Do not add location
        # hub.notify(added_event)
        
        hub.notify(moved_event)
        self.assertRaises(NotFoundError, hub.lookupRuid, location)
        self.assertRaises(NotFoundError, hub.lookupRuid, new_location)
        
        self.subscriber.verifyEventsReceived(self, [
                (IObjectMovedEvent, new_location),
                ])


    def testMovedToExistingLocation(self):
        """Test that moving to an existing location raises ObjectHubError.
        """
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
                (IRuidObjectRegisteredEvent, None, location),
                (IRuidObjectAddedEvent, None, location),
                (IObjectAddedEvent, new_location),
                (IRuidObjectRegisteredEvent, None, new_location),
                (IRuidObjectAddedEvent, None, new_location),
                (IObjectMovedEvent, new_location),
            ])
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TransmitRuidObjectAddedEventTest),
        unittest.makeSuite(TransmitRuidObjectRemovedEventTest),
        unittest.makeSuite(TransmitRuidObjectModifiedEventTest),
        unittest.makeSuite(TransmitRuidObjectContextChangedEventTest),
        unittest.makeSuite(TransmitRuidObjectRegisteredEventTest),
        unittest.makeSuite(TransmitRuidObjectUnregisteredEventTest),
        unittest.makeSuite(TestRegistrationEvents),
        unittest.makeSuite(TestNoRegistration),
        unittest.makeSuite(TestObjectAddedEvent),
        unittest.makeSuite(TestObjectRemovedEvent),
        unittest.makeSuite(TestObjectModifiedEvent),
        unittest.makeSuite(TestObjectMovedEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
