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
$Id: test_directives.py,v 1.2 2002/12/25 14:12:51 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from StringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig

from zope.exceptions import NotFoundError
from zope.event import subscribe, unsubscribe, publish
from zope.app.event.objectevent import ObjectAddedEvent
from zope.app.event.objectevent import ObjectRemovedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.tests.test_eventservice \
     import DummySubscriber, DummyFilter, DummyEvent
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getServiceManager, getService
from zope.configuration.tests.basetestdirectivesxml import makeconfig


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from zope.interfaces.event import IEventService
        getServiceManager(None).defineService("Events", IEventService)
        from zope.app.event.globaleventservice import eventService
        getServiceManager(None).provideService("Events", eventService)

    def testSubscribe(self):
        from zope.event.tests.subscriber import subscriber
        # This should fail, since we're not subscribed
        self.assertRaises(NotFoundError,unsubscribe,None,subscriber)

        xmlconfig(makeconfig(
            '''<directive
                   name="subscribe"
                   attributes="subscriber event_types filter"
                   handler="zope.app.event.metaconfigure.subscribe" />''',
            '''<test:subscribe
                   subscriber="zope.event.tests.subscriber.subscriber"
                   event_types=
                       "zope.app.interfaces.event.IObjectAddedEvent
                        zope.app.interfaces.event.IObjectRemovedEvent"
                   filter="zope.event.tests.subscriber.filter" />'''
            ))

        publish(None,ObjectAddedEvent(None, 'foo'))
        self.assertEqual(subscriber.notified,1)
        publish(None,ObjectRemovedEvent(object(), 'foo'))
        self.assertEqual(subscriber.notified,2)
        publish(None,ObjectModifiedEvent(None, 'foo'))
        self.assertEqual(subscriber.notified,2) # NB: no increase ;-)
        publish(None,DummyEvent())
        self.assertEqual(subscriber.notified,4) # NB: increased by 2 ;-)

        unsubscribe(subscriber)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
