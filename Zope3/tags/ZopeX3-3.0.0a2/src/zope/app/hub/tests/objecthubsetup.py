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
from zope.app import zapi
from zope.app.event.tests.eventsetup import EventSetup
from zope.app.servicenames import HubIds
from zope.app.traversing.api import traverse, canonicalPath

from zope.app.container.interfaces import IObjectAddedEvent, IObjectMovedEvent
from zope.app.event.interfaces import ISubscriber

from zope.interface import implements

class LoggingSubscriber:
    # XXX Jim mentioned there is a new generic
    # version of this in zope.app somewhere...

    implements(ISubscriber)

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
            location = canonicalPath(location)
            testcase.assert_(interface.providedBy(event),
                             'Interface %s' % interface.getName())
            testcase.assertEqual(canonicalPath(event.object), location)

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
        # The policy is to register on object adds and object copies.
        if IObjectAddedEvent.providedBy(event):
            self.hub.register(event.object)

class ObjectHubSetup(EventSetup):

    def setUpRegistrationSubscriber(self):
        subscriber = RegistrationSubscriber(self.object_hub)
        self.rootFolder['registration_subscriber'] = subscriber
        self.subscriber = traverse(self.rootFolder, 'registration_subscriber')
        self.object_hub.subscribe(self.subscriber)

    def setUpLoggingSubscriber(self):
        subscriber = LoggingSubscriber()
        self.rootFolder['logging_subscriber'] = subscriber
        self.subscriber = traverse(self.rootFolder, 'logging_subscriber')
        self.object_hub.subscribe(self.subscriber)

    def setUp(self):
        EventSetup.setUp(self)
        self.object_hub = zapi.getService(self.rootFolder, HubIds)

