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
$Id: testEventService.py,v 1.6 2002/11/30 18:37:17 jim Exp $
"""

from unittest import TestCase, TestLoader, TextTestRunner

from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager

from Zope.App.OFS.Services.LocalEventService.LocalEventService \
     import LocalEventService

from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration

from Zope.App.Traversing import getPhysicalPathString, traverse

from Zope.ComponentArchitecture import getService, getServiceManager

from Zope.Exceptions import NotFoundError

from Zope.Event import subscribe, unsubscribe, listSubscriptions, publishEvent
from Zope.Event.tests.subscriber import DummySubscriber, DummyFilter
from Zope.Event.IObjectEvent import IObjectEvent
from Zope.Event.IObjectEvent import IObjectAddedEvent
from Zope.Event.IObjectEvent import IObjectRemovedEvent
from Zope.Event.IObjectEvent import IObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent, ObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent
from Zope.Event.GlobalEventService import GlobalEventService
from Zope.Event.IEvent import IEvent
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered

from Zope.Proxy.ContextWrapper import ContextWrapper

from EventSetup import EventSetup

class UnpromotingLocalEventService(LocalEventService):
    
    def isPromotableEvent(self, event):
        "see ILocalEventService"
        return 0

class DummyEvent:

    __implements__ = IObjectAddedEvent, IObjectRemovedEvent

class ObjectEvent:

    __implements__ = IObjectEvent



class DummySubscriptionAwareSubscriber(DummySubscriber):
    __implements__ = ISubscriptionAware
    
    def subscribedTo(self, subscribable, event_type, filter):
        self.subscribable = subscribable
        self.event_type = event_type
        self.filter = filter
    
    def unsubscribedFrom(self, subscribable, event_type, filter):
        self.un_subscribable = subscribable
        self.un_event_type = event_type
        self.un_filter = filter

class EventServiceTests(EventSetup, TestCase):
    
    def _createNestedServices(self):
        self.createEventService('folder1')
        self.createEventService('folder1/folder1_1')
        self.createEventService('folder1/folder1_1/folder1_1_1')
    
    def _createSubscribers(self):
        self.rootFolder.setObject("rootFolderSubscriber", DummySubscriber())
        self.rootFolderSubscriber=ContextWrapper(
            self.rootFolder["rootFolderSubscriber"],
            self.rootFolder,
            name="rootFolderSubscriber")
        self.folder1.setObject("folder1Subscriber", DummySubscriber())
        self.folder1Subscriber=ContextWrapper(
            self.folder1["folder1Subscriber"],
            self.folder1,
            name="folder1Subscriber")
        self.folder1_1.setObject("folder1_1Subscriber", DummySubscriber())
        self.folder1_1Subscriber=ContextWrapper(
            self.folder1_1["folder1_1Subscriber"],
            self.folder1_1,
            name="folder1_1Subscriber")
        
    def testCreateNestedServices(self):
        self._createNestedServices()
    
    def testListSubscriptions1(self):
        "a non-subscribed subscriber gets an empty array"
        self._createSubscribers()

        events = getService(self.rootFolder, "Events")
        
        self.assertEqual(events.listSubscriptions(self.rootFolderSubscriber),
                         [])
    
    def testListSubscriptions2(self):
        "one subscription"
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual(
            [(IObjectAddedEvent,None)],
            self.rootFolder.getServiceManager().getService(
            "Events").listSubscriptions(self.rootFolderSubscriber))
    
    def testListSubscriptions3(self):
        "listing limited subscription"
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        self.assertEqual(
            [],
            self.rootFolder.getServiceManager().getService(
            "Events").listSubscriptions(self.rootFolderSubscriber, IObjectRemovedEvent))
    
    def testSubscribe1(self):
        "Test subscribe method with one parameter"
        self._createSubscribers()
        subscribe(self.rootFolderSubscriber)
        publishEvent(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        
    def testSubscribe2(self):
        "Test subscribe method with two parameters"
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testSubscribe3(self):
        "Test subscribe method with three parameters"
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter()
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testSubscribe4(self):
        """Test subscribe method with three parameters
        and an always failing filter.
        """
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent,
            filter=DummyFilter(0)
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testSubscribe5(self):
        """Test subscribe method with three parameters
        and an irrelevent event type.
        """
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectModifiedEvent,
            filter=DummyFilter()
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 0)

    def testSubscribe6(self):
        """Test subscribe method where the event type
        registered is a generalised interface of the
        event passed to the 'publishEvent' method.
        """
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectEvent
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testSubscribe7(self):
        """Test subscribe method where one of the
        event types registered is not interested in
        the publishEvented event.
        """
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectModifiedEvent
            )
        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testSubscribe8(self):
        """Test subscribe method where the same subscriber
        subscribes multiple times. 
        """
        self._createSubscribers()
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
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 2)

    def testUnsubscribe1(self):
        "Test unsubscribe method"
        self._createSubscribers()
        subscribe(
            self.rootFolderSubscriber
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
        unsubscribe(
            self.rootFolderSubscriber
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

    def testUnsubscribe2(self):
        "Test unsubscribe of something that hasn't been subscribed"
        self._createSubscribers()
        self.assertRaises(NotFoundError,
                          unsubscribe,
                          self.rootFolderSubscriber,
                          IObjectEvent)
        self.assertEqual(None,
                         unsubscribe(self.rootFolderSubscriber))
    
    def testUnsubscribe3(self):
        "Test selective unsubscribe"
        self._createSubscribers()
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
        publishEvent(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 3)
        self.assertEqual(subscriber2.notified, 1)
        publishEvent(self.folder1_1_1, event2)
        self.assertEqual(subscriber.notified, 4)
        self.assertEqual(subscriber2.notified, 1)
        unsubscribe(subscriber, IObjectAddedEvent)
        publishEvent(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        unsubscribe(subscriber, IEvent)
        publishEvent(self.folder1_1_1, event2)
        self.assertEqual(subscriber.notified, 6)
        self.assertEqual(subscriber2.notified, 2)
        publishEvent(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 3)
        self.assertRaises(NotFoundError, unsubscribe, subscriber, IObjectAddedEvent)
        unsubscribe(subscriber, IObjectAddedEvent, filter)
        publishEvent(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 4)
        unsubscribe(subscriber2, IObjectAddedEvent)
        publishEvent(self.folder1_1_1, event)
        self.assertEqual(subscriber.notified, 7)
        self.assertEqual(subscriber2.notified, 4)
    
    def testUnsubscribe4(self):
        "Test selective unsubscribe with nested services"
        self._createNestedServices()
        self.testUnsubscribe3()

    def testpublishEvent1(self):
        "Test publishEvent method"
        self._createSubscribers()
        subscriber = self.rootFolderSubscriber
        subscribe(subscriber)
        self.assertEqual(subscriber.notified, 0)
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(subscriber.notified, 1)

    def testpublishEvent2(self):
        """Test publishEvent method where subscriber has been
        subscribed twice, with a more generalised
        version of the initially subscribed interface
        in the second subscription.
        """
        self._createSubscribers()
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectEvent,
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent,
            )
        publishEvent(self.folder1_1_1, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(subscriber.notified, 2)

    def testpublishEvent3(self):
        """Test publishEvent method where subscriber has been
        to two interfaces and a single event implements both
        of those interfaces.
        """
        self._createSubscribers()
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectRemovedEvent
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent
            )
        publishEvent(self.folder1_1_1, DummyEvent())
        self.assertEqual(subscriber.notified, 2)

    def testpublishEvent4(self):
        """Test publishEvent method to make sure that we don't
        'leak registrations up' sez Jim.
        """
        self._createSubscribers()
        subscriber = self.rootFolderSubscriber
        subscribe(
            subscriber,
            event_type=IObjectEvent
            )
        subscribe(
            subscriber,
            event_type=IObjectAddedEvent
            )
        publishEvent(self.folder1_1_1, ObjectEvent())
        self.assertEqual(subscriber.notified, 1)
    
    def _createAlternateService(self, service):
        self._createSubscribers()
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

        subscribe(
            self.rootFolderSubscriber,
            event_type=IObjectAddedEvent
            )
        subscribe(
            self.folder2Subscriber,
            event_type=IObjectAddedEvent
            )
    
    def testNonPromotingEventService1(self):
        """test to see if events are not passed on to a parent event
        service with the appropriate isPromotableEvent setting"""
        self._createAlternateService(UnpromotingLocalEventService())
        publishEvent(self.folder2, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder2Subscriber.notified, 1)
        self.assertEqual(self.rootFolderSubscriber.notified, 0)
    
    def testPromotingEventService1(self):
        """test to see if events are passed on to a parent event
        service with the appropriate isPromotableEvent setting"""
        self._createAlternateService(LocalEventService())
        publishEvent(self.folder2, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder2Subscriber.notified, 1)
        self.assertEqual(self.rootFolderSubscriber.notified, 1)
    
    def testUnbindingResubscribing1(self):
        """an event service is unbound; a lower event service should
        then rebind to upper event service"""
        self._createNestedServices()
        self._createSubscribers()
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

        publishEvent(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder1Subscriber.notified, 0)
        self.assertEqual(self.folder1_1Subscriber.notified, 1)
    
    def testNoSubscribeOnBind(self):
        """if subscribeOnBind is 0, service should not subscribe to
        parent"""
        sv=LocalEventService()
        sv.subscribeOnBind=0
        self._createAlternateService(sv)
        publishEvent(self.rootFolder, ObjectAddedEvent(None, '/foo'))
        self.assertEqual(self.folder2Subscriber.notified, 0)
        self.assertEqual(self.rootFolderSubscriber.notified, 1)

        sm = traverse(self.rootFolder, "folder2/++etc++Services")
        configuration = sm.queryConfigurations("Events").active()
        # make sure it doesn't raise any errors
        configuration.status = Registered
        
    def testSubscriptionAwareInteraction(self):
        sub = DummySubscriptionAwareSubscriber()
        self.rootFolder.setObject(
            "mySubscriber",
            DummySubscriptionAwareSubscriber())
        self.mySubscriber=ContextWrapper(
            self.rootFolder["mySubscriber"],
            self.rootFolder,
            name="mySubscriber")
        filter = DummyFilter()
        subscribe(
            self.mySubscriber,
            event_type=IObjectAddedEvent,
            filter=filter)
        self.assertEqual(
            self.mySubscriber.subscribable,
            self.rootFolder.getServiceManager().getService("Events"))
        self.assertEqual(
            self.mySubscriber.event_type,
            IObjectAddedEvent)
        self.assertEqual(
            self.mySubscriber.filter,
            filter)
        unsubscribe(
            self.mySubscriber,
            event_type=IObjectAddedEvent,
            filter=filter)
        self.assertEqual(
            self.mySubscriber.un_subscribable,
            self.rootFolder.getServiceManager().getService("Events"))
        self.assertEqual(
            self.mySubscriber.un_event_type,
            IObjectAddedEvent)
        self.assertEqual(
            self.mySubscriber.un_filter,
            filter)
        
        
def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(EventServiceTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
