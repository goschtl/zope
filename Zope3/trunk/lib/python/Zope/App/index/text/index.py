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

$Id: index.py,v 1.1 2002/12/04 11:10:24 gvanrossum Exp $
"""

from Zope.Event.ISubscriber import ISubscriber

from Zope.App.OFS.Services.ObjectHub.IHubEvent import \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent

from Zope.App.index.text.interfaces import ISearchableText

from Zope.ComponentArchitecture import queryAdapter
from Zope.ContextWrapper import ContextMethod

from Zope.TextIndex.TextIndexWrapper import TextIndexWrapper

class TextIndex(TextIndexWrapper):

    __implements__ = TextIndexWrapper.__implements__ + (ISubscriber,)

    def notify(wrapped_self, event):
        """An event occurred.  Index or unindex the object in response."""
        if (IObjectRegisteredHubEvent.isImplementedBy(event) or
            IObjectModifiedHubEvent.isImplementedBy(event)):
            adapted = queryAdapter(event.object,
                                   ISearchableText,
                                   context=wrapped_self)
            if adapted is None:
                return
            texts = adapted.getSearchableText()
            wrapped_self.index_doc(event.hubid, texts)
        elif IObjectUnregisteredHubEvent.isImplementedBy(event):
            try:
                wrapped_self.unindex_doc(event.hubid)
            except KeyError:
                pass
    notify = ContextMethod(notify)
