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
"""Standard serializers.

$Id$
"""

from types import StringType

from interfaces import ISerializer, IFullObjectSerializer
from interfaces import DeserializationError, SerializationError
from schemas import ColumnSchema


class CompositeSerializer:
    """Full serializer based on partial serializers.
    """
    __implements__ = IFullObjectSerializer
    schema = None

    def __init__(self, base=None):
        self._part_names = {}  # { name -> 1 }
        self._parts = []       # [(name, serializer)] -- Order matters.
        self._final_parts = [] # [(name, serializer)]
        if base is not None:
            self._part_names.update(base._part_names)
            self._parts[:] = base._parts
            self._final_parts[:] = base._final_parts
        self._update_schema()

    def _update_schema(self):
        self.schema = {}
        for name, serializer in self.get_serializers():
            s = serializer.schema
            if s is not None:
                self.schema[name] = s

    def add(self, name, serializer, force=0, final=0):
        if self._part_names.has_key(name):
            if not force:
                raise KeyError, "Serializer name %s in use" % repr(name)
            self.removeSerializer(name)
        if final:
            self._final_parts.append((name, serializer))
        else:
            self._parts.append((name, serializer))
        self._part_names[name] = 1
        self._update_schema()

    def remove(self, name):
        if not self._part_names.has_key(name):
            raise KeyError, "Serializer name %s not in use" % repr(name)
        for lst in (self._parts, self._final_parts):
            for i in range(len(lst)):
                if lst[i][0] == name:
                    del lst[i]
                    break
        del self._part_names[name]
        self._update_schema()

    def has(self, name):
        return self._part_names.has_key(name)

    def get_serializers(self):
        return self._parts + self._final_parts

    def can_serialize(self, obj):
        # XXX Need access to the mapper to make this determination.
        return 1
##        if not hasattr(obj, '__class__'):
##            return 0
##        c = obj.__class__
##        return (c.__module__ == self._module and c.__name__ == self._name)

    def has_base(self, klass, base_name):
        try:
            n = '%s.%s' % (klass.__module__, klass.__name__)
        except AttributeError:
            return False
        if n == base_name:
            return True
        for b in klass.__bases__:
            if self.has_base(b, base_name):
                return True
        return False

    def serialize(self, event):
        if event.mapper.class_name:
            assert self.has_base(
                event.obj.__class__, event.mapper.class_name), (
                event.obj, event.mapper.class_name)
        else:
            raise RuntimeError("Mapper '%s' is abstract" % event.mapper.name)
        full_state = {}
        for name, s in self.get_serializers():
            event.serializer_name = name
            state = s.serialize(event)
            if state is not None:
                full_state[name] = state
        return full_state

    def deserialize(self, event, full_state):
        if event.mapper.class_name:
            assert self.has_base(
                event.obj.__class__, event.mapper.class_name), (
                event.obj, event.mapper.class_name)
        for name, s in self.get_serializers():
            state = full_state.get(name)
            event.serializer_name = name
            s.deserialize(event, state)

    def new_instance(self, event):
        if event.classification is None:
            # Can't do anything without the classification.
            return None
        cn = event.classification.get('class_name')
        if cn is None:
            # Fall back to the default
            cn = event.mapper.class_name
        pos = cn.rfind('.')
        if pos < 0:
            raise ValueError, "class_name must include the module"
        module = cn[:pos]
        name = cn[pos + 1:]
        c = event.obj_db.get_class(module, name)
        if hasattr(c, "__basicnew__"):  # ExtensionClass
            return c.__basicnew__()
        else:
            return c.__new__()


class PDBSerializer (CompositeSerializer):
    """Invokes PDB before serialization / deserialization."""

    def serialize(self, event):
        import pdb
        pdb.set_trace()
        return AnyObjectSerializer.serialize(self, event)

    def deserialize(self, event, full_state):
        import pdb
        pdb.set_trace()
        AnyObjectSerializer.deserialize(self, event, full_state)


class FullState:
    """Serializer that reads/writes the entire state of an object."""

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'object')

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        return event.obj.__getstate__()

    def deserialize(self, event, state):
        event.obj.__setstate__(state)



class IgnoredAttribute:
    """Serializer that explicitly ignores an attribute
    """
    __implements__ = ISerializer
    schema = None  # No storage

    def __init__(self, attrname):
        self.attrname = attrname

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        event.ignore(self.attrname)
        return None

    def deserialize(self, event, state):
        assert state is None, state


class OptionalSerializer:
    """Serializer wrapper that serializes only if the object is compatible.
    """

    __implements__ = ISerializer
    schema = None

    def __init__(self, real, default_state=None):
        self._real = real
        self._default_state = default_state
        self.schema = real.schema

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        if self._real.can_serialize(event.obj):
            return self._real.serialize(event)
        else:
            return self._default_state

    def deserialize(self, event, state):
        if self._real.can_serialize(event.obj):
            self._real.deserialize(event, state)
        else:
            if state is not None and state != self._default_state:
                raise DeserializationError(
                    "Optional serializer unable to install state %s into %s" %
                    (repr(state), repr(event.obj)))


class StringDataAttribute:
    """Serializer of a simple string data attribute."""

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'string')

    def __init__(self, attrname):
        self.attrname = attrname

    def can_serialize(self, object):
        return 1

    def serialize(self, event):
        attrname = self.attrname
        assert attrname
        v = getattr(event.obj, attrname)
        assert isinstance(v, StringType)
        event.serialized(attrname, v, 1)
        return v

    def deserialize(self, event, state):
        attrname = self.attrname
        assert attrname
        assert isinstance(state, StringType)
        setattr(event.obj, attrname, state)
        event.deserialized(attrname, state)

