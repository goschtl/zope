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
$Id: objecthubsetup.py,v 1.6 2003/02/11 15:59:57 sidnei Exp $
"""

from zope.app.services.tests.eventsetup import EventSetup
from zope.component import getServiceManager, getService
from zope.component.servicenames import HubIds
from zope.app.services.service import ServiceConfiguration
from zope.app.traversing import getPhysicalPathString, traverse
from zope.app.traversing import locationAsTuple

from zope.app.services.hub import ObjectHub
from zope.app.interfaces.event import IObjectAddedEvent
from zope.app.interfaces.services.configuration import Active
from zope.app.interfaces.event import ISubscriber

class LoggingSubscriber:
    # XXX Jim mentioned there is a new generic
    # version of this in zope.app somewhere...

    __implements__ = ISubscriber

    def __init__(self):
        self.events_received = []

    def notify(self, event):
        self.events_received.append(event)

    def verifyEventsReceived(self, testcase, event_spec_list):
        # iterate through self.events_received and check
        # that each one implements the interface that is
        # in the same place, with the same location and hub id

        testcase.assertEqual(len(event_spec_list), len(self.events_received))

        for spec,event in zip(event_spec_list, self.events_received):
            if len(spec)==4:
                interface,hubid,location,obj = spec
            elif len(spec)==3:
                interface,hubid,location = spec
                obj = None
            elif len(spec)==2:
                interface, location = spec
                obj = None
                hubid = None
            location = locationAsTuple(location)
            testcase.assert_(interface.isImplementedBy(event),
                             'Interface %s' % interface.getName())
            testcase.assertEqual(event.location, location)

            if obj is not None:
                testcase.assertEqual(event.object, obj)

            # Sometimes, the test won't care about the hubid. In this case,
            # it is passed into the spec as None.
            if hubid is not None:
                testcase.assertEqual(event.hubid, hubid)

        self.events_received = []

class RegistrationSubscriber(LoggingSubscriber):
    def __init__(self, objectHub):
        LoggingSubscriber.__init__(self)
        self.hub = objectHub

    def notify(self, event):
        LoggingSubscriber.notify(self, event)
        if IObjectAddedEvent.isImplementedBy(event):
            self.hub.register(event.location)

class ObjectHubSetup(EventSetup):

    def setUpRegistrationSubscriber(self):
        subscriber = RegistrationSubscriber(self.object_hub)
        self.rootFolder.setObject('registration_subscriber', subscriber)
        self.subscriber = traverse(self.rootFolder, 'registration_subscriber')
        self.object_hub.subscribe(self.subscriber)

    def setUpLoggingSubscriber(self):
        subscriber = LoggingSubscriber()
        self.rootFolder.setObject('logging_subscriber', subscriber)
        self.subscriber = traverse(self.rootFolder, 'logging_subscriber')
        self.object_hub.subscribe(self.subscriber)
        
    def setUp(self):
        EventSetup.setUp(self)
        self.object_hub = getService(self.rootFolder, HubIds)

