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

$Id: test_globaleventchannel.py,v 1.1 2002/12/30 14:03:05 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.interfaces.event import IEvent

class ISomeEvent(IEvent):
    pass

class ISomeSubEvent(ISomeEvent):
    pass

class ISomeOtherEvent(IEvent):
    pass

class SomeEvent:
    __implements__ = ISomeEvent

class SomeSubEvent:
    __implements__ = ISomeSubEvent

class SomeOtherEvent:
    __implements__ = ISomeOtherEvent

class SubscriberStub:
    received = None
    def notify(self, event):
        self.received = event

class Test(TestCase):

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


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
