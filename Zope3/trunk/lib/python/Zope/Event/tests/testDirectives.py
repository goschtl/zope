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
$Id: testDirectives.py,v 1.3 2002/07/17 16:54:21 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from StringIO import StringIO

from Zope.Configuration.xmlconfig import xmlconfig

from Zope.Exceptions import NotFoundError
from Zope.Event import subscribe, unsubscribe, publishEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent
from Zope.Event.ObjectEvent import ObjectRemovedEvent
from Zope.Event.ObjectEvent import ObjectModifiedEvent
from testEventService import DummySubscriber, DummyFilter, DummyEvent
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getServiceManager, getService

template = """<zopeConfigure
  xmlns='http://namespaces.zope.org/zope'
  xmlns:event='http://namespaces.zope.org/event'>
  %s
  </zopeConfigure>"""

class Test(PlacelessSetup, TestCase):
    
    def setUp(self):
        PlacelessSetup.setUp(self)
        from Zope.Event.IEventService import IEventService
        getServiceManager(None).defineService("Events", IEventService)
        from Zope.Event.GlobalEventService import eventService
        getServiceManager(None).provideService("Events", eventService)

    def testSubscribe(self):
        from Zope.Event.tests.subscriber import subscriber
        # This should fail, since we're not subscribed
        self.assertRaises(NotFoundError,unsubscribe,None,subscriber)
            
        xmlconfig(StringIO(template % (
            """
            <directive name="subscribe"
                       attributes="subscriber event_types filter"
                       handler="Zope.Event.metaConfigure.subscribe"
                       namespace="http://namespaces.zope.org/event"/>
            <event:subscribe subscriber="Zope.Event.tests.subscriber.subscriber"
                            
 event_types="Zope.Event.IObjectEvent.IObjectAddedEvent
                                         
 Zope.Event.IObjectEvent.IObjectRemovedEvent"
                             filter="Zope.Event.tests.subscriber.filter"/>
            """)))

        publishEvent(None,ObjectAddedEvent('foo'))
        self.assertEqual(subscriber.notified,1)
        publishEvent(None,ObjectRemovedEvent('foo', object()))
        self.assertEqual(subscriber.notified,2)
        publishEvent(None,ObjectModifiedEvent('foo'))
        self.assertEqual(subscriber.notified,2) # NB: no increase ;-)
        publishEvent(None,DummyEvent())
        self.assertEqual(subscriber.notified,4) # NB: increased by 2 ;-)
        
        unsubscribe(subscriber)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
