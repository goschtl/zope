##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Process-lifetime related events.

$Id$
"""

from zope.interface import implements
from zope.app.event.interfaces import \
     IDatabaseOpenedEvent, IProcessStartingEvent

class DatabaseOpened:
    implements(IDatabaseOpenedEvent)

    def __init__(self, database):
        self.database = database

class ProcessStarting:
    implements(IProcessStartingEvent)
