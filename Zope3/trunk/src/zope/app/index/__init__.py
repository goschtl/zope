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
"""
$Id: __init__.py,v 1.7 2004/03/02 18:51:00 philikon Exp $
"""

from zope.interface import implements
from zope.app.index.interfaces import IInterfaceIndexer
from zope.app.event.interfaces import ISubscriber
from zope.component import queryAdapter

from zope.app.interfaces.services.hub import \
     IObjectRegisteredHubEvent, \
     IObjectUnregisteredHubEvent, \
     IObjectModifiedHubEvent


class InterfaceIndexingSubscriber(object):
    """Mixin for indexing a particular field name, after first adapting the
       object to be indexed to an interface.
    """
    implements(IInterfaceIndexer, ISubscriber)
    default_field_name = None
    default_interface = None

    def __init__(self, field_name=None, interface=None):
        super(InterfaceIndexingSubscriber, self).__init__()
        if field_name is None and self.default_field_name is None:
            raise ValueError, "Must pass a field_name"
        if field_name is None:
            self._field_name = self.default_field_name
        else:
            self._field_name = field_name
        if interface is None:
            self._interface = self.default_interface
        else:
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

