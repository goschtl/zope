

"""A serializer for ZODB that stores protobuf messages instead of pickles."""

from zope.interface import implements
from ZODB.interfaces import ISerialFormat, ISerializer, IDeserializer
from ZODB.format import register_format
from ZODB.utils import p64, u64
from ZODB.POSException import POSError
from ZODB.broken import find_global as default_find_global
from keas.pbstate.state import StateTuple

from keas.pbpersist.persistent_pb2 import ClassMetadata
from keas.pbpersist.persistent_pb2 import ObjectRecord
from keas.pbpersist.persistent_pb2 import Reference

format_prefix = "{%s}" % StateTuple.serial_format

def decode_record(data):
    """Deserialize an ObjectRecord.

    The serialized data must start with the serialization format prefix.
    """
    if not data.startswith(format_prefix):
        raise POSError("Not a protobuf record: %s" % repr(data))
    res = ObjectRecord()
    res.MergeFromString(data[len(format_prefix):])
    return res

def read_reference(ref, find_global):
    """Return a ZODB formatted reference given a Reference message."""
    oid = p64(ref.zoid)
    if ref.weak:
        return ['w', (oid,)]
    elif ref.database:
        if ref.class_meta:
            klass = find_global(
                ref.class_meta.module_name, ref.class_meta.class_name)
            return ['m', (ref.database, oid, klass)]
        else:
            return ['n', (ref.database, oid)]
    elif ref.class_meta:
        klass = find_global(
            ref.class_meta.module_name, ref.class_meta.class_name)
        return (oid, klass)
    else:
        return oid


class ProtobufFormat(object):
    implements(ISerialFormat)

    def makeSerializer(self, persistent_id):
        return ProtobufSerializer(persistent_id)

    def makeDeserializer(self, persistent_load, find_global=None):
        return ProtobufDeserializer(persistent_load, find_global)

    def listPersistentReferences(self, data):
        record = decode_record(data)
        return (read_reference(ref, default_find_global)
            for ref in record.references)


class ProtobufSerializer(object):
    implements(ISerializer)

    def __init__(self, persistent_id):
        self.persistent_id = persistent_id

    def dump(self, classmeta, state):
        """Serialize a persistent object as an ObjectRecord message."""
        record = ObjectRecord()
        self.set_class(record.class_meta, classmeta)
        record.state, refs = state

        for refid, target in refs.iteritems():
            p = self.persistent_id(target)
            if p is None:
                # All references must point to Persistent objects because
                # the serialization format requires references to have an OID
                # and only Persistent objects have an OID.
                raise POSError(
                    "Protobuf reference target is not a Persistent object: %s"
                    % repr(target))
            self.add_reference(record, refid, p)

        return '%s%s' % (format_prefix, record.SerializeToString())

    def set_class(self, class_meta, source):
        """Set attributes of a ClassMetadata from a source class metadata.

        The source is in any of the formats described by the
        ZODB.serialize docstring.
        """
        if not isinstance(source, tuple):
            # source is in format #1
            class_meta.module_name = source.__module__
            class_meta.class_name = source.__name__
        else:
            klass, args = source
            if args is not None:
                # source is in format #2, 4, 6, or 7
                raise POSError(
                    "ProtobufSerializer can not serialize classes "
                    "using __getnewargs__ or __getinitargs__")
            if isinstance(klass, tuple):
                # source is in format #3
                class_meta.module_name, class_meta.class_name = klass
            else:
                # source is in format #5
                class_meta.module_name = klass.__module__
                class_meta.class_name = klass.__name__

    def add_reference(self, record, refid, p):
        """Add a reference to an ObjectRecord.

        p is a reference, created by the persistent_id() function,
        in one of the formats documented by ZODB.serialize.
        """
        r = record.references.add()
        r.refid = refid
        oid = None
        klass = None
        if isinstance(p, tuple):
            oid, klass = p
        elif isinstance(p, str):
            oid = p
        elif len(p) == 1:
            # old weakref format: [oid]
            (oid,) = p
            r.weak = True
        else:
            ref_type, args = p
            if ref_type == 'm':
                r.database, oid, klass = args
            elif ref_type == 'w':
                (oid,) = args
                r.weak = True
            elif ref_type == 'n':
                r.database, oid = args
            else:
                raise POSError("Unknown reference type: %s" % repr(ref_type))
        r.zoid = u64(oid)
        if klass is not None:
            r.class_meta.module_name = klass.__module__
            r.class_meta.class_name = klass.__name__


class ProtobufDeserializer(object):
    implements(IDeserializer)

    def __init__(self, persistent_load, find_global=None):
        self.persistent_load = persistent_load
        if find_global is None:
            self.find_global = default_find_global
        else:
            self.find_global = find_global

    def getClassAndState(self, data):
        record = decode_record(data)
        cm = record.class_meta
        yield (cm.module_name, cm.class_name), None
        ref_dict = {}
        for ref in record.references:
            zodb_ref = read_reference(ref, self.find_global)
            target = self.persistent_load(zodb_ref)
            ref_dict[ref.refid] = target
        yield record.state, ref_dict

    def getClassMetadata(self, data):
        return self.getClassAndState(data).next()

    def getState(self, data):
        i = self.getClassAndState(data)
        i.next()
        return i.next()

protobuf_format = ProtobufFormat()
def register():
    register_format(StateTuple.serial_format, protobuf_format)
