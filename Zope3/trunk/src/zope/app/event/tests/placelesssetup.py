##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Unit test logic for setting up and tearing down basic infrastructure


$Id: placelesssetup.py,v 1.12 2003/11/21 17:11:36 jim Exp $
"""

from zope.component import getServiceManager
from zope.app.services.servicenames import EventPublication
from zope.app.interfaces.event import IPublisher, ISubscriber
from zope.app.event.globalservice import eventPublisher
from zope.interface import implements

events = []

class EventRecorderClass:
    implements(ISubscriber)

    notify = events.append

EventRecorder = EventRecorderClass()

def getEvents(event_type=None, filter=None):
    r = []
    for event in events:
        if event_type is not None and not event_type.isImplementedBy(event):
            continue
        if filter is not None and not filter(event):
            continue
        r.append(event)

    return r

def clearEvents():
    del events[:]

class PlacelessSetup:

    def setUp(self):
        sm = getServiceManager(None)
        defineService = sm.defineService
        provideService = sm.provideService

        defineService(EventPublication, IPublisher)
        provideService(EventPublication, eventPublisher)

        clearEvents()
        eventPublisher.globalSubscribe(EventRecorder)

import zope.testing.cleanup
zope.testing.cleanup.addCleanUp(clearEvents)
