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
"""Standard gateway classes.

$Id$
"""

import time

from interfaces import IGateway, OIDConflictError


class CompositeGateway:
    """Gateway that delegates to multiple smaller gateways."""

    __implements__ = IGateway
    schema = None

    def __init__(self, base=None):
        self._gws = {}
        if base is not None:
            self._gws.update(base._gws)
        self._update_schema()

    def _update_schema(self):
        self.schema = {}
        for name, gw in self._gws.items():
            s = gw.schema
            if s is not None:
                self.schema[name] = s

    def add(self, name, gw, force=0):
        if not force and self._gws.has_key(name):
            raise KeyError, "Gateway name %s in use" % name
        self._gws[name] = gw
        self._update_schema()

    def remove(self, name):
        del self._gws[name]  # raise KeyError if not in use
        self._update_schema()

    def has(self, name):
        return self._gws.has_key(name)

    def load(self, event):
        """Loads data.

        Returns a pair containing the data and an object
        that acts as a serial number or a hash of the data.
        The serial number is either a time stamp or some other object
        that can be consistently compared to detect conflicts.
        """
        full_state = {}
        serials = {}
        for name, gw in self._gws.items():
            state, serial = gw.load(event)
            if state is not None:
                full_state[name] = state
                if serial is not None:
                    serials[name] = serial
        serials = serials.items()
        serials.sort()
        return full_state, tuple(serials)

    def store(self, event, full_state):
        """Stores data.

        Returns a new serial.
        """
        serials = {}
        for name, gw in self._gws.items():
            state = full_state.get(name)
            # print 'gateway storing', event.oid, name, state
            serial = gw.store(event, state)
            if serial is not None:
                serials[name] = serial
        serials = serials.items()
        serials.sort()
        return tuple(serials)

    def get_sources(self, event):
        """Returns data source information.  See IGateway.
        """
        res = {}
        for gw in self._gws.values():
            sources = gw.get_sources(event)
            if sources is not None:
                res.update(sources)
        return res


class RAMGateway:
    """Gateway to a simple dictionary (primarily for testing).
    """
    __implements__ = IGateway
    schema = None

    def __init__(self, schema):
        self.schema = schema
        self.data = {}

    def load(self, event):
        # Returns (data, serial)
        return self.data[event.oid]

    def store(self, event, data):
        if event.is_new and self.data.has_key(event.oid):
            raise OIDConflictError(event.oid)
        h = time.time()
        self.data[event.oid] = (data, h)
        return h

    def get_sources(self, event):
        return None

