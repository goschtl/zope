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
$Id: testEventService.py,v 1.4 2002/10/03 20:53:22 jim Exp $
"""

import unittest, sys
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.Event.IObjectEvent import IObjectEvent
from Zope.Event.IObjectEvent import IObjectAddedEvent
from Zope.Event.IObjectEvent import IObjectRemovedEvent
from Zope.Event.IObjectEvent import IObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent, ObjectModifiedEvent
from Zope.Event.GlobalEventService import GlobalEventService
from Zope.Exceptions import NotFoundError
from Zope.Event.IEvent import IEvent

from subscriber import DummySubscriber, DummyFilter

class DummyEvent:

    __implements__ = IObjectAddedEvent, IObjectRemovedEvent

class ObjectEvent:

    __implements__ = IObjectEvent
    
class TestEventService(CleanUp, unittest.TestCase):

    def setUp(self):
        CleanUp.setUp(self)
        self.service = GlobalEventService()
        self.event = ObjectAddedEvent(None, '/foo')
        self.subscriber = DummySubscriber()
        
    def testSubscribe1(self):
        "Test subscribe method with one parameter"
        self.service.subscribe(self.subscriber)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)
        
    def testSubscribe2(self):
        "Test subscribe method with two parameters"
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe3(self):
        "Test subscribe method with three parameters"
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe4(self):
        """Test subscribe method with three parameters
        and an always failing filter.
        """
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 0)

    def testSubscribe5(self):
        """Test subscribe method with three parameters
        and an irrelevent event type.
        """
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectModifiedEvent,
            filter=DummyFilter()
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 0)

    def testSubscribe6(self):
        """Test subscribe method where the event type
        registered is a generalised interface of the
        event passed to the 'publishEvent' method.
        """
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectEvent
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe7(self):
        """Test subscribe method where one of the
        event types registered is not interested in
        the publishEvented event.
        """
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectModifiedEvent
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe8(self):
        """Test subscribe method where the same subscriber
        subscribes multiple times. 
        """
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 2)

    def testUnsubscribe1(self):
        "Test unsubscribe method"
        subscriber = self.subscriber
        self.service.subscribe(subscriber)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)
        self.service.unsubscribe(subscriber)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testUnsubscribe2(self):
        "Test unsubscribe of something that hasn't been subscribed"
        subscriber = self.subscriber
        self.assertRaises(NotFoundError,
                          self.service.unsubscribe,
                          subscriber, IObjectEvent)
        self.assertEqual(None,
                         self.service.unsubscribe(subscriber))
    
    def testUnsubscribe3(self):
        "Test selective unsubscribe"
        subscriber2=DummySubscriber()
        filter=DummyFilter()
        event2=ObjectModifiedEvent(None, '/foo')
        self.service.subscribe(
            self.subscriber)
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=filter
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.subscribe(
            subscriber2,
            event_type=IObjectAddedEvent
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 3)
        self.assertEqual(subscriber2.notified, 1)
        self.service.publishEvent(event2)
        self.assertEqual(self.subscriber.notified, 4)
        self.assertEqual(subscriber2.notified, 1)
        self.service.unsubscribe(self.subscriber, IObjectAddedEvent)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        self.service.unsubscribe(self.subscriber, IEvent)
        self.service.publishEvent(event2)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        self.assertRaises(NotFoundError, self.service.unsubscribe,
                          self.subscriber, IObjectAddedEvent)
        self.service.unsubscribe(self.subscriber, IObjectAddedEvent, filter)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 3)
        self.service.unsubscribe(subscriber2, IObjectAddedEvent)
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 3)

    def testpublishEvent1(self):
        "Test publishEvent method"
        subscriber = self.subscriber
        self.service.subscribe(subscriber)
        self.assertEqual(self.subscriber.notified, 0)        
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testpublishEvent2(self):
        """Test publishEvent method where subscriber has been
        subscribed twice, with a more generalised
        version of the initially subscribed interface
        in the second subscription.
        """
        subscriber = self.subscriber
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectEvent,
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            )
        self.service.publishEvent(self.event)
        self.assertEqual(self.subscriber.notified, 2) 

    def testpublishEvent3(self):
        """Test publishEvent method where subscriber has been
        to two interfaces and a single event implements both
        of those interfaces.
        """
        subscriber = self.subscriber
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectRemovedEvent
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publishEvent(DummyEvent())
        self.assertEqual(self.subscriber.notified, 2)

    def testpublishEvent4(self):
        """Test publishEvent method to make sure that we don't
        'leak registrations up' sez Jim.
        """
        subscriber = self.subscriber
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectEvent
            )
        self.service.subscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publishEvent(ObjectEvent())
        self.assertEqual(self.subscriber.notified, 1)
    
    def testListSubscriptions1(self):
        "a non-subscribed subscriber gets an empty array"
        self.assertEqual([], self.service.listSubscriptions(self.subscriber))
    
    def testListSubscriptions2(self):
        "one subscription"
        self.service.subscribe(self.subscriber, event_type=IObjectAddedEvent)
        self.assertEqual([(IObjectAddedEvent, None)],
                         self.service.listSubscriptions(self.subscriber))
    
    def testListSubscriptions3(self):
        "listing limited subscription"
        self.service.subscribe(self.subscriber, event_type=IObjectAddedEvent)
        L = self.service.listSubscriptions(self.subscriber,
                                           IObjectRemovedEvent)
        self.assertEqual([], L)
    
def test_suite():
    return unittest.makeSuite(TestEventService)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
