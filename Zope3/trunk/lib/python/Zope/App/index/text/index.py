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

$Id: index.py,v 1.4 2002/12/04 17:11:51 gvanrossum Exp $
"""

from Zope.Event.ISubscriber import ISubscriber

from Zope.ComponentArchitecture import getService

from Zope.App.OFS.Services.ObjectHub.IHubEvent import \
     IRegistrationHubEvent, \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent

from Zope.App.index.text.interfaces import ISearchableText, IUITextIndex

from Zope.ComponentArchitecture import queryAdapter
from Zope.ContextWrapper import ContextMethod

from Zope.TextIndex.TextIndexWrapper import TextIndexWrapper

class TextIndex(TextIndexWrapper):

    __implements__ = TextIndexWrapper.__implements__ + (ISubscriber,
                                                        IUITextIndex)

    def notify(wrapped_self, event):
        """An event occurred.  Index or unindex the object in response."""
        if (IObjectRegisteredHubEvent.isImplementedBy(event) or
            IObjectModifiedHubEvent.isImplementedBy(event)):
            texts = wrapped_self._getTexts(event.object)
            if texts is not None:
                wrapped_self.index_doc(event.hubid, texts)
        elif IObjectUnregisteredHubEvent.isImplementedBy(event):
            try:
                wrapped_self.unindex_doc(event.hubid)
            except KeyError:
                pass
    notify = ContextMethod(notify)

    def _getTexts(wrapped_self, object):
        adapted = queryAdapter(object, ISearchableText, context=wrapped_self)
        if adapted is None:
            return None
        return adapted.getSearchableText()
    _getTexts = ContextMethod(_getTexts)

    def subscribe(wrapped_self, channel=None, update=True):
        channel = wrapped_self._getChannel(channel)
        channel.subscribe(wrapped_self, IRegistrationHubEvent)
        channel.subscribe(wrapped_self, IObjectModifiedHubEvent)
        if update:
            wrapped_self._update(channel.iterObjectRegistrations()) 
    subscribe = ContextMethod(subscribe)

    def unsubscribe(wrapped_self, channel=None):
        channel = wrapped_self._getChannel(channel)
        channel.unsubscribe(wrapped_self, IObjectModifiedHubEvent)
        channel.unsubscribe(wrapped_self, IRegistrationHubEvent)
    unsubscribe = ContextMethod(unsubscribe)

    def _getChannel(wrapped_self, channel):
        if channel is None:
            channel = getService(wrapped_self, "ObjectHubService")
        return channel
    _getChannel = ContextMethod(_getChannel)

    def _update(wrapped_self, registrations):
        for location, hubid, wrapped_object in registrations:
            texts = wrapped_self._getTexts(wrapped_object)
            if texts is not None:
                wrapped_self.index_doc(hubid, texts)
    _update = ContextMethod(_update)
