##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""This is a keyword index which can be subscribed to an event service.

Events related to object creation and deletion are translated into
index_doc() and unindex_doc() calls.

This (along with field and text indexes) should be refactored to abstract
out the common code.

$Id: index.py,v 1.1 2003/08/03 05:41:10 anthony Exp $
"""

from zope.component import getService, queryAdapter
from zope.app.services.servicenames import HubIds
from zope.context import ContextMethod
from zope.app.interfaces.event import ISubscriber
from zope.index.keyword.index import KeywordIndex 
from zope.interface import implements

from zope.app.interfaces.services.hub import \
     IRegistrationHubEvent, \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent

from zope.app.interfaces.index.keyword import IUIKeywordCatalogIndex
from zope.app.interfaces.catalog.index import ICatalogIndex

class KeywordCatalogIndex(KeywordIndex):

    implements(ISubscriber, ICatalogIndex, IUIKeywordCatalogIndex)

    def __init__(self, field_name, interface=None):
        KeywordIndex.__init__(self)
        self._field_name = field_name
        self._interface = interface

    field_name = property(lambda self: self._field_name)
    interface = property(lambda self: self._interface)

    def _getValue(self, object):
        if self._interface is not None:
            object = queryAdapter(object, self._interface)
            if object is None: return None

        value = getattr(object, self._field_name, None)
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

