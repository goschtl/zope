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
"""Class to create an event subscriber from a simple function.

$Id$
"""

from zope.interface import implements
from zope.app.event.interfaces import ISubscriber


class Subscriber:
    """Event subscriber that calls a function when an event is received.

    This is especially useful for creating subscribers from global
    functions that can be registered from ZCML:

        from zope.app.event import function

        def startupEventHandler(event):
            # do something useful with event:
            pass

        startupEventHandler = function.Subscriber(startupEventHandler)

    And then use this ZCML:

        <event:subscribe
            subscriber='.module.startupEventHandler'
            event_types='zope.app.event.interfaces.IProcessStartingEvent'
            />
    """
    implements(ISubscriber)

    def __init__(self, function):
        self.notify = function
