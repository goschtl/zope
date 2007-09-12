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
"""Serializers specific to ZODB3.

$Id$
"""

import os
from cStringIO import StringIO
from cPickle import Pickler, Unpickler, UnpickleableError, loads, dumps
import time
import base64
from types import DictType

from Persistence import Persistent, PersistentMapping
from ZODB.TimeStamp import TimeStamp

from apelib.core.interfaces \
     import ISerializer, IFullSerializationEvent, IFullDeserializationEvent
from apelib.core.events import SerializationEvent, DeserializationEvent
from apelib.core.interfaces import SerializationError
from apelib.core.schemas import RowSequenceSchema, ColumnSchema


def is_persistent(obj):
    try:
        return isinstance(obj, Persistent)
    except TypeError:
        # XXX Python 2.1 thinks Persistent is not a class
        return 0

def encode_to_text(s, keys, unmanaged_count=0):
    """Encodes a binary pickle using base 64.

    Note that Python's text pickle format encodes unicode using full
    8-bit bytes (Python versions 2.1 through 2.3 all do this), meaning
    that so-called text pickles are not 7-bit clean.  On the other
    hand, the text pickle format is fairly easy to read, making
    debugging easier.  This encoding is a compromise that generates
    pure 7-bit text but also provides an overview of what's in the
    pickle.
    """
    comments = ['# pickle-base-64']
    if keys:
        keys = list(keys)
        keys.sort()
        comments[0] = comments[0] + ' contents:'
        for key in keys:
            r = repr(key).replace('\n', ' ')
            comments.append('# %s' % r)
    if unmanaged_count:
        comments.append('# unmanaged persistent objects: %d' % unmanaged_count)
    text = base64.encodestring(s)
    return '%s\n%s' % ('\n'.join(comments), text)

def decode_from_text(s):
    """Decodes using base 64, ignoring leading comments.
    """
    i = s.rfind('#')
    if i >= 0:
        j = s.find('\n', i)
        if j >= 0:
            # Remove the comments.
            s = s[j + 1:].strip()
    return base64.decodestring(s)



class PersistentMappingSerializer:
    """(de)serializer of a persistent mapping that uses string keys.

    Serializes both references and second-class persistent objects.
    Because of this flexibility, the schema is a little complex.
    """
    __implements__ = ISerializer

    # This schema includes both a list of items that are references to
    # persistent objects and a pickle containing items that are not
    # references.
    schema1 = RowSequenceSchema()
    schema1.add('key', 'string', 1)
    schema1.add('oid', 'string')
    schema1.add('classification', 'classification')
    schema2 = ColumnSchema('data', 'string')
    schema = {'references': schema1, 'others': schema2}

    def can_serialize(self, obj):
        return isinstance(obj, PersistentMapping)

    def serialize(self, event):
        assert self.can_serialize(event.obj)
        refs = []
        others = {}
        for key, value in event.obj.items():
            if is_persistent(value):
                oid = event.obj_db.identify(value)
                if oid is None:
                    oid = event.obj_db.new_oid()
                event.referenced(key, value, False, oid)
                # No need to pass classification.
                refs.append((key, oid, None))
            else:
                event.serialized(key, value, False)
                others[key] = value
        event.ignore(('data', '_container'))
        if others:
            # Encode as a sorted list to preserve order.
            others_list = others.items()
            others_list.sort()
            s = encode_to_text(dumps(others_list, 1), others.keys())
        else:
            s = ''
        return {'references': refs, 'others': s}

    def deserialize(self, event, state):
        assert self.can_serialize(event.obj)
        data_dict = {}
        s = state['others']
        if s:
            s = decode_from_text(s)
            if s:
                data = loads(s)
                if hasattr(data, 'items'):
                    # Stored as a dictionary
                    data_list = data.items()
                    data_dict = data
                else:
                    # Stored as a sequence of tuples
                    data_list = data
                    for key, value in data:
                        data_dict[key] = value
                for key, value in data_list:
                    event.deserialized(key, value)
        for (key, oid, classification) in state['references']:
            value = event.resolve(key, oid, classification)
            data_dict[key] = value
        event.obj.__init__(data_dict)


class RollCall:
    """Helps ensure all parts of an object get serialized.

    Designed for debugging purposes.
    """
    __implements__ = ISerializer
    schema = None  # No storage

    def can_serialize(self, obj):
        return 1

    def serialize(self, event):
        assert IFullSerializationEvent.isImplementedBy(event)
        attrs = event.get_seralized_attributes()
        attrs_map = {}
        for attr in attrs:
            attrs_map[attr] = 1
        missed = []
        for k in event.obj.__dict__.keys():
            if not k.startswith('_v_') and not attrs_map.has_key(k):
                missed.append(repr(k))
        if missed:
            raise SerializationError(
                'Attribute(s) %s of object %s, oid=%s, not serialized' %
                (', '.join(missed), repr(event.obj), repr(event.oid)))
        return None

    def deserialize(self, event, state):
        assert state is None


class RemainingState:
    """(De)serializes the remaining state of a Persistent object"""

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'string')

    def can_serialize(self, obj):
        return is_persistent(obj)

    def serialize(self, event):
        assert IFullSerializationEvent.isImplementedBy(event)
        assert isinstance(event.obj, Persistent)

        # Allow pickling of cyclic references to the object.
        event.serialized('self', event.obj, False)

        # Ignore previously serialized attributes
        state = event.obj.__dict__.copy()
        for key in state.keys():
            if key.startswith('_v_'):
                del state[key]
        for attrname in event.get_seralized_attributes():
            if state.has_key(attrname):
                del state[attrname]
        if not state:
            # No data needs to be stored
            return ''

        outfile = StringIO()
        p = Pickler(outfile, 1)  # Binary pickle
        unmanaged = []

        def persistent_id(ob, identify_internal=event.identify_internal,
                          unmanaged=unmanaged):
            ref = identify_internal(ob)
            if ref is None:
                if hasattr(ob, '_p_oid'):
                    # Persistent objects that end up in the remainder
                    # are unmanaged.  Tell ZODB about them so that
                    # ZODB can deal with them specially.
                    unmanaged.append(ob)
            return ref

        # Preserve order to a reasonable extent by storing a list
        # instead of a dictionary.
        state_list = state.items()
        state_list.sort()
        p.persistent_id = persistent_id
        try:
            p.dump(state_list)
        except UnpickleableError, exc:
            # Try to reveal which attribute is unpickleable.
            attrname = None
            attrvalue = None
            for key, value in state_list:
                del unmanaged[:]
                outfile.seek(0)
                outfile.truncate()
                p = Pickler(outfile)
                p.persistent_id = persistent_id
                try:
                    p.dump(value)
                except UnpickleableError:
                    attrname = key
                    attrvalue = value
                    break
            if attrname is not None:
                # Provide a more informative exception.
                if os.environ.get('APE_TRACE_UNPICKLEABLE'):
                    # Provide an opportunity to examine
                    # the "attrvalue" attribute.
                    import pdb
                    pdb.set_trace()
                raise RuntimeError(
                    'Unable to pickle the %s attribute, %s, '
                    'of %s at %s.  %s.' % (
                    repr(attrname), repr(attrvalue), repr(event.obj),
                    repr(event.oid), str(exc)))
            else:
                # Couldn't help.
                raise

        p.persistent_id = lambda ob: None  # Stop recording references
        p.dump(unmanaged)
        event.upos.extend(unmanaged)

        s = outfile.getvalue()
        return encode_to_text(s, state.keys(), len(unmanaged))


    def deserialize(self, event, state):
        assert IFullDeserializationEvent.isImplementedBy(event)
        assert isinstance(event.obj, Persistent)

        # Set up to resolve cyclic references to the object.
        event.deserialized('self', event.obj)

        state = state.strip()
        if state:
            if state.startswith('#'):
                # Text-encoded pickles start with a pound sign.
                # (A pound sign is not a valid pickle opcode.)
                data = decode_from_text(state)
            else:
                data = state
            infile = StringIO(data)
            u = Unpickler(infile)
            u.persistent_load = event.resolve_internal
            s = u.load()
            if not hasattr(s, 'items'):
                # Turn the list back into a dictionary
                s_list = s
                s = {}
                for key, value in s_list:
                    s[key] = value
            event.obj.__dict__.update(s)
            try:
                unmanaged = u.load()
            except EOFError:
                # old pickle with no list of unmanaged objects
                pass
            else:
                event.upos.extend(unmanaged)


class ModTimeAttribute:
    """Sets the _p_mtime attribute.

    XXX Due to a ZODB limitation, this class has to set the _p_mtime
    by setting _p_serial.
    """

    __implements__ = ISerializer

    schema = ColumnSchema('mtime', 'int')

    def can_serialize(self, obj):
        return is_persistent(obj)

    def _set_time(self, obj, t):
        """Sets the last modification time of a Persistent obj to float t.
        """
        args = time.gmtime(t)[:5] + (t%60,)
        obj._p_serial = repr(TimeStamp(*args))

    def serialize(self, event):
        now = long(time.time())
        if event.obj._p_changed:
            # Indicate that this object just changed.  Note that the time
            # is a guess.
            self._set_time(event.obj, now)
        return now

    def deserialize(self, event, state):
        self._set_time(event.obj, state)


def find_unmanaged(obj, managed):
    """Gathers the list of unmanaged subobjects from an object.

    'managed' is a list of subobjects known to be managed.
    """
    d = {}
    for m in managed:
        d[id(m)] = m
    outfile = StringIO()
    p = Pickler(outfile, 1)  # Binary pickle
    unmanaged = []

    def persistent_id(ob, d_get=d.get, unmanaged=unmanaged):
        if d_get(id(ob)) is not None:
            # Don't search inside managed subobjects.
            return 'managed'
        if hasattr(ob, '_p_oid'):
            unmanaged.append(ob)
        return None

    p.persistent_id = persistent_id
    p.dump(obj)
    return unmanaged
