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

$Id$
"""

from zope.app.event.interfaces import IObjectEvent
from zope.app.event.objectevent import objectEventNotify
from zope.interface import implements
from zope.component import getGlobalServices
from zope.app.tests import ztapi

events = []

def getEvents(event_type=None, filter=None):
    r = []
    for event in events:
        if event_type is not None and not event_type.providedBy(event):
            continue
        if filter is not None and not filter(event):
            continue
        r.append(event)

    return r

def clearEvents():
    del events[:]

class PlacelessSetup:

    def setUp(self):
        clearEvents()
        ztapi.handle([None], events.append)
        ztapi.handle([IObjectEvent], objectEventNotify)

import zope.testing.cleanup
zope.testing.cleanup.addCleanUp(clearEvents)
