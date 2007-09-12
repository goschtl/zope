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
"""Serializers for Zope products

$Id$
"""

from apelib.core.interfaces import ISerializer
from apelib.core.schemas import RowSequenceSchema
from apelib.zodb3.serializers import find_unmanaged
from apelib.zope2.ofsserial import FolderItems


class BTreeFolder2Items:
    """BTreeFolder2 items (de)serializer
    """
    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('key', 'string', 1)
    schema.add('oid', 'string')
    schema.add('classification', 'classification')

    def can_serialize(self, obj):
        return hasattr(obj, '_tree')

    def serialize(self, event):
        obj = event.obj
        assert self.can_serialize(obj)
        state = []
        event.ignore('_objects')
        d = obj._tree
        event.ignore(('_tree', '_mt_index', '_count'))
        for id in obj.objectIds():
            base = d[id]
            oid = event.obj_db.identify(base)
            if oid is None:
                oid = event.obj_db.new_oid()
            event.referenced(id, base, True, oid)
            # No need to pass classification.
            state.append((id, oid, None))
        # The structure that makes up the BTree (the root node and
        # the buckets) are unmanaged.  Tell the event about them.
        event.upos.extend(find_unmanaged(obj._tree, obj._tree.values()))
        return state

    def deserialize(self, event, state):
        obj = event.obj
        if hasattr(obj, '_initBTrees'):
            # Version 1.0.1+ of BTreeFolder2
            obj._initBTrees()
        else:
            # Crufty workaround for older versions
            obj.__init__(obj.id)
        assert self.can_serialize(obj)
        for (id, oid, classification) in state:
            subob = event.resolve(id, oid, classification)
            obj._setOb(id, subob)
        # The tree and the buckets are unmanaged.
        event.upos.extend(find_unmanaged(obj._tree, obj._tree.values()))


class ContainerTabItems (FolderItems):
    """DCWorkflow.ContainerTab items (de)serializer"""
    
    def deserialize(self, event, state):
        # This object needs a little help with initialization
        event.obj._mapping = {}
        FolderItems.deserialize(self, event, state)

