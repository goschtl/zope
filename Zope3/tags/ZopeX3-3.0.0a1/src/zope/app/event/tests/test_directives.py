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
$Id$
"""
from unittest import TestCase, main, makeSuite

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
import zope.app.event
from StringIO import StringIO

from zope.exceptions import NotFoundError
from zope.app.event import globalUnsubscribe, publish
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.tests.test_eventpublisher import DummyEvent
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getServiceManager
from zope.app.servicenames import EventPublication
from zope.app.event.interfaces import IEvent

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        from zope.app.event.interfaces import IPublisher
        getServiceManager(None).defineService(EventPublication, IPublisher)
        from zope.app.event.globalservice import eventPublisher
        getServiceManager(None).provideService(EventPublication, eventPublisher)

    def testSubscribe(self):
        from zope.app.event.tests.subscriber import subscriber
        # This should do nothing silently, as the event_type is default
        globalUnsubscribe(subscriber)
        # This should fail, since we're not subscribed
        self.assertRaises(NotFoundError, globalUnsubscribe, subscriber, IEvent)
        XMLConfig('meta.zcml', zope.app.event)()
        xmlconfig(StringIO(
            '''<configure xmlns='http://namespaces.zope.org/zope'
                              xmlns:test='http://namespaces.zope.org/event'>
            <test:subscribe
                   subscriber="zope.app.event.tests.subscriber.subscriber"
                   event_types=
                       "zope.app.container.interfaces.IObjectAddedEvent
                        zope.app.container.interfaces.IObjectRemovedEvent"
                   filter="zope.app.event.tests.subscriber.filter" />
            </configure>'''
            ))

        parent= object()
        publish(None, ObjectAddedEvent(None, parent, 'foo'))
        self.assertEqual(subscriber.notified, 1)
        publish(None, ObjectRemovedEvent(object(), parent, 'foo'))
        self.assertEqual(subscriber.notified, 2)
        publish(None, ObjectModifiedEvent(None))
        self.assertEqual(subscriber.notified, 2) # NB: no increase ;-)
        publish(None, DummyEvent())
        self.assertEqual(subscriber.notified, 4) # NB: increased by 2 ;-)

        globalUnsubscribe(subscriber)

        subscriber.notified = 0

def test_suite():
    return makeSuite(Test)

if __name__ == '__main__':
    main(defaultTest='test_suite')
