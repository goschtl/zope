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
"""A functional GlobalEventChannel test.

$Id: test_globaleventchannel.py,v 1.2 2003/01/27 18:16:57 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.interfaces.event import IEvent, ISubscribingAware, ISubscriber
from zope.interface import Interface
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.tests.components import RecordingAdapter
from zope.component.adapter import provideAdapter

class ISomeEvent(IEvent):
    pass

class ISomeSubEvent(ISomeEvent):
    pass

class ISomeOtherEvent(IEvent):
    pass

class ISubscriberStub(ISubscriber):
    pass

class INonSubscriberStub(Interface):
    pass

class SomeEvent:
    __implements__ = ISomeEvent

class SomeSubEvent:
    __implements__ = ISomeSubEvent

class SomeOtherEvent:
    __implements__ = ISomeOtherEvent

class SubscriberStub:
    __implements__ = ISubscriberStub
    received = None
    def notify(self, event):
        self.received = event

class NonSubscriberStub:
    __implements__ = INonSubscriberStub


class Test(PlacelessSetup, TestCase):

    def test_notify(self):
        from zope.app.event.globalservice import GlobalEventChannel

        subscriber = SubscriberStub()
        ec = GlobalEventChannel()
        ec.globalSubscribe(subscriber, ISomeEvent)

        ev = SomeEvent()
        ec.notify(ev)
        self.assertEquals(subscriber.received, ev,
                          "Did not get event registered for")

        ev = SomeSubEvent()
        ec.notify(ev)
        self.assertEquals(
                subscriber.received, ev, "Did not get subclassed event")

        ev = SomeOtherEvent()
        ec.notify(ev)
        self.assertNotEquals(subscriber.received, ev, "Got unrelated event")

    def test_notify_filter(self):
        from zope.app.event.globalservice import GlobalEventChannel

        true = lambda x: True
        false = lambda x: False

        subscriber = SubscriberStub()
        ec = GlobalEventChannel()
        ec.globalSubscribe(subscriber, ISomeEvent, true)

        ev = SomeEvent()
        ec.notify(ev)
        self.assertEquals(subscriber.received, ev,
                          "Did not get event registered for")

        subscriber = SubscriberStub()
        ec = GlobalEventChannel()
        ec.globalSubscribe(subscriber, ISomeEvent, false)

        ev = SomeEvent()
        ec.notify(ev)
        self.assertEquals(subscriber.received, None,
                          "Event was not filtered")

class SubAware(RecordingAdapter):
    __implements__ = ISubscribingAware

    def subscribedTo(self, subscribable, event_type, filter):
        self.record.append(('subscribed', self.context, subscribable,
                            event_type, filter))

    def unsubscribedFrom(self, subscribable, event_type, filter):
        self.record.append(('unsubscribed', self.context, subscribable,
                            event_type, filter))


class TestSubscribingAwareChannel(PlacelessSetup, TestCase):

    def setUpChannel(self):
        from zope.app.event.globalservice import GlobalEventChannel
        self.ec = GlobalEventChannel()

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.setUpChannel()
        self.subscriber = SubscriberStub()
        self.filter = lambda x: True
        self.subaware = SubAware()
        provideAdapter(ISubscriberStub, ISubscribingAware, self.subaware)

    def test_subscribe(self):
        self.ec.globalSubscribe(self.subscriber, ISomeEvent, self.filter)
        self.subaware.check(
            ('subscribed', self.subscriber, self.ec, ISomeEvent, self.filter)
            )

    def test_unsubscribe(self):
        self.test_subscribe()
        self.ec.unsubscribe(self.subscriber, ISomeEvent, self.filter)
        self.subaware.check(
        ('subscribed', self.subscriber, self.ec, ISomeEvent, self.filter),
        ('unsubscribed', self.subscriber, self.ec, ISomeEvent, self.filter),
        )

class TestSubscribingAwareGlobalPublisher(TestSubscribingAwareChannel):

    def setUpChannel(self):
        from zope.app.event.globalservice import GlobalEventPublisher
        self.ec = GlobalEventPublisher()

class SubscriberAdapter(RecordingAdapter):
    __implements__ = ISubscriber

    def notify(self, event):
        self.record.append(('notified', self.context, event))

class TestAdaptingToISubscriberBase(PlacelessSetup, TestCase):

    def setUpChannel(self):
        raise NotImplementedError('You need to write a setUpChannel method.')

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.setUpChannel()
        self.subscriber = NonSubscriberStub()
        self.event = SomeEvent()
        self.adapter = SubscriberAdapter()
        provideAdapter(INonSubscriberStub, ISubscriber, self.adapter)

class TestAdaptingToISubscriberOnNotify(TestAdaptingToISubscriberBase):
    def setUpChannel(self):
        from zope.app.event.globalservice import GlobalEventChannel
        self.ec = GlobalEventChannel()

    def test_notify(self):
        self.ec.globalSubscribe(self.subscriber, ISomeEvent)
        self.ec.notify(self.event)
        self.adapter.check(
            ('notified', self.subscriber, self.event)
            )

class TestAdaptingToISubscriberOnPublish(TestAdaptingToISubscriberBase):
    def setUpChannel(self):
        from zope.app.event.globalservice import GlobalEventPublisher
        self.ec = GlobalEventPublisher()

    def test_notify(self):
        self.ec.globalSubscribe(self.subscriber, ISomeEvent)
        self.ec.publish(self.event)
        self.adapter.check(
            ('notified', self.subscriber, self.event)
            )


def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(TestSubscribingAwareChannel),
        makeSuite(TestSubscribingAwareGlobalPublisher),
        makeSuite(TestAdaptingToISubscriberOnNotify),
        makeSuite(TestAdaptingToISubscriberOnPublish),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
