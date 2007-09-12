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
"""Standard event implementations

$Id$
"""

import interfaces


SIMPLE_IMMUTABLE_OBJECTS = (None, (), 0, 1, '', u'', False, True)


class DatabaseInitEvent:
    """Database initialization event.
    """
    __implements__ = interfaces.IDatabaseInitEvent
    connections = None
    clear_all = False

    def __init__(self, connections, clear_all):
        self.connections = connections
        self.clear_all = clear_all


class MapperEvent:
    __implements__ = interfaces.IMapperEvent
    conf = None
    mapper = None
    oid = ""
    classification = None

    def __init__(self, conf, mapper, oid, classification):
        self.conf = conf
        self.mapper = mapper
        self.oid = oid
        self.classification = classification


class GatewayEvent (MapperEvent):
    __implements__ = interfaces.IGatewayEvent
    connections = None

    def __init__(self, conf, mapper, oid, classification, connections):
        MapperEvent.__init__(self, conf, mapper, oid, classification)
        self.connections = connections


class LoadEvent (GatewayEvent):
    """Object loading event.
    """
    __implements__ = interfaces.ILoadEvent

    def classify(self, oid):
        sub_event = LoadEvent(self.conf, None, oid, None, self.connections)
        return self.conf.classifier.classify_state(sub_event)


class StoreEvent (GatewayEvent):
    """Object storing event.
    """
    __implements__ = interfaces.IStoreEvent
    is_new = False

    def __init__(self, conf, mapper, oid, classification, connections, is_new):
        GatewayEvent.__init__(
            self, conf, mapper, oid, classification, connections)
        self.is_new = is_new


class SDEvent (MapperEvent):
    __implements__ = interfaces.ISDEvent
    obj_db = None
    obj = None
    serializer_name = ""
    upos = None
    external = None

    def __init__(self, conf, mapper, oid, classification, obj_db, obj):
        MapperEvent.__init__(self, conf, mapper, oid, classification)
        self.obj_db = obj_db
        self.obj = obj
        self.upos = []
        # self.external has the form [(oid, subobject)]
        self.external = []


class DeserializationEvent (SDEvent):
    __implements__ = interfaces.IFullDeserializationEvent

    def __init__(self, conf, mapper, oid, classification, obj_db, obj):
        SDEvent.__init__(self, conf, mapper, oid, classification, obj_db, obj)
        self._loaded_refs = {}  # { (serializer_name, name) -> object }

    # IDeserializationEvent interface methods:

    def deserialized(self, name, value):
        self._loaded_refs['%s:%s' % (self.serializer_name, name)] = value

    def resolve(self, name, oid, classification=None):
        """Retrieves a referenced subobject (usually ghosted initially).
        """
        ob = self.obj_db.get(oid, classification)
        self.external.append((oid, ob))
        self.deserialized(name, ob)
        return ob

    # IFullDeserializationEvent interface methods:

    def resolve_internal(self, ref):
        """Returns an object already deserialized by another serializer.

        'ref' is a tuple containing (serializer_name, name).
        """
        return self._loaded_refs[ref]


class SerializationEvent (SDEvent):
    __implements__ = interfaces.IFullSerializationEvent

    def __init__(self, conf, mapper, oid, classification, obj_db, obj):
        SDEvent.__init__(self, conf, mapper, oid, classification, obj_db, obj)
        self._attrs = {}
        # _internal_refs:
        # id(ob) -> (serializer_name, name)
        self._internal_refs = {}
        # _internal_ref_list contains all objects that may be referenced
        # internally.  This only ensures that id(ob) stays consistent.
        self._internal_ref_list = []

    # ISerializationEvent interface methods:

    def serialized(self, name, value, is_attribute):
        """See the ISerializationEvent interface."""
        for ob in SIMPLE_IMMUTABLE_OBJECTS:
            # If value is a simple immutable object, don't make a
            # reference to it.  Compare by identity rather than
            # equality, otherwise rich comparison leads to surprises.
            if value is ob:
                break
        else:
            # Make internal references only for mutable or complex objects.
            idx = id(value)
            if not self._internal_refs.has_key(idx):
                self._internal_ref_list.append(value)
                if name is not None:
                    self._internal_refs[idx] = (
                        '%s:%s' % (self.serializer_name, name))
                else:
                    self._internal_refs[idx] = None
        if is_attribute and name is not None:
            self._attrs[name] = 1

    def referenced(self, name, value, is_attribute, oid):
        assert oid is not None
        self.external.append((oid, value))
        self.serialized(name, value, is_attribute)

    def ignore(self, name_or_names):
        if isinstance(name_or_names, (str, unicode)):
            self._attrs[name_or_names] = 1
        else:
            for name in name_or_names:
                self._attrs[name] = 1


    # IFullSerializationEvent interface methods:

    def get_seralized_attributes(self):
        """Returns the name of all attributes serialized."""
        return self._attrs.keys()

    def identify_internal(self, ob):
        """Returns (serializer_name, name) or None."""
        return self._internal_refs.get(id(ob))
