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

$Id: index.py,v 1.3 2002/12/28 17:49:26 stevea Exp $
"""

from zope.component import getService, queryAdapter
from zope.proxy.context import ContextMethod
from zope.interfaces.event import ISubscriber
from zope.exceptions import NotFoundError
from zope.textindex.textindexwrapper import TextIndexWrapper

from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.services.hub import \
     IRegistrationHubEvent, \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent
from zope.app.traversing import locationAsUnicode
from zope.app.interfaces.index.text import ISearchableText
from zope.app.interfaces.index.text import IUITextIndex

class TextIndex(TextIndexWrapper):

    __implements__ = (TextIndexWrapper.__implements__,
                      ISubscriber, IUITextIndex)

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
    subscribe = ContextMethod(subscribe)

    def unsubscribe(wrapped_self, channel=None):
        if not wrapped_self.currentlySubscribed:
            raise RuntimeError, "not subscribed; please subscribe first"
        channel = wrapped_self._getChannel(channel)
        channel.unsubscribe(wrapped_self, IObjectModifiedHubEvent)
        channel.unsubscribe(wrapped_self, IRegistrationHubEvent)
        wrapped_self.currentlySubscribed = False
    unsubscribe = ContextMethod(unsubscribe)

    def isSubscribed(self):
        return self.currentlySubscribed

    def _getChannel(wrapped_self, channel):
        if channel is None:
            channel = getService(wrapped_self, "ObjectHub")
        return channel
    _getChannel = ContextMethod(_getChannel)

    def _update(wrapped_self, registrations):
        for location, hubid, wrapped_object in registrations:
            texts = wrapped_self._getTexts(wrapped_object)
            if texts is not None:
                wrapped_self.index_doc(hubid, texts)
    _update = ContextMethod(_update)
