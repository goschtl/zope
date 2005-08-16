##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Event channel class for observable events.

$Id: observerevent.py,v 1.1 2004/03/30 21:47:38 nathan Exp $
"""

from zope.app.event.interfaces import ISubscriber
from zope.app.observable.interfaces import IObservable
from zope.interface import implements

class ObserverEventNotifier:

    implements(ISubscriber)

    def notify (self, event):
        adapter = IObservable(event.object, None)

        if adapter is not None:
            adapter.notify(event, ISubscriber)

observerEventNotifierInstance = ObserverEventNotifier()

