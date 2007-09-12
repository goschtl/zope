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
"""Basic filesystem gateways.

$Id$
"""

from types import StringType

from apelib.core.interfaces import IGateway, LoadError
from apelib.core.schemas import ColumnSchema, RowSequenceSchema

from base import FSGatewayBase


class FSFileData (FSGatewayBase):
    """File data gateway, where data is a string.
    """

    __implements__ = IGateway

    schema = ColumnSchema('data', 'string')

    def __init__(self, text=0, conn_name='fs'):
        if text == 'text':
            text = 1
        elif text == 'binary':
            text = 0
        self.text = text
        FSGatewayBase.__init__(self, conn_name)

    def load(self, event):
        c = self.get_connection(event)
        assert c.read_node_type(event.oid) == 'f'
        state = c.read_data(event.oid, as_text=self.text)
        return state, state

    def store(self, event, state):
        if not isinstance(state, StringType):
            raise ValueError('Not a string: %s' % repr(state))
        c = self.get_connection(event)
        c.write_node_type(event.oid, 'f')
        c.write_data(event.oid, state, as_text=self.text)
        return state


class FSAutoId (FSGatewayBase):
    """Automatic ID gateway based on the object name in the primary parent.
    """

    __implements__ = IGateway

    schema = ColumnSchema('id', 'string')

    def load(self, event):
        id = self.get_connection(event).read_object_name(event.oid)
        # Disable conflict checking by returning None as the hash value.
        return id, None

    def store(self, event, state):
        # Ignore.
        return None

    def get_sources(self, event):
        fs_conn = self.get_connection(event)
        return fs_conn.get_sources(event.oid)


class FSDirectoryItems (FSGatewayBase):
    """Read/write objects in a filesystem directory."""

    __implements__ = IGateway

    schema = RowSequenceSchema()
    schema.add('key', 'string', 1)
    schema.add('oid', 'string')
    schema.add('classification', 'classification')

    def load(self, event):
        c = self.get_connection(event)
        if c.read_node_type(event.oid) != 'd':
            raise LoadError("Not a directory")
        data = list(c.read_directory(event.oid))
        data.sort()
        # Assign OIDs to previously existing subobjects.
        assigned = {}
        for objname, child_oid in data:
            if child_oid is None:
                child_oid = event.conf.oid_gen.new_oid(event)
                assigned[objname] = child_oid
        if assigned:
            # Saw existing objects.  Tell the connection what their OIDs are.
            c.assign_existing(event.oid, assigned.items())
        # Return the results.
        res = []
        hash_value = []
        for objname, child_oid in data:
            if child_oid is None:
                child_oid = assigned[objname]
            classification = event.classify(child_oid)
            # Return info about each subobject.
            res.append((objname, child_oid, classification))
            hash_value.append((objname, child_oid))
        return res, tuple(hash_value)

    def store(self, event, state):
        c = self.get_connection(event)
        c.write_node_type(event.oid, 'd')
        data = []
        for objname, child_oid, classification in state:
            data.append((objname, child_oid))
        data.sort()
        c.write_directory(event.oid, data)
        return tuple(data)


class FSModTime (FSGatewayBase):
    """Reads the modification time of a file."""

    __implements__ = IGateway

    schema = ColumnSchema('mtime', 'int')

    def load(self, event):
        fs_conn = self.get_connection(event)
        state = long(fs_conn.read_mod_time(event.oid))
        return state, None  # Use None as the hash (see store())

    def store(self, event, state):
        # Under normal circumstances, there is no need to change the mod
        # time of a file.  Ignore by returning None as the hash.
        return None


def root_mapping():
    """Returns a gateway suitable for storing the root persistent mapping.
    """
    from apelib.core.gateways import CompositeGateway
    from properties import FSAnnotationData
    g = CompositeGateway()
    g.add('references', FSDirectoryItems())
    g.add('others', FSAnnotationData('others'))
    return g
