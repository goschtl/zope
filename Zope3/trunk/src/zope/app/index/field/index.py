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

$Id: index.py,v 1.11 2003/08/05 08:33:25 anthony Exp $
"""

from zope.component import getService, queryAdapter
from zope.app.services.servicenames import HubIds
from zope.context import ContextMethod
from zope.app.interfaces.event import ISubscriber
from zope.index.field.index import FieldIndex as FieldIndexWrapper
from zope.interface import implements

from zope.app.interfaces.services.hub import \
     IRegistrationHubEvent, \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent

from zope.app.interfaces.index.field import IUIFieldIndex, IUIFieldCatalogIndex
from zope.app.interfaces.catalog.index import ICatalogIndex
from zope.app.index import InterfaceIndexingSubscriber

class FieldCatalogIndex(InterfaceIndexingSubscriber, FieldIndexWrapper):
    implements(ICatalogIndex, IUIFieldCatalogIndex)

class FieldIndex(FieldCatalogIndex):

    implements(IUIFieldIndex)

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
