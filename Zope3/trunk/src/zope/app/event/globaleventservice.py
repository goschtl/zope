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
$Id: globaleventservice.py,v 1.2 2002/12/25 14:12:51 jim Exp $
"""

from zope.app.interfaces.event import IGlobalEventService
from zope.event.subscribable import Subscribable

class GlobalEventService(Subscribable):

    __implements__ = IGlobalEventService

    def globalSubscribe(self, *args, **kw):
        super(GlobalEventService, self).subscribe(*args, **kw)

    def subscribe(self, subscriber, event_type=None, filter=None):
        """Don't allow regular persistent subscriptions."""
        raise NotImplementedError("You cannot subscribe to the "
            "GlobalEventService. Use the 'globalSubscribe' method instead.")

    def publish(self, event):

        for subscriptions in self.subscriptionsForEvent(event):
            for subscriber, filter in subscriptions:
                if filter is not None and not filter(event):
                    continue
                subscriber.notify(event)


eventService = GlobalEventService()

_clear = eventService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
