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
"""Serializers for OFSP (object file system product) objects

$Id$
"""

from cPickle import dumps, loads
from types import DictType

from Acquisition import aq_base
from OFS.SimpleItem import Item_w__name__
from OFS.ObjectManager import ObjectManager
from OFS.Image import File
from OFS.PropertyManager import PropertyManager

from apelib.core.interfaces import ISerializer, SerializationError
from apelib.core.schemas import ColumnSchema, RowSequenceSchema
from apelib.core.serializers import OptionalSerializer


string_repr_types = {
    # Properties that are safe to render as strings for storage.
    # Other kinds of properties get pickled.
    'string': 1,
    'float': 1,
    'int': 1,
    'long': 1,
    'date': 1,
    'date_international': 1,
    'text': 1,
    'boolean': 1,
}


class FilePData:
    """Serializer of the 'data' attribute of OFS.File and OFS.Image"""

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'string')

    def can_serialize(self, object):
        return isinstance(object, File)

    def serialize(self, event):
        obj = event.obj
        event.serialized('data', obj.data, 1)
        event.ignore(('size', 'width', 'height'))
        return str(obj.data)

    def deserialize(self, event, state):
        obj = event.obj
        data, size = obj._read_data(state)
        if not obj.__dict__.get('content_type'):
            # Guess the content type.
            content_type = obj._get_content_type(
                state, data, obj.__name__)
        else:
            # The properties serializer is authoritative.  Defer to it.
            content_type = None
        obj.update_data(data, content_type, size)
        event.deserialized('data', obj.data)


class FolderItems:
    """Zope 2 folder items (de)serializer
    """
    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('key', 'string', 1)
    schema.add('oid', 'string')
    schema.add('classification', 'classification')

    def can_serialize(self, obj):
        return isinstance(obj, ObjectManager)

    def serialize(self, event):
        obj = event.obj
        assert isinstance(obj, ObjectManager), repr(obj)
        state = []
        event.ignore('_objects')
        d = obj.__dict__
        for id in obj.objectIds():
            if d.has_key(id):
                base = d[id]
            else:
                # Fall back to _getOb.
                base = aq_base(obj._getOb(id))
            oid = event.obj_db.identify(base)
            if oid is None:
                oid = event.obj_db.new_oid()
            event.referenced(id, base, True, oid)
            # No need to pass classification.
            state.append((id, oid, None))
        return state

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(obj, ObjectManager), obj
        for (id, oid, classification) in state:
            subob = event.resolve(id, oid, classification)
            obj._setOb(id, subob)
            obj._objects += ({
                'id': id,
                'meta_type': subob.__class__.meta_type,
                },)


class IdAttribute:
    """Zope 2 id attribute."""

    __implements__ = ISerializer

    schema = ColumnSchema('id', 'string')

    def can_serialize(self, obj):
        return 1

    def _get_attr_name_for(self, obj):
        if isinstance(obj, Item_w__name__):
            return '__name__'
        else:
            return 'id'

    def serialize(self, event):
        obj = event.obj
        attrname = self._get_attr_name_for(obj)
        id = getattr(obj, attrname)
        if not id:
            raise SerializationError('ID of %r is %r' % (obj, id))
        event.serialized(attrname, id, 1)
        return id

    def deserialize(self, event, state):
        obj = event.obj
        attrname = self._get_attr_name_for(obj)
        setattr(obj, attrname, state)
        # Allow references under either attribute name.
        event.deserialized('id', state)
        event.deserialized('__name__', state)


class AutoBindings:
    """For classes that extend Shared.DC.Scripts.Bindings.Bindings.

    Discards the name bindings at serialization time and re-creates
    them at deserialization.
    """

    __implements__ = ISerializer

    schema = None  # No storage

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        event.ignore('_bind_names')
        return None

    def deserialize(self, event, state):
        assert state is None, state
        # prepare the _bind_names attribute
        event.obj.getBindingAssignments()


class OFSProperties:
    """Serializer for OFS.PropertyManager properties."""

    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('type', 'string')
    schema.add('data', 'string')

    def can_serialize(self, obj):
        return isinstance(obj, PropertyManager)

    def serialize(self, event):
        res = []
        obj = event.obj
        assert isinstance(obj, PropertyManager), repr(obj)
        assert obj._properties is obj._propertyMap()
        event.ignore('_properties')
        for p in obj._properties:
            name = p['id']
            t = p['type']
            event.ignore(name)
            data = obj.getProperty(name)
            if t == 'lines':
                v = '\n'.join(data)
            elif t == 'boolean':
                v = data and '1' or '0'
            elif string_repr_types.get(t):
                v = str(data)
            else:
                # Pickle the value and any extra info about the property.
                # Extra info is present in select and multi-select properties.
                d = p.copy()
                del d['id']
                del d['type']
                if d.has_key('mode'):
                    del d['mode']
                d['value'] = data
                v = dumps(d)
            res.append((name, t, v))
        return res

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(obj, PropertyManager)
        assert obj._properties is obj._propertyMap()
        if not state:
            # No stored properties.  Revert the object to its
            # class-defined property schema.
            if obj.__dict__.has_key('_properties'):
                del obj._properties
            return

        old_props = obj.propdict()
        new_props = {}
        for id, t, v in state:
            p = old_props.get(id)
            if p is None:
                p = {'mode': 'wd'}
            else:
                p = p.copy()
            p['id'] = id
            p['type'] = t
            if v and not string_repr_types.get(t) and t != 'lines':
                # v is a pickle.
                # Check the pickle for extra property info.
                d = loads(v)
                if isinstance(d, DictType):
                    del d['value']
                    if d:
                        # The data is stored with extra property info.
                        p.update(d)
            new_props[id] = p

        if old_props != new_props:
            obj._properties = tuple(new_props.values())

        for id, t, v in state:
            if t == 'lines':
                data = v.split('\n')
            elif t == 'boolean':
                # match 0, [f]alse, [n]o
                if (not v or v == '0' or v[:1].lower() in 'fn'):
                    data = 0
                else:
                    data = 1
            elif string_repr_types.get(t):
                data = str(v)
            elif v:
                d = loads(v)
                if isinstance(d, DictType):
                    # The data is stored with extra property info.
                    data = d['value']
                else:
                    data = d
            else:
                # Fall back to a default.
                data = ''
            obj._updateProperty(id, data)


class OptionalOFSProperties(OptionalSerializer):

    def __init__(self):
        OptionalSerializer.__init__(self, OFSProperties(), [])

