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
"""Placeless Test Setup

$Id$
"""
import zope.component
from zope.component.event import objectEventNotify
from zope.testing import cleanup

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
cleanup.addCleanUp(clearEvents)

class PlacelessSetup(cleanup.CleanUp):

    def setUp(self):
        super(PlacelessSetup, self).setUp()
        zope.component.provideHandler(events.append, (None,))
        zope.component.provideHandler(objectEventNotify)

def setUp(test=None):
    PlacelessSetup().setUp()

def tearDown(test=None):
    PlacelessSetup().tearDown()
