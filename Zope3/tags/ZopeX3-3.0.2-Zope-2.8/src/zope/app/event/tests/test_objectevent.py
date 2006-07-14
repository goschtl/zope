##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object Event Tests

$Id$
"""
import unittest
import doctest

from zope.interface import implements
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.objectevent import ObjectAnnotationsModifiedEvent
from zope.app.event.objectevent import ObjectContentModifiedEvent
from zope.app.event import objectevent
from zope.app.container.contained import Contained, ObjectRemovedEvent
from zope.app.container.interfaces import IContained, IObjectRemovedEvent
from zope.app.container.interfaces import IObjectEvent
from zope.app.container.sample import SampleContainer
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.app.tests import ztapi

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
        events = []

        def record(*args):
            events.append(args)

        ztapi.handle([IContained, IObjectRemovedEvent], record)

        item = Contained()
        event = ObjectRemovedEvent(item)
        objectevent.objectEventNotify(event)
        self.assertEqual([(item, event)], events)

    def testNotifyNobody(self):
        # Check that notify won't raise an exception in absence of
        # of subscribers.
        events = []
        item = Contained()
        evt = ObjectRemovedEvent(item)
        objectevent.objectEventNotify(evt)
        self.assertEqual([], events)

    def testVeto(self):
        ztapi.handle([IObjectEvent], objectevent.objectEventNotify)
        container = SampleContainer()
        item = Contained()

        # This will fire an event.
        container['Fred'] = item

        class Veto(Exception):
            pass
        
        def callback(item, event):
            self.callbackTriggered = True
            self.assertEqual(item, event.object)
            raise Veto

        ztapi.handle([IContained, IObjectRemovedEvent], callback)

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
