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

$Id: index.py,v 1.18 2004/03/13 23:55:05 srichter Exp $
"""
from zope.component import getService
from zope.app.servicenames import HubIds
from zope.index.field.index import FieldIndex as FieldIndexWrapper
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.app.hub.interfaces import IObjectModifiedHubEvent
from zope.app.hub.interfaces import IRegistrationHubEvent
from zope.app.index.interfaces.field import IUIFieldIndex, IUIFieldCatalogIndex
from zope.app.catalog.interfaces.index import ICatalogIndex
from zope.app.index import InterfaceIndexingSubscriber

class FieldCatalogIndex(InterfaceIndexingSubscriber, FieldIndexWrapper,
                        Contained):
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

    def unsubscribe(self, channel=None):
        if not self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = self._getChannel(channel)
        channel.unsubscribe(self, IObjectModifiedHubEvent)
        channel.unsubscribe(self, IRegistrationHubEvent)
        self.currentlySubscribed = False

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(self, channel):
        if channel is None:
            channel = getService(self, HubIds)
        return channel

    def _update(self, registrations):
        for location, hubid, wrapped_object in registrations:
            value = self._getValue(wrapped_object)
            if value is not None:
                self.index_doc(hubid, value)
