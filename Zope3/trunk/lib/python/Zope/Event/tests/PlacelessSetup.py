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


$Id: PlacelessSetup.py,v 1.2 2002/10/04 20:07:09 jim Exp $
"""

from Zope.ComponentArchitecture import getServiceManager
from Zope.Event.IEventService import IEventService
from Zope.Event.GlobalEventService import eventService
from Interface import Interface

events = []

class EventRecorderClass:
    notify = events.append

EventRecorder = EventRecorderClass()

def getEvents(event_type = None, filter = None):
    r = []
    for event in events:
        if event_type is not None and not event_type.isImplementedBy(event):
            continue
        if filter is not None and not filter(event):
            continue
        r.append(event)

    return r
            
    

class PlacelessSetup:

    def setUp(self):

        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService

        defineService("Events", IEventService)
        provideService("Events", eventService)
        
        del events[:]
        eventService.subscribe(EventRecorder)
