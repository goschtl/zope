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
$Id: test_eventservice.py,v 1.6 2003/01/28 11:30:57 stevea Exp $
"""

from unittest import TestCase, TestLoader, TextTestRunner
from zope.interface import Interface
from zope.app.services.service import ServiceManager, ServiceConfiguration
from zope.component import getServiceManager
from zope.app.services.event import EventService
from zope.app.traversing import getPhysicalPathString, traverse
from zope.exceptions import NotFoundError
from zope.app.services.event import subscribe, unsubscribe
from zope.app.services.event import listSubscriptions, getSubscriptionService
from zope.app.event import getEventService, publish
from zope.app.event.tests.subscriber import DummySubscriber, DummyFilter
from zope.app.interfaces.event import IObjectEvent, IObjectModifiedEvent
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectAddedEvent
from zope.app.interfaces.event import ISubscriber
from zope.app.event.objectevent import ObjectAddedEvent, ObjectModifiedEvent
from zope.app.event.globalservice import GlobalEventPublisher
from zope.app.interfaces.event import IEvent, ISubscribingAware
from zope.app.interfaces.services.configuration import Active
from zope.app.interfaces.services.configuration import Unregistered
from zope.app.interfaces.services.configuration import Registered
from zope.proxy.context import ContextWrapper
from zope.app.services.tests.eventsetup import EventSetup
from zope.component.tests.components import RecordingAdapter
from zope.component.adapter import provideAdapter

class UnpromotingEventService(EventService):

    def isPromotableEvent(self, event):
        "see EventService implementation"
        return False

class DummyEvent:

    __implements__ = IObjectAddedEvent, IObjectRemovedEvent

class ObjectEvent:

    __implements__ = IObjectEvent

class IObjectHub(Interface):
    def getObject(hubid):
        "gets object"

    def getHubId(object):
        "gets hubid"

class DumbObjectHub:
    __implements__ = IObjectHub

    def __init__(self):
        self.lib = []

    def getObject(self, hubid):
        try:
            return self.lib[hubid]
        except IndexError:
            raise NotFoundError

    def getHubId(self, object):
        for i in range(len(self.lib)):
            if self.lib[i] is object:
                return i
        raise NotFoundError

class IHasSubscribingAwareAdapter(Interface):
    pass

class HasSubscribingAwareAdapter(DummySubscriber):
    __implements__ = IHasSubscribingAwareAdapter, ISubscriber


class SubscribingAwareAdapter(RecordingAdapter):

    __implements__ = ISubscribingAware

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
        self.createEventService('folder1')
        self.createEventService('folder1/folder1_1')
        self.createEventService('folder1/folder1_1/folder1_1_1')

    def _createSubscribers(self):
        self.rootFolder.setObject("rootFolderSubscriber", DummySubscriber())
        self.rootFolderSubscriber = ContextWrapper(
            self.rootFolder["rootFolderSubscriber"],
            self.rootFolder,
            name="rootFolderSubscriber")
        self.folder1.setObject("folder1Subscriber", DummySubscriber())
        self.folder1Subscriber = ContextWrapper(
            self.folder1["folder1Subscriber"],
            self.folder1,
            name="folder1Subscriber")
        self.folder1_1.setObject("folder1_1Subscriber", DummySubscriber())
        self.folder1_1Subscriber = ContextWrapper(
            self.folder1_1["folder1_1Subscriber"],
            self.folder1_1,
            name="folder1_1Subscriber")

    def _createHubIdSubscribers(self):
        self._createSubscribers()
        self.objectHub.lib = [self.rootFolderSubscriber,
                              self.folder1Subscriber,
                              self.folder1_1Subscriber]

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
        self.assertEqual(
            root,
            getPhysicalPathString(self.rootFolderSubscriber))
        self.assertEqual(
            folder1,
            getPhysicalPathString(self.folder1Subscriber))
        self.assertEqual(
            folder1_1,
            getPhysicalPathString(self.folder1_1Subscriber))
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        rootPath = getPhysicalPathString(self.rootFolderSubscriber)
        folder1Path = getPhysicalPathString(self.folder1Subscriber)
        folder1_1Path = getPhysicalPathString(self.folder1_1Subscriber)
        unsubscribe(rootPath, context=self.rootFolder)
            # curve ball:
        unsubscribe(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(folder1_1Path,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
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
            self.objectHub.lib[root],
            self.rootFolderSubscriber)
        self.assertEqual(
            self.objectHub.lib[folder1],
            self.folder1Subscriber)
        self.assertEqual(
            self.objectHub.lib[folder1_1],
            self.folder1_1Subscriber)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        self.assertRaises(
            NotFoundError,
            unsubscribe,
            getPhysicalPathString(self.rootFolderSubscriber),
            event_type=IObjectAddedEvent,
            context=self.rootFolder)
        unsubscribe(root, context=self.rootFolder)
            # curve balls:
        unsubscribe(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(2,
                    event_type=IObjectAddedEvent, 
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def testByPathExplicit(self):
        # test complex interaction, with hubids available but explicitly
        # using paths
        self._createHubIdSubscribers()
        rootPath = getPhysicalPathString(self.rootFolderSubscriber)
        folder1Path = getPhysicalPathString(self.folder1Subscriber)
        folder1_1Path = getPhysicalPathString(self.folder1_1Subscriber)
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
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        unsubscribe(rootPath, context=self.rootFolder)
            # curve balls:
        unsubscribe(self.folder1Subscriber, context=self.folder1_1)
        self.assertRaises(
            NotFoundError,
            unsubscribe,
            2,
            event_type=IObjectAddedEvent,
            context=self.folder1_1)
        unsubscribe(folder1_1Path,
                    event_type=IObjectAddedEvent,
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
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
            self.rootFolderSubscriber)
        self.assertEqual(
            self.objectHub.lib[folder1],
            self.folder1Subscriber)
        self.assertEqual(
            self.objectHub.lib[folder1_1],
            self.folder1_1Subscriber)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
        self.assertRaises(
            NotFoundError,
            unsubscribe,
            getPhysicalPathString(self.rootFolderSubscriber),
            event_type = IObjectAddedEvent,
            context=self.rootFolder)
        unsubscribe(root, context=self.rootFolder)
            # curve ball:
        unsubscribe(self.folder1Subscriber, context=self.folder1_1)
        unsubscribe(2,
                    event_type=IObjectAddedEvent, 
                    context=self.folder1_1)
        publish(self.folder1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

    def _testListSubscriptions1(self):
        # a non-subscribed subscriber gets an empty array
        events = getSubscriptionService(self.rootFolder)

        self.assertEqual(events.listSubscriptions(self.rootFolderSubscriber),
                         [])

    def testPathListSubscriptions1(self):
        self._createSubscribers()
        self._testListSubscriptions1()

    def testHubIdListSubscriptions1(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions1()

    def _testListSubscriptions2(self):
        # one subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual([(IObjectAddedEvent,None)],
                         getSubscriptionService(self.rootFolder)
                            .listSubscriptions(self.rootFolderSubscriber))

    def testPathListSubscriptions2(self):
        self._createSubscribers()
        self._testListSubscriptions2()

    def testHubIdListSubscriptions2(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions2()

    def _testListSubscriptions3(self):
        # listing limited subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual([],
                         getSubscriptionService(self.rootFolder)
                            .listSubscriptions(self.rootFolderSubscriber,
                                               IObjectRemovedEvent))

    def testPathListSubscriptions3(self):
        self._createSubscribers()
        self._testListSubscriptions3()

    def testHubIdListSubscriptions3(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions3()

    def _testListSubscriptions4(self):
        # a non-subscribed subscriber gets an empty array
        events = getSubscriptionService(self.rootFolder)

        self.assertEqual(events.listSubscriptions(self.rootFolderSubscriber),
                         [])
    
    def testPathListSubscriptions4(self):
        self._createSubscribers()
        self._testListSubscriptions4()
    
    def testHubIdListSubscriptions4(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions4()

    def _testListSubscriptions5(self):
        # one subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual([(IObjectAddedEvent,None)],
                         getSubscriptionService(self.rootFolder)
                            .listSubscriptions(self.rootFolderSubscriber))

    def testPathListSubscriptions5(self):
        self._createSubscribers()
        self._testListSubscriptions5()

    def testHubIdListSubscriptions5(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions5()

    def _testListSubscriptions6(self):
        # listing limited subscription
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual([],
                         getSubscriptionService(self.rootFolder)
                            .listSubscriptions(self.rootFolderSubscriber,
                                               IObjectRemovedEvent))

    def testPathListSubscriptions6(self):
        self._createSubscribers()
        self._testListSubscriptions6()

    def testHubIdListSubscriptions6(self):
        self._createHubIdSubscribers()
        self._testListSubscriptions6()

    def _testSubscribe1(self):
        # Test subscribe method with one parameter
        subscribe(self.rootFolderSubscriber)
        publish(self.rootFolder, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        unsubscribe(
            self.rootFolderSubscriber
            )
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
                          self.rootFolderSubscriber,
                          IObjectEvent)
        self.assertEqual(None,
                         unsubscribe(self.rootFolderSubscriber))

    def testPathUnsubscribe2(self):
        self._createSubscribers()
        self._testUnsubscribe2()

    def testHubIdUnsubscribe2(self):
        self._createHubIdSubscribers()
        self._testUnsubscribe2()

    def _testUnsubscribe3(self):
        # Test selective unsubscribe
        subscriber=self.rootFolderSubscriber
        subscriber2=self.folder1Subscriber
        filter=DummyFilter()
        event=ObjectAddedEvent(None, '/foo')
        event2=ObjectModifiedEvent(None, '/foo')
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        publish(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
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
        self.folder2.setObject("folder2Subscriber", DummySubscriber())
        self.folder2Subscriber = ContextWrapper(
            self.folder2["folder2Subscriber"],
            self.folder2,
            name="folder2Subscriber")

        if not self.folder2.hasServiceManager():
            self.folder2.setServiceManager(ServiceManager())

        sm = traverse(self.rootFolder, 'folder2/++etc++Services')
        default = traverse(sm, 'Packages/default')

        default.setObject("myEventService", service)

        path = "%s/Packages/default/myEventService" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration("Events", path)
        default['configure'].setObject("myEventServiceDir", configuration)
        traverse(default, 'configure/1').status = Active

        configuration = ServiceConfiguration("Subscription", path)
        default['configure'].setObject("mySubscriptionServiceDir",
                                       configuration)
        traverse(
            default,
            'configure/2').status = Active

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
        publish(self.folder2, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder2Subscriber.notified, 1)
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testPromotingEventPublisher1(self):
        # test to see if events are passed on to a parent event service with
        # the appropriate isPromotableEvent setting
        self._createHubIdSubscribers()
        self._createAlternateService(EventService())
        publish(self.folder2, ObjectAddedEvent(None, '/foo'))
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

        sm = traverse(self.rootFolder, "folder1/++etc++Services")
        configuration = sm.queryConfigurations("Events").active()
        configuration.status = Registered

        publish(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)

        configuration = sm.queryConfigurations("Subscription").active()
        configuration.status = Registered

        publish(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder1Subscriber.notified, 1)
        self.assertEqual(self.folder1_1Subscriber.notified, 2)

    def testNoSubscribeOnBind(self):
        # if subscribeOnBind is 0, service should not subscribe to parent
        sv = EventService()
        sv.subscribeOnBind = 0
        self._createHubIdSubscribers()
        self._createAlternateService(sv)
        publish(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder2Subscriber.notified, 0)
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

        sm = traverse(self.rootFolder, "folder2/++etc++Services")
        configuration = sm.queryConfigurations("Subscription").active()
        # make sure it doesn't raise any errors
        configuration.status = Registered
        configuration = sm.queryConfigurations("Events").active()
        # make sure it doesn't raise any errors
        configuration.status = Registered

    def testSubscriptionAwareInteraction(self):
        adapter = SubscribingAwareAdapter()
        provideAdapter(IHasSubscribingAwareAdapter,
                       ISubscribingAware,
                       adapter)
        self.rootFolder.setObject(
            "mySubscriber",
            HasSubscribingAwareAdapter())
        self.mySubscriber = ContextWrapper(
            self.rootFolder["mySubscriber"],
            self.rootFolder,
            name="mySubscriber")
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
