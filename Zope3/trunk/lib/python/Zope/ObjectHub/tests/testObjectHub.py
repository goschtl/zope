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
$Id: testObjectHub.py,v 1.2 2002/06/10 23:29:29 jim Exp $
"""

import unittest, sys

from Zope.Event.ObjectEvent import ObjectAddedEvent, ObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectRemovedEvent, ObjectMovedEvent
from Zope.Event.ISubscriber import ISubscriber

from Zope.ObjectHub.ObjectHub import ObjectHub, ObjectHubError
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectAddedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectRemovedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectModifiedEvent
from Zope.ObjectHub.IRuidObjectEvent import IRuidObjectContextChangedEvent

from Zope.Exceptions import NotFoundError
from types import StringTypes

class LoggingSubscriber:

    __implements__ = ISubscriber
    
    def __init__(self):
        self.events_received = []
    
    def notify(self, event):
        self.events_received.append(event)


    # see ObjectHub._canonical
    def _canonical(location):
        """ returns a canonical traversal location for a location that is 
        a string or a sequence of strings """
        if not isinstance(location, StringTypes):
            location='/'.join(location)
        # URIs are ascii, right?
        return str(location)
    _canonical = staticmethod(_canonical)
    
    def verifyEventsReceived(self, testcase, event_spec_list):
        # iterate through self.events_received and check
        # that each one implements the interface that is
        # in the same place, with the same location and ruid
        
        testcase.assertEqual(len(event_spec_list), len(self.events_received))
        
        for spec,event in zip(event_spec_list, self.events_received):
            if len(spec)==4:
                interface,ruid,location,obj = spec
            else:
                interface,ruid,location = spec
                obj = None
            location = self._canonical(location)
            testcase.assert_(interface.isImplementedBy(event))
            testcase.assertEqual(event.getLocation(), location)
            
            if obj is not None:
                testcase.assertEqual(event.getObject(), obj)
            
            # Sometimes, the test won't care about the ruid. In this case,
            # it is passed into the spec as None.
            if ruid is not None:
                testcase.assertEqual(event.getRuid(), ruid)
            
    
class BasicHubTest(unittest.TestCase):

    location = '/foo/bar'
    obj = object()
    new_location = '/baz/spoo'
    
    def setUp(self):
        self.added_event = ObjectAddedEvent(self.location)
        self.added_new_location_event = ObjectAddedEvent(self.new_location)
        self.removed_event = ObjectRemovedEvent(self.location, self.obj)
        self.modified_event = ObjectModifiedEvent(self.location)
        self.moved_event = ObjectMovedEvent(self.location,
                                            self.new_location)
        self.object_hub = ObjectHub()
        self.subscriber = LoggingSubscriber()
        self.object_hub.subscribe(self.subscriber)

        # TODO: test that ObjectHub acts as an EventChannel


class TestObjectAddedEvent(BasicHubTest):
            
    def testLookingUpLocation(self):
        """Test that the location is in the lookup
        
        Compare getRuidForLocation and getLocationForRuid
        
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
                (IRuidObjectAddedEvent, ruid, location)
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
                (IRuidObjectAddedEvent, ruid, location),
                (IRuidObjectRemovedEvent, ruid, location, obj)
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

        self.subscriber.verifyEventsReceived(self, [])
                

class TestObjectModifiedEvent(BasicHubTest):

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
                (IRuidObjectAddedEvent, ruid, location),
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
        
        self.subscriber.verifyEventsReceived(self, [])


class TestObjectMovedEvent(BasicHubTest):

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
                (IRuidObjectAddedEvent, ruid, location),
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
        
        self.subscriber.verifyEventsReceived(self, [])


    def testMovedToExistingLocation(self):
        """Test that moving to an existing location raises ObjectHubError.
        """
        hub = self.object_hub
        added_event2 = self.added_new_location_event
        moved_event = self.moved_event
        location = self.new_location
        
        hub.notify(added_event2)
        
        self.assertRaises(ObjectHubError, hub.notify, moved_event)
        
        self.subscriber.verifyEventsReceived(self, [
                (IRuidObjectAddedEvent, None, location)
            ])
        

        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectAddedEvent),
        unittest.makeSuite(TestObjectRemovedEvent),
        unittest.makeSuite(TestObjectModifiedEvent),
        unittest.makeSuite(TestObjectMovedEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
