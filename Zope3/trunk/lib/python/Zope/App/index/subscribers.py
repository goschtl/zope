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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: subscribers.py,v 1.1 2002/12/05 13:47:43 stevea Exp $
"""
__metaclass__ = type

from Interface import Interface
from Zope.Event.ISubscriber import ISubscriber
from Zope.Event.IObjectEvent import IObjectAddedEvent
from Zope.ContextWrapper import ContextMethod
from Persistence import Persistent
from Zope.ComponentArchitecture import getService

class ISubscriptionControl(Interface):
    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

class Registration(Persistent):

    __implements__ = ISubscriptionControl, ISubscriber

    def notify(wrapped_self, event):
        """An event occured. Perhaps register this object with the hub."""
        getService(wrapped_self, "ObjectHub").register(event.object)
    notify = ContextMethod(notify)

    currentlySubscribed = False # Default subscription state

    def subscribe(wrapped_self):
        if wrapped_self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        channel = wrapped_self._getChannel(None)
        channel.subscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = True
    subscribe = ContextMethod(subscribe)

    def unsubscribe(wrapped_self):
        if not wrapped_self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = wrapped_self._getChannel(None)
        channel.unsubscribe(wrapped_self, IObjectAddedEvent)
        wrapped_self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(wrapped_self, channel):
        if channel is None:
            channel = getService(wrapped_self, "ObjectHub")
        return channel
    _getChannel = ContextMethod(_getChannel)

