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
"""Ape I/O facades.

These facades implement commonly useful high-level mapper operations.

$Id$
"""

from weakref import proxy

from events import DatabaseInitEvent, GatewayEvent, LoadEvent, StoreEvent
from events import SerializationEvent, DeserializationEvent
from interfaces import IMapperConfiguration, ITPCConnection, IObjectDatabase
from interfaces import LoadError


class GatewayIO:
    """Gateway operations facade."""

    def __init__(self, conf, connections):
        assert IMapperConfiguration.isImplementedBy(conf), conf
        self.conf = conf
        self.conn_map = connections
        # Sort the connections by sort key.  Use an extra index to avoid
        # using connections as sort keys.
        items = []  # [(sort_key, index, conn)]
        index = 0
        for c in connections.values():
            assert ITPCConnection.isImplementedBy(c)
            sort_key = c.sortKey()
            items.append((sort_key, index, c))
            index += 1
        items.sort()
        conn_list = []
        for sort_key, index, c in items:
            conn_list.append(c)
        self.conn_list = conn_list

    def open_connections(self):
        try:
            opened = []
            for c in self.conn_list:
                c.connect()
                opened.append(c)
        except:
            for c in opened:
                c.close()
            raise

    def close_connections(self):
        for conn in self.conn_list:
            conn.close()

    def get_connection_list(self):
        return self.conn_list

    def get_connection_map(self):
        return self.conn_map

    def init_databases(self, clear_all=0):
        """Creates tables, etc.
        """
        # Find all initializers, eliminating duplicates.
        initializers = {}  # obj -> 1
        for mapper in self.conf.mappers.values():
            for obj in mapper.initializers:
                initializers[obj] = 1
        for obj in self.conf.initializers:
            initializers[obj] = 1
            
        # Now call them.
        event = DatabaseInitEvent(self.conn_map, clear_all)
        for initializer in initializers.keys():
            initializer.init(event)

    def classify_state(self, oid):
        event = LoadEvent(self.conf, None, oid, None, self.conn_map)
        # Returns classification
        return self.conf.classifier.classify_state(event)

    def load(self, oid):
        classification = self.classify_state(oid)
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = LoadEvent(
            self.conf, mapper, oid, classification, self.conn_map)
        state, hash_value = mapper.gateway.load(event)
        return event, classification, state, hash_value

    def store(self, oid, classification, state, is_new):
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = StoreEvent(
            self.conf, mapper, oid, classification, self.conn_map, is_new)
        # Store the classification first
        self.conf.classifier.gateway.store(event, classification)
        # Store the state second
        new_hash = mapper.gateway.store(event, state)
        return event, new_hash

    def get_sources(self, oid):
        try:
            classification = self.classify_state(oid)
        except LoadError:
            # Doesn't exist.
            return {}
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = LoadEvent(
            self.conf, mapper, oid, classification, self.conn_map)
        return mapper.gateway.get_sources(event)

    def new_oid(self):
        event = GatewayEvent(self.conf, None, None, None, self.conn_map)
        return self.conf.oid_gen.new_oid(event)



class ObjectSystemIO:
    """Object system (de)serialization facade."""

    def __init__(self, conf, obj_db):
        assert IMapperConfiguration.isImplementedBy(conf), conf
        assert IObjectDatabase.isImplementedBy(obj_db), obj_db
        self.conf = conf
        self.obj_db = obj_db

    def classify_object(self, obj, oid):
        event = SerializationEvent(
            self.conf, None, oid, None, self.obj_db, obj)
        # Returns classification
        return self.conf.classifier.classify_object(event)

    def serialize(self, oid, obj):
        classification = self.classify_object(obj, oid)
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = SerializationEvent(
            self.conf, mapper, oid, classification, self.obj_db, obj)
        state = mapper.serializer.serialize(event)
        return event, classification, state

    def deserialize(self, oid, obj, classification, state):
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = DeserializationEvent(
            self.conf, mapper, oid, classification, self.obj_db, obj)
        mapper.serializer.deserialize(event, state)
        return event

    def new_instance(self, oid, classification):
        mapper_name = classification['mapper_name']
        mapper = self.conf.mappers[mapper_name]
        event = DeserializationEvent(
            self.conf, mapper, oid, classification, self.obj_db, None)
        return mapper.serializer.new_instance(event)



class ExportImport:
    """Simple import/export facade.
    """
    __implements__ = IObjectDatabase

    def __init__(self, conf, connections, class_factory=None):
        self._objects = {}     # { oid -> obj }
        self._oids = {}   # { id(obj) -> oid }
        # _incomplete contains the oids of objects not yet
        # imported fully.
        self._incomplete = {}   # { oid -> 1 }
        self._class_factory = class_factory
        # Avoid a circular reference by making a weakref proxy
        self.obj_io = ObjectSystemIO(conf, proxy(self))
        self.gw_io = GatewayIO(conf, connections)


    def _register(self, oid, obj):
        """Registers obj in the temporary object index.

        Returns true if the object was added to the index for the first
        time.  If the registration conflicts, raises an exception.
        """
        is_new = 0
        if self._objects.has_key(oid):
            if self._objects[oid] is not obj:
                raise ValueError, (
                    "Multiple objects for oid %s" % repr(oid))
        else:
            self._objects[oid] = obj
            is_new = 1
        obj_id = id(obj)
        if self._oids.has_key(obj_id):
            if self._oids[obj_id] != oid:
                raise ValueError, (
                    "Multiple oids for object %s" % repr(obj))
        else:
            self._oids[obj_id] = oid
            is_new = 1
        return is_new


    def export_object(self, src_obj, dest_oid=None, deactivate_func=None):
        count = 0
        if dest_oid is None:
            dest_oid = self.new_oid()
        self._register(dest_oid, src_obj)
        # Export subobjects.
        todo = [(dest_oid, src_obj)]
        while todo:
            oid, obj = todo.pop()
            event, classification, state = self.obj_io.serialize(oid, obj)
            count += 1
            if deactivate_func is not None:
                deactivate_func(obj, count)
            self.gw_io.store(oid, classification, state, False)
            ext_refs = event.external
            if ext_refs:
                for ext_oid, ext_obj in ext_refs:
                    if self._register(ext_oid, ext_obj):
                        todo.append((ext_oid, ext_obj))


    def import_object(self, src_oid, dest_obj=None, commit_func=None):
        count = 0
        if dest_obj is None:
            dest_obj = self.get(src_oid)
        root_obj = dest_obj
        self._register(src_oid, dest_obj)
        # Import subobjects.
        todo = [(src_oid, dest_obj)]
        while todo:
            oid, obj = todo.pop()
            e, classification, state, hash_value = self.gw_io.load(oid)
            event = self.obj_io.deserialize(oid, obj, classification, state)
            if self._incomplete.has_key(oid):
                del self._incomplete[oid]
            count += 1
            if commit_func is not None:
                commit_func(obj, count)
            ext_refs = event.external
            if ext_refs:
                for ext_oid, ext_obj in ext_refs:
                    if (self._register(ext_oid, ext_obj)
                        or self._incomplete.has_key(ext_oid)):
                        todo.append((ext_oid, ext_obj))
        return root_obj


    # IObjectDatabase implementation

    def get_class(self, module, name):
        # Normally called only while importing
        if self._class_factory is not None:
            return self._class_factory.get_class(module, name)
        else:
            m = __import__(module, {}, {}, ('__doc__',))
            return getattr(m, name)

    def get(self, oid, classification=None):
        # Should be called only while importing
        try:
            return self._objects[oid]
        except KeyError:
            # This object has not been loaded yet.  Make a stub.
            e, classification, state, hash_value = self.gw_io.load(oid)
            obj = self.obj_io.new_instance(oid, classification)
            # Don't fill in the state yet, to avoid infinite
            # recursion.  Just register it.
            self._incomplete[oid] = 1
            self._register(oid, obj)
            return obj

    def identify(self, obj):
        # Normally called only while exporting
        return self._oids.get(id(obj))

    def new_oid(self):
        # Should be called only while exporting
        return self.gw_io.new_oid()
