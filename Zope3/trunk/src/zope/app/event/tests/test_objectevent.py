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
$Id: test_objectevent.py,v 1.6 2004/03/02 18:50:59 philikon Exp $
"""

import unittest

from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.objectevent import ObjectAnnotationsModifiedEvent
from zope.app.event.objectevent import ObjectContentModifiedEvent
from zope.app.event import objectevent
from zope.app.container.contained import Contained, ObjectRemovedEvent
from zope.app.interfaces.container import IContained, IObjectRemovedEvent
from zope.app.interfaces.container import IObjectEvent
from zope.app.event.interfaces import ISubscriber
from zope.app.container.sample import SampleContainer
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.app.services.servicenames import Adapters, EventPublication
from zope.component import getService


class TestObjectModifiedEvent(unittest.TestCase):

    klass = ObjectModifiedEvent

    object = object()

    def setUp(self):
        self.event = self.klass(self.object)

    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

class TestObjectAnnotationsModifiedEvent(TestObjectModifiedEvent):
    klass = ObjectAnnotationsModifiedEvent

class TestObjectContentModifiedEvent(TestObjectModifiedEvent):
    klass = ObjectContentModifiedEvent

class TestObjectEventNotifications(unittest.TestCase):
    def setUp(self):
        self.callbackTriggered = False
        setUp()

    def testNotify(self):
        notifier = objectevent.ObjectEventNotifier()
        events = []

        factory = objectevent.objectEventCallbackHelper(events.append)
        getService(None, Adapters).provideSubscriptionAdapter(
            IContained, ISubscriber, [factory], with=[IObjectRemovedEvent]
        )

        item = Contained()
        event = ObjectRemovedEvent(item)
        notifier.notify(event)
        self.assertEqual([event], events)
                
    def testNotifyNobody(self):
        # Check that notify won't raise an exception in absence of
        # of subscribers.
        notifier = objectevent.ObjectEventNotifier()
        events = []
        item = Contained()
        evt = ObjectRemovedEvent(item)
        notifier.notify(evt)
        self.assertEqual([], events)

    def testVeto(self):
        eventPublication = getService(None, EventPublication)
        eventPublication.globalSubscribe(objectevent.ObjectEventNotifier(),
                                         IObjectEvent)
        container = SampleContainer()
        item = Contained()

        # This will fire an event.
        container['Fred'] = item

        class Veto(Exception):
            pass
        
        def callback(event):
            self.callbackTriggered = True
            self.assertEqual(item, event.object)
            raise Veto

        factory = objectevent.objectEventCallbackHelper(callback)
        getService(None, Adapters).provideSubscriptionAdapter(
            IContained, ISubscriber, [factory], with=[IObjectRemovedEvent]
        )

        # del container['Fred'] will fire an ObjectRemovedEvent event.
        self.assertRaises(Veto, container.__delitem__, 'Fred')
        
    def tearDown(self):
        tearDown()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectModifiedEvent),
        unittest.makeSuite(TestObjectAnnotationsModifiedEvent),
        unittest.makeSuite(TestObjectContentModifiedEvent),
        unittest.makeSuite(TestObjectEventNotifications),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
