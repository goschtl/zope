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
"""This is a field index which can be subscribed to an event service.

Events related to object creation and deletion are translated into
index_doc() and unindex_doc() calls.

In addition, this implements TTW subscription management.

$Id: index.py,v 1.2 2003/03/26 16:25:18 andreasjung Exp $
"""

from zope.component import getService, queryAdapter
from zope.app.services.servicenames import HubIds
from zope.proxy.context import ContextMethod
from zope.app.interfaces.event import ISubscriber
from zope.exceptions import NotFoundError
from zope.fieldindex.fieldindex import FieldIndex as FieldIndexWrapper

from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.services.hub import \
     IRegistrationHubEvent, \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent

from zope.app.interfaces.index.field  import IUIFieldIndex

class FieldIndex(FieldIndexWrapper):

    __implements__ = (FieldIndexWrapper.__implements__,
                      ISubscriber, IUIFieldIndex)

    def __init__(self, indexed_attr):
        FieldIndexWrapper.__init__(self)
        self._indexed_attr = indexed_attr


    def _getValue(self, object):

        value = getattr(object, self._indexed_attr, None)
        if value is None: return None

        if callable(value): 
            try: value = value()
            except: return None

        return value


    def notify(self, event):
        """An event occurred.  Index or unindex the object in response."""

        if (IObjectRegisteredHubEvent.isImplementedBy(event) or
            IObjectModifiedHubEvent.isImplementedBy(event)):
            value = self._getValue(event.object)
            if value is not None:
                self.index_doc(event.hubid, value)
        elif IObjectUnregisteredHubEvent.isImplementedBy(event):
            try:
                self.unindex_doc(event.hubid)
            except KeyError:
                pass
    notify = ContextMethod(notify)

    currentlySubscribed = False # Default subscription state

    def subscribe(self, channel=None, update=True):
        if self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        channel = self._getChannel(channel)
        channel.subscribe(self, IRegistrationHubEvent)
        channel.subscribe(self, IObjectModifiedHubEvent)
        if update:
            self._update(channel.iterObjectRegistrations())
        self.currentlySubscribed = True
    subscribe = ContextMethod(subscribe)

    def unsubscribe(self, channel=None):
        if not self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = self._getChannel(channel)
        channel.unsubscribe(self, IObjectModifiedHubEvent)
        channel.unsubscribe(self, IRegistrationHubEvent)
        self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(self, channel):
        if channel is None:
            channel = getService(self, HubIds)
        return channel
    _getChannel = ContextMethod(_getChannel)

    def _update(self, registrations):
        for location, hubid, wrapped_object in registrations:
            value = self._getValue(wrapped_object)
            if value is not None:
                self.index_doc(hubid, value)
    _update = ContextMethod(_update)
