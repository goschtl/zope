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
$Id: test_localservice.py,v 1.5 2004/03/13 23:55:00 srichter Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner

import zope.interface
from zope.interface import Interface, implements
from zope.exceptions import NotFoundError
from zope.component.tests.components import RecordingAdapter

from zope.app.servicenames import EventPublication, EventSubscription
from zope.app.event.localservice import EventService
from zope.app.event.localservice import subscribe, unsubscribe, unsubscribeAll
from zope.app.event.localservice import getSubscriptionService

from zope.app.event import publish
from zope.app.event.tests.subscriber import DummySubscriber, DummyFilter
from zope.app.event.interfaces import IObjectEvent, IObjectModifiedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.interfaces import IEvent, ISubscriber, ISubscribingAware

from zope.app.traversing import getPath, traverse
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.app.container.contained import ObjectAddedEvent, Contained
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.site.interfaces import ISimpleService
from zope.app.tests import ztapi, setup
from eventsetup import EventSetup

class Folder(Contained):
    pass

root = Folder()
zope.interface.directlyProvides(root, IContainmentRoot)
foo = Folder()
foo.__parent__ = root
foo.__name__ = 'foo'
                                

class UnpromotingEventService(EventService):

    def isPromotableEvent(self, event):
        "see EventService implementation"
        return False

class DummyEvent:

    implements(IObjectAddedEvent, IObjectRemovedEvent)
    object = None

class ObjectEvent:

    implements(IObjectEvent)
    object = None

class IObjectHub(Interface):
    def getObject(hubid):
        "gets object"

    def getHubId(object):
        "gets hubid"

    def getLocation(hubId):
        "gets location"

class DumbObjectHub:
    implements(IObjectHub, ISimpleService)

    __name__ = __parent__ = None
    
    def __init__(self):
        # (location, object)
        self.lib = []

    def getObject(self, hubid):
        try:
            return self.lib[hubid][1]
        except IndexError:
            raise NotFoundError

    def getHubId(self, object_or_path):
        for i in range(len(self.lib)):
            if self.lib[i][0] == object_or_path:
                return i
            if self.lib[i][1] is object_or_path:
                return i
        raise NotFoundError, object_or_path

    def getLocation(self, hubId):
        return self.lib[hubId][0]

class IHasSubscribingAwareAdapter(Interface):
    pass

class HasSubscribingAwareAdapter(DummySubscriber):
    implements(IHasSubscribingAwareAdapter, ISubscriber)


class SubscribingAwareAdapter(RecordingAdapter):

    implements(ISubscribingAware)

    def subscribedTo(self, subscribable, event_type, filter):
        self.record.append(('subscribed', self.context, subscribable,
                            event_type, filter))

    def unsubscribedFrom(self, subscribable, event_type, filter):
        self.record.append(('unsubscribed', self.context, subscribable,
                            event_type, filter))


class TestEventPublisher(EventSetup, TestCase):

    def setUp(self):
        EventSetup.setUp(self)

    def getObjectHub(self):
        self.objectHub = DumbObjectHub()
        return self.objectHub

    def _createNestedServices(self):
        for path in ('folder1', 'folder1/folder1_1',
                     'folder1/folder1_1/folder1_1_1'):
            sm = self.makeSite(path)
            events = EventService()
            setup.addService(sm, EventPublication, events)
            setup.addService(sm, EventSubscription, events, suffix='s')

    def _createSubscribers(self):
        self.rootFolder["rootFolderSubscriber"] = DummySubscriber()
        self.rootFolderSubscriber = self.rootFolder["rootFolderSubscriber"]
        self.folder1["folder1Subscriber"] = DummySubscriber()
        self.folder1Subscriber = self.folder1["folder1Subscriber"]
        self.folder1_1["folder1_1Subscriber"] = DummySubscriber()
        self.folder1_1Subscriber = self.folder1_1["folder1_1Subscriber"]

    def _createHubIdSubscribers(self):
        self._createSubscribers()
        self.objectHub.lib = [
        ('/rootFolderSubscriber', self.rootFolderSubscriber),
        ('/folder1/folder1Subscriber', self.folder1Subscriber),
        ('/folder1/folder1_1/folder1_1Subscriber', self.folder1_1Subscriber)
        ]
        self.rootSubscriberHubId = 0
        self.folder1SubscriberHubId = 1
        self.folder1_1SubscriberHubId = 2

    def testCreateNestedServices(self):
        self._createNestedServices()

    def testByPath(self):
        # test complex interaction, with no hubids available
        self._createSubscribers()
        root = subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        folder1 = subscribe(self.folder1Subscriber,
                            event_type=IObjectAddedEvent)
        folder1_1 = subscribe(self.folder1_1Subscriber,
                              event_type=IObjectAddedEvent)
        self.assertEqual(root, getPath(self.rootFolderSubscriber))
        self.assertEqual(folder1, getPath(self.folder1Subscriber))
        self.assertEqual(folder1_1, getPath(self.folder1_1Subscriber))
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        rootPath = getPath(self.rootFolderSubscriber)
        folder1Path = getPath(self.folder1Subscriber)
        folder1_1Path = getPath(self.folder1_1Subscriber)
        unsubscribeAll(rootPath, context=self.rootFolder)
            # curve ball:
        unsubscribeAll(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(folder1_1Path,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def testByHubId(self):
        # test complex interaction, with hubids available
        self._createHubIdSubscribers()
        root = subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        folder1 = subscribe(self.folder1Subscriber,
                            event_type=IObjectAddedEvent)
        folder1_1 = subscribe(self.folder1_1Subscriber,
                              event_type=IObjectAddedEvent)
        self.assertEqual(
            self.objectHub.lib[self.rootSubscriberHubId],
            ('/rootFolderSubscriber', self.rootFolderSubscriber)
            )
        self.assertEqual(
            self.objectHub.lib[self.folder1SubscriberHubId],
            ('/folder1/folder1Subscriber', self.folder1Subscriber)
            )
        self.assertEqual(
            self.objectHub.lib[self.folder1_1SubscriberHubId],
            ('/folder1/folder1_1/folder1_1Subscriber',
             self.folder1_1Subscriber)
            )
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        unsubscribe(getPath(self.rootFolderSubscriber),
                    event_type=IObjectAddedEvent,
                    context=self.rootFolder)
        subscribe(self.rootFolderSubscriber,
                  event_type=IObjectAddedEvent)
        unsubscribeAll(self.rootSubscriberHubId, context=self.rootFolder)
        # curve balls:
        unsubscribeAll(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(2,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(None, 'fauxparent', 'foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def testBadSubscriber(self):
        self._createSubscribers()
        root = subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        folder1 = subscribe(self.folder1Subscriber,
                            event_type=IObjectAddedEvent)
        folder1_1 = subscribe(self.folder1_1Subscriber,
                              event_type=IObjectAddedEvent)
        self.assertEqual(root, getPath(self.rootFolderSubscriber))
        self.assertEqual(folder1, getPath(self.folder1Subscriber))
        self.assertEqual(folder1_1, getPath(self.folder1_1Subscriber))
        # Remove folder1Subscriber, so that the event service will not
        # be able to notify it.
        folder1Subscriber = self.folder1['folder1Subscriber']
        del self.folder1['folder1Subscriber']

        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 0)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

        # Now, put folder1Subscriber back. This incidentally fires off a
        # ObjectAddedEvent, since self.folder1 is decorated with a context
        # decorator.
        self.folder1['folder1Subscriber'] = folder1Subscriber
        self.assertEqual(self.rootFolderSubscriber.notified, 2)
        self.assertEqual(self.folder1Subscriber.notified, 0)
        self.assertEqual(self.folder1_1Subscriber.notified, 2)

        # folder1Subscriber should not be notified now, because it was removed
        # as a bad subscriber.
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 3)
        self.assertEqual(self.folder1Subscriber.notified, 0)
        self.assertEqual(self.folder1_1Subscriber.notified, 3)

    def testByPathExplicit(self):
        # test complex interaction, with hubids available but explicitly
        # using paths
        self._createHubIdSubscribers()
        rootPath = getPath(self.rootFolderSubscriber)
        folder1Path = getPath(self.folder1Subscriber)
        folder1_1Path = getPath(self.folder1_1Subscriber)
        self.assertEqual(
            rootPath,
            subscribe(
                rootPath,
                event_type=IObjectAddedEvent,
                context=self.rootFolder))
        self.assertEqual(
            folder1Path,
            subscribe(
                folder1Path,
                event_type=IObjectAddedEvent,
                context=self.folder1))
        self.assertEqual(
            folder1_1Path,
            subscribe(
                folder1_1Path,
                event_type=IObjectAddedEvent,
                context=self.folder1_1))
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        unsubscribeAll(rootPath, context=self.rootFolder)
        # curve balls:
        unsubscribeAll(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(2, event_type=IObjectAddedEvent, context=self.folder1_1)
        subscribe(2, event_type=IObjectAddedEvent, context=self.folder1_1)

        # this is supposed to unsubscribe '2'
        unsubscribe(folder1_1Path,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def testByHubIdExplicit(self):
        # test complex interaction, with hubids available and explicitly
        # using them
        self._createHubIdSubscribers()
        root = subscribe(
            0,
            event_type=IObjectAddedEvent,
            context = self.folder1_1
            )
        folder1 = subscribe(1,
                            event_type=IObjectAddedEvent,
                            context = self.folder1)
        folder1_1 = subscribe(2,
                              event_type=IObjectAddedEvent,
                              context = self.rootFolder)
        self.assertEqual(
            self.objectHub.lib[root],
            ('/rootFolderSubscriber', self.rootFolderSubscriber)
            )
        self.assertEqual(
            self.objectHub.lib[folder1],
            ('/folder1/folder1Subscriber', self.folder1Subscriber)
            )
        self.assertEqual(
            self.objectHub.lib[folder1_1],
            ('/folder1/folder1_1/folder1_1Subscriber',
             self.folder1_1Subscriber)
            )
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        unsubscribe(getPath(self.rootFolderSubscriber),
                    event_type=IObjectAddedEvent,
                    context=self.rootFolder)
        subscribe(self.rootFolderSubscriber, event_type=IObjectAddedEvent,
                  context=self.rootFolder)
        unsubscribeAll(root, context=self.rootFolder)
        # curve ball:
        unsubscribeAll(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(2,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def _testIterSubscriptions1(self):
        # a non-subscribed subscriber gets an empty array
        events = getSubscriptionService(self.rootFolder)

        self.assertEqual(
            [x for x in events.iterSubscriptions(self.rootFolderSubscriber)],
            [])

    def testPathIterSubscriptions1(self):
        self._createSubscribers()
        self._testIterSubscriptions1()

    def testHubIdIterSubscriptions1(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions1()

    def _testIterSubscriptions2(self, subscription_type):
        # one subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        if subscription_type is int:
            reference = 0
        else:
            reference = u'/rootFolderSubscriber'
        events = getSubscriptionService(self.rootFolder)
        self.assertEqual(
            [x for x in events.iterSubscriptions(self.rootFolderSubscriber)],
            [(reference, IObjectAddedEvent, None)]
            )

    def testPathIterSubscriptions2(self):
        self._createSubscribers()
        self._testIterSubscriptions2(unicode)

    def testHubIdIterSubscriptions2(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions2(int)

    def _testIterSubscriptions3(self):
        # listing limited subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual(
            [],
            [x for x in getSubscriptionService(self.rootFolder)
            .iterSubscriptions(self.rootFolderSubscriber, IObjectRemovedEvent)]
            )

    def testPathIterSubscriptions3(self):
        self._createSubscribers()
        self._testIterSubscriptions3()

    def testHubIdIterSubscriptions3(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions3()

    def _testIterSubscriptions4(self):
        # a non-subscribed subscriber gets an empty array
        events = getSubscriptionService(self.rootFolder)

        self.assertEqual(
            [x for x in events.iterSubscriptions(self.rootFolderSubscriber)],
            [])

    def testPathIterSubscriptions4(self):
        self._createSubscribers()
        self._testIterSubscriptions4()

    def testHubIdIterSubscriptions4(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions4()

    def _testIterSubscriptions5(self, subscription_type):
        if subscription_type is int:
            reference = 0
        else:
            reference = u'/rootFolderSubscriber'
        # one subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual(
            [x for x in getSubscriptionService(self.rootFolder)
             .iterSubscriptions(self.rootFolderSubscriber)],
            [(reference, IObjectAddedEvent, None)]
            )

    def testPathIterSubscriptions5(self):
        self._createSubscribers()
        self._testIterSubscriptions5(unicode)

    def testHubIdIterSubscriptions5(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions5(int)

    def _testIterSubscriptions6(self):
        # listing limited subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual(
        [x for x in getSubscriptionService(self.rootFolder)
        .iterSubscriptions(self.rootFolderSubscriber, IObjectRemovedEvent)],
        []
        )

    def testPathIterSubscriptions6(self):
        self._createSubscribers()
        self._testIterSubscriptions6()

    def testHubIdIterSubscriptions6(self):
        self._createHubIdSubscribers()
        self._testIterSubscriptions6()

    def _testSubscribe1(self):
        # Test subscribe method with one parameter
        subscribe(self.rootFolderSubscriber)
        publish(self.rootFolder, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathSubscribe1(self):
        self._createSubscribers()
        self._testSubscribe1()

    def testHubIdSubscribe1(self):
        self._createHubIdSubscribers()
        self._testSubscribe1()

    def _testSubscribe2(self):
        # Test subscribe method with two parameters
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathSubscribe2(self):
        self._createSubscribers()
        self._testSubscribe2()

    def testHubIdSubscribe2(self):
        self._createHubIdSubscribers()
        self._testSubscribe2()

    def _testSubscribe3(self):
        # Test subscribe method with three parameters
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathSubscribe3(self):
        self._createSubscribers()
        self._testSubscribe3()

    def testHubIdSubscribe3(self):
        self._createHubIdSubscribers()
        self._testSubscribe3()

    def _testSubscribe4(self):
        # Test subscribe method with three parameters and an always failing
        # filter.
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testPathSubscribe4(self):
        self._createSubscribers()
        self._testSubscribe4()

    def testHubIdSubscribe4(self):
        self._createHubIdSubscribers()
        self._testSubscribe4()

    def _testSubscribe5(self):
        # Test subscribe method with three parameters and an irrelevent event
        # type.
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectModifiedEvent,
            filter=DummyFilter()
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testPathSubscribe5(self):
        self._createSubscribers()
        self._testSubscribe5()

    def testHubIdSubscribe5(self):
        self._createHubIdSubscribers()
        self._testSubscribe5()

    def _testSubscribe6(self):
        # Test subscribe method where the event type registered is a
        # generalised interface of the event passed to the 'publish' method.
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectEvent
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathSubscribe6(self):
        self._createSubscribers()
        self._testSubscribe6()

    def testHubIdSubscribe6(self):
        self._createHubIdSubscribers()
        self._testSubscribe6()

    def _testSubscribe7(self):
        # Test subscribe method where one of the event types registered is not
        # interested in the published event.
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectModifiedEvent
            )
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathSubscribe7(self):
        self._createSubscribers()
        self._testSubscribe7()

    def testHubIdSubscribe7(self):
        self._createHubIdSubscribers()
        self._testSubscribe7()

    def _testSubscribe8(self):
        # Test subscribe method where the same subscriber subscribes multiple
        # times.
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 2)

    def testPathSubscribe8(self):
        self._createSubscribers()
        self._testSubscribe8()

    def testHubIdSubscribe8(self):
        self._createHubIdSubscribers()
        self._testSubscribe8()

    def _testUnsubscribe1(self):
        # Test unsubscribe method
        subscribe(
            self.rootFolderSubscriber
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        unsubscribeAll(
            self.rootFolderSubscriber
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testPathUnsubscribe1(self):
        self._createSubscribers()
        self._testUnsubscribe1()

    def testHubIdUnsubscribe1(self):
        self._createHubIdSubscribers()
        self._testUnsubscribe1()

    def _testUnsubscribe2(self):
        # Test unsubscribe of something that hasn't been subscribed
        self.assertRaises(NotFoundError,
                          unsubscribe,
                          69,
                          IObjectEvent)
        unsubscribeAll(self.rootFolderSubscriber)

    def testPathUnsubscribe2(self):
        self._createSubscribers()
        self._testUnsubscribe2()

    def testHubIdUnsubscribe2(self):
        self._createHubIdSubscribers()
        self._testUnsubscribe2()

    def _testUnsubscribe3(self):
        # Test selective unsubscribe
        subscriber = self.rootFolderSubscriber
        subscriber2 = self.folder1Subscriber
        filter = DummyFilter()
        event = ObjectAddedEvent(foo)
        event2 = ObjectModifiedEvent(None)
        subscribe(
            subscriber)
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent,
            filter=filter
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            subscriber2,
            event_type=IObjectAddedEvent
            )
        publish(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 3)
        self.assertEqual(subscriber2.notified, 1)
        publish(self.folder1_1_1, event2)
        self.assertEqual(subscriber.notified, 4)
        self.assertEqual(subscriber2.notified, 1)
        unsubscribe(subscriber, IObjectAddedEvent)
        publish(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        unsubscribe(subscriber, IEvent)
        publish(self.folder1_1_1, event2)
        self.assertEqual(subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        publish(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 3)
        self.assertRaises(NotFoundError, unsubscribe, subscriber,
                          IObjectAddedEvent)
        unsubscribe(subscriber, IObjectAddedEvent, filter)
        publish(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 4)
        unsubscribe(subscriber2, IObjectAddedEvent)
        publish(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 4)

    def testPathUnsubscribe3(self):
        self._createSubscribers()
        self._testUnsubscribe3()

    def testHubIdUnsubscribe3(self):
        self._createHubIdSubscribers()
        self._testUnsubscribe3()

    def testPathUnsubscribe4(self):
        self._createNestedServices()
        self._createSubscribers()
        self._testUnsubscribe3()

    def testHubIdUnsubscribe4(self):
        self._createNestedServices()
        self._createHubIdSubscribers()
        self._testUnsubscribe3()

    def _testpublish1(self):
        # Test publish method
        subscriber = self.rootFolderSubscriber
        subscribe(subscriber)
        self.assertEqual(subscriber.notified, 0)
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(subscriber.notified, 1)

    def testPathPublish1(self):
        self._createSubscribers()
        self._testpublish1()

    def testHubIdPublish1(self):
        self._createHubIdSubscribers()
        self._testpublish1()

    def _testpublish2(self):
        # Test publish method where subscriber has been subscribed twice, with
        # a more generalised version of the initially subscribed interface in
        # the second subscription.
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectEvent,
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent,
            )
        publish(self.folder1_1_1, ObjectAddedEvent(foo))
        self.assertEqual(subscriber.notified, 2)

    def testPathPublish2(self):
        self._createSubscribers()
        self._testpublish2()

    def testHubIdPublish2(self):
        self._createHubIdSubscribers()
        self._testpublish2()

    def _testpublish3(self):
        # Test publish method where subscriber has been to two interfaces and
        # a single event implements both of those interfaces.
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectRemovedEvent
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent
            )
        publish(self.folder1_1_1, DummyEvent())
        self.assertEqual(subscriber.notified, 2)

    def testPathPublish3(self):
        self._createSubscribers()
        self._testpublish3()

    def testHubIdPublish3(self):
        self._createHubIdSubscribers()
        self._testpublish3()

    def _testpublish4(self):
        # Test publish method to make sure that we don't 'leak registrations
        # up' sez Jim.
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectEvent
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent
            )
        publish(self.folder1_1_1, ObjectEvent())
        self.assertEqual(subscriber.notified, 1)

    def testPathPublish4(self):
        self._createSubscribers()
        self._testpublish4()

    def testHubIdPublish4(self):
        self._createHubIdSubscribers()
        self._testpublish4()

    def _createAlternateService(self, service):
        self.folder2["folder2Subscriber"] = DummySubscriber()
        self.folder2Subscriber = self.folder2["folder2Subscriber"]

        sm = self.makeSite('folder2')
        setup.addService(sm, EventPublication, service);
        setup.addService(sm, EventSubscription, service, suffix='s');

        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.folder2Subscriber,
            event_type=IObjectAddedEvent
            )

    def testNonPromotingEventPublisher(self):
        # test to see if events are not passed on to a parent event service
        # with the appropriate isPromotableEvent setting
        self._createHubIdSubscribers()
        self._createAlternateService(UnpromotingEventService())
        publish(self.folder2, ObjectAddedEvent(foo))
        self.assertEqual(self.folder2Subscriber.notified, 1)
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testPromotingEventPublisher1(self):
        # test to see if events are passed on to a parent event service with
        # the appropriate isPromotableEvent setting
        self._createHubIdSubscribers()
        self._createAlternateService(EventService())
        publish(self.folder2, ObjectAddedEvent(foo))
        self.assertEqual(self.folder2Subscriber.notified, 1)
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testUnbindingResubscribing1(self):
        # an event service is unbound; a lower event service should then
        # rebind to upper event service
        self._createNestedServices()
        self._createHubIdSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.folder1Subscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.folder1_1Subscriber,
            event_type=IObjectAddedEvent
            )

        sm = traverse(self.rootFolder, "folder1/++etc++site")
        registration = sm.queryRegistrations(EventPublication).active()
        registration.status = RegisteredStatus
        publish(self.rootFolder, ObjectAddedEvent(foo))
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

        registration = sm.queryRegistrations(EventSubscription).active()
        registration.status = RegisteredStatus

        publish(self.rootFolder, ObjectAddedEvent(foo))
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 2)

    def testNoSubscribeOnBind(self):
        # if subscribeOnBind is 0, service should not subscribe to parent
        sv = EventService()
        sv.subscribeOnBind = 0
        self._createHubIdSubscribers()
        self._createAlternateService(sv)
        publish(self.rootFolder, ObjectAddedEvent(foo))
        self.assertEqual(self.folder2Subscriber.notified, 0)
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

        sm = traverse(self.rootFolder, "folder2/++etc++site")
        registration = sm.queryRegistrations(EventSubscription).active()
        # make sure it doesn't raise any errors
        registration.status = RegisteredStatus
        registration = sm.queryRegistrations(EventPublication).active()
        # make sure it doesn't raise any errors
        registration.status = RegisteredStatus

    def testSubscriptionAwareInteraction(self):
        adapter = SubscribingAwareAdapter()
        ztapi.provideAdapter(IHasSubscribingAwareAdapter,
                             ISubscribingAware,
                             adapter)
        self.rootFolder["mySubscriber"] = HasSubscribingAwareAdapter()
        self.mySubscriber = self.rootFolder["mySubscriber"]
        filter = DummyFilter()
        subscribe(
            self.mySubscriber,
            event_type=IObjectAddedEvent,
            filter=filter)
        adapter.check(
            ('subscribed',
             self.mySubscriber,
             getSubscriptionService(self.rootFolder),
             IObjectAddedEvent,
             filter
            )
        )
        #self.assertEqual(
        #    self.mySubscriber.subscribable,
        #    getEventService(self.rootFolder))
        #self.assertEqual(
        #    self.mySubscriber.subscribable,
        #    getSubscriptionService(self.rootFolder))
        #self.assertEqual(
        #    self.mySubscriber.event_type,
        #    IObjectAddedEvent)
        #self.assertEqual(
        #    self.mySubscriber.filter,
        #    filter)
        unsubscribe(
            self.mySubscriber,
            event_type=IObjectAddedEvent,
            filter=filter)
        adapter.check(
            ('subscribed',
             self.mySubscriber,
             getSubscriptionService(self.rootFolder),
             IObjectAddedEvent,
             filter
            ),
            ('unsubscribed',
             self.mySubscriber,
             getSubscriptionService(self.rootFolder),
             IObjectAddedEvent,
             filter
            )
        )



def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(TestEventPublisher)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
