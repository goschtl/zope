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
$Id: test_eventpublisher.py,v 1.10 2004/03/03 10:38:42 philikon Exp $
"""
import unittest

from zope.app.event.interfaces import IObjectEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.app.event.globalservice import GlobalEventPublisher
from zope.exceptions import NotFoundError
from zope.app.event.interfaces import IEvent
from zope.component.tests.placelesssetup import PlacelessSetup

from zope.app.event.tests.subscriber import DummySubscriber, DummyFilter
from zope.interface import implements

class DummyEvent:

    implements(IObjectAddedEvent, IObjectRemovedEvent)
    object = None

class ObjectEvent:

    implements(IObjectEvent)
    object = None

class TestEventService(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestEventService, self).setUp()
        self.service = GlobalEventPublisher()
        parent = object()
        self.event = ObjectAddedEvent(None, parent, 'foo')
        self.subscriber = DummySubscriber()

    def testSubscribe1(self):
        # Test subscribe method with one parameter
        self.service.globalSubscribe(self.subscriber)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe2(self):
        # Test subscribe method with two parameters
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe3(self):
        # Test subscribe method with three parameters
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe4(self):
        # Test subscribe method with three parameters and an always failing
        # filter.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 0)

    def testSubscribe5(self):
        # Test subscribe method with three parameters and an irrelevent event
        # type.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectModifiedEvent,
            filter=DummyFilter()
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 0)

    def testSubscribe6(self):
        # Test subscribe method where the event type registered is a
        # generalised interface of the event passed to the 'publish' method.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectEvent
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe7(self):
        # Test subscribe method where one of the event types registered is not
        # interested in the published event.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectModifiedEvent
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testSubscribe8(self):
        # Test subscribe method where the same subscriber subscribes multiple
        # times.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 2)

    def testUnsubscribe1(self):
        # Test unsubscribe method
        subscriber = self.subscriber
        self.service.globalSubscribe(subscriber)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)
        self.service.unsubscribe(subscriber)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testUnsubscribe2(self):
        # Test unsubscribe of something that hasn't been subscribed
        subscriber = self.subscriber
        self.assertRaises(NotFoundError,
                          self.service.unsubscribe,
                          subscriber, IObjectEvent)
        self.assertEqual(None,
                         self.service.unsubscribe(subscriber))

    def testUnsubscribe3(self):
        # Test selective unsubscribe
        subscriber2=DummySubscriber()
        filter=DummyFilter()
        event2=ObjectModifiedEvent(None)
        self.service.globalSubscribe(
            self.subscriber)
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            filter=filter
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.globalSubscribe(
            subscriber2,
            event_type=IObjectAddedEvent
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 3)
        self.assertEqual(subscriber2.notified, 1)
        self.service.publish(event2)
        self.assertEqual(self.subscriber.notified, 4)
        self.assertEqual(subscriber2.notified, 1)
        self.service.unsubscribe(self.subscriber, IObjectAddedEvent)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        self.service.unsubscribe(self.subscriber, IEvent)
        self.service.publish(event2)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        self.assertRaises(NotFoundError, self.service.unsubscribe,
                          self.subscriber, IObjectAddedEvent)
        self.service.unsubscribe(self.subscriber, IObjectAddedEvent, filter)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 3)
        self.service.unsubscribe(subscriber2, IObjectAddedEvent)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 3)

    def testpublish1(self):
        # Test publish method
        subscriber = self.subscriber
        self.service.globalSubscribe(subscriber)
        self.assertEqual(self.subscriber.notified, 0)
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 1)

    def testpublish2(self):
        # Test publish method where subscriber has been subscribed twice, with
        # a more generalised version of the initially subscribed interface in
        # the second subscription.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectEvent,
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent,
            )
        self.service.publish(self.event)
        self.assertEqual(self.subscriber.notified, 2)

    def testpublish3(self):
        # Test publish method where subscriber has been to two interfaces and
        # a single event implements both of those interfaces.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectRemovedEvent
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publish(DummyEvent())
        self.assertEqual(self.subscriber.notified, 2)

    def testpublish4(self):
        # Test publish method to make sure that we don't 'leak registrations
        # up' sez Jim.
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectEvent
            )
        self.service.globalSubscribe(
            self.subscriber,
            event_type=IObjectAddedEvent
            )
        self.service.publish(ObjectEvent())
        self.assertEqual(self.subscriber.notified, 1)

    def testListSubscriptions1(self):
        # a non-subscribed subscriber gets an empty array
        self.assertEqual([], self.service.listSubscriptions(self.subscriber))

    def testListSubscriptions2(self):
        # one subscription
        self.service.globalSubscribe(
                self.subscriber, event_type=IObjectAddedEvent)
        self.assertEqual([(IObjectAddedEvent, None)],
                         self.service.listSubscriptions(self.subscriber))

    def testListSubscriptions3(self):
        # listing limited subscription
        self.service.globalSubscribe(
                self.subscriber, event_type=IObjectAddedEvent)
        L = self.service.listSubscriptions(self.subscriber,
                                           IObjectRemovedEvent)
        self.assertEqual([], L)


def test_suite():
    return unittest.makeSuite(TestEventService)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
