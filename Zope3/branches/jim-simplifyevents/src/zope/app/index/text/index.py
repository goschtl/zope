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
"""This is a text index which can be subscribed to an event service.

Events related to object creation and deletion are translated into
index_doc() and unindex_doc() calls.

In addition, this implements TTW subscription management.

$Id$
"""
from zope.component import getService
from zope.app.servicenames import HubIds
from zope.app.container.contained import Contained
from zope.index.text.textindexwrapper import TextIndexWrapper

from zope.app.hub.interfaces import \
     IRegistrationHubEvent, IObjectModifiedHubEvent
from zope.app.index.interfaces.text import ISearchableText
from zope.app.index.interfaces.text import IUITextIndex, IUITextCatalogIndex
from zope.interface import implements
from zope.app.index import InterfaceIndexingSubscriber
from zope.app.catalog.interfaces.index import ICatalogIndex


class TextCatalogIndex(InterfaceIndexingSubscriber, TextIndexWrapper,
                       Contained):
    implements(ICatalogIndex, IUITextCatalogIndex)

    default_interface = ISearchableText
    default_field_name = "getSearchableText"

class TextIndex(TextCatalogIndex):

    implements(IUITextIndex)

    currentlySubscribed = False # Default subscription state

    def subscribe(wrapped_self, channel=None, update=True):
        if wrapped_self.currentlySubscribed:
            raise RuntimeError, "already subscribed; please unsubscribe first"
        channel = wrapped_self._getChannel(channel)
        channel.subscribe(wrapped_self, IRegistrationHubEvent)
        channel.subscribe(wrapped_self, IObjectModifiedHubEvent)
        if update:
            wrapped_self._update(channel.iterObjectRegistrations())
        wrapped_self.currentlySubscribed = True

    def unsubscribe(wrapped_self, channel=None):
        if not wrapped_self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = wrapped_self._getChannel(channel)
        channel.unsubscribe(wrapped_self, IObjectModifiedHubEvent)
        channel.unsubscribe(wrapped_self, IRegistrationHubEvent)
        wrapped_self.currentlySubscribed = False

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(wrapped_self, channel):
        if channel is None:
            channel = getService(wrapped_self, HubIds)
        return channel

    def _update(wrapped_self, registrations):
        for location, hubid, wrapped_object in registrations:
            texts = wrapped_self._getValue(wrapped_object)
            if texts is not None:
                wrapped_self.index_doc(hubid, texts)

