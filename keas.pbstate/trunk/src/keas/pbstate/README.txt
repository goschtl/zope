
=====
Tests
=====

These are tests of keas.pbstate, a Python package that provides
a way to store Python object state in a Google Protocol Buffer.
These tests also serve as basic documentation of this package.
This package is designed to be compatible with ZODB, but ZODB is
not required.

These tests depend on the module named testclasses_pb2.py, which
is generated from testclasses.proto using the following command:

    protoc --python_out . *.proto

Create a Contact class.

    >>> import time
    >>> from keas.pbstate.meta import ProtobufState
    >>> from keas.pbstate.testclasses_pb2 import ContactPB
    >>> class Contact(object):
    ...     __metaclass__ = ProtobufState
    ...     protobuf_type = ContactPB
    ...     def __init__(self):
    ...         self.create_time = int(time.time())
    ...

Create an instance of this class and verify the instance has the expected
attributes.

    >>> c = Contact()
    >>> c.create_time > 0
    True
    >>> c.name
    u''
    >>> c.address.line1
    u''
    >>> c.address.country
    u'United States'

The instance also provides access to the protobuf message, its type (inherited
from the class), and the references from the message.

    >>> c.protobuf
    <keas.pbstate.testclasses_pb2.ContactPB object at ...>
    >>> c.protobuf_type
    <class 'keas.pbstate.testclasses_pb2.ContactPB'>
    >>> c.protobuf_refs
    <keas.pbstate.meta.ProtobufReferences object at ...>

Set and retrieve some of the attributes.

    >>> c.name = u'John Doe'
    >>> c.address.line1 = u'100 First Avenue'
    >>> c.address.country = u'Canada'
    >>> c.name
    u'John Doe'
    >>> c.address.country
    u'Canada'

Try to set one of the attributes to a value the protobuf message can't
serialize.

    >>> c.name = 100
    Traceback (most recent call last):
    ...
    TypeError: 100 has type <type 'int'>, but expected one of: (<type 'str'>, <type 'unicode'>)
    >>> c.name
    u'John Doe'

Try to set an attribute not declared in the .proto file.

    >>> c.phone = u'555-1234'
    Traceback (most recent call last):
    ...
    AttributeError: 'Contact' object has no attribute 'phone'

Try to serialize the object without providing all of the required fields.

    >>> c.__getstate__()
    Traceback (most recent call last):
    ...
    EncodeError: Required field AddressPB.city is not set.

Finish filling out the required fields, then serialize.

    >>> c.address.city = u'Toronto'
    >>> c.create_time = 1001
    >>> c.__getstate__()
    ('\x08\xe9\x07\x12\x08John Doe\x1a#\n\x10100 First Avenue\x1a\x07Toronto2\x06Canada', {})

Create a contact and copy its state from c.

    >>> c_dup = Contact.__new__(Contact)
    >>> c_dup.__setstate__(c.__getstate__())
    >>> c_dup.name
    u'John Doe'
    >>> c_dup.address.country
    u'Canada'

Create another contact, but this time provide no address information.

    >>> c2 = Contact()
    >>> c2.create_time = 1002
    >>> c2.name = u'Mary Anne'
    >>> c2.__getstate__()
    ('\x08\xea\x07\x12\tMary Anne', {})

Add a guardian to c2, but don't say who the guardian is yet.

    >>> guardian_ref = c2.guardians.add()

Using the protobuf_refs attribute, assign c to be a guardian of c2.
Note that the item interface of the protobuf_refs attribute is
unusual.  Don't think of it like a mapping; just think of it as a way
to refer to any object.  Under the covers, a reference
ID will be generated, that ID will be assigned to guardian_ref._p_refid,
and the refid and target object will be added to the internal
state of the protobuf_refs object.  Any message with a _p_refid field
is a reference.  Every _p_refid field should be of type uint32.

    >>> c2.protobuf_refs[guardian_ref] = c

Verify the reference is serialized correctly.

    >>> data, targets = c2.__getstate__()
    >>> targets[c2.guardians[0]._p_refid] is c
    True


Features Designed for ZODB
--------------------------

The _p_changed attribute, if it exists, is set to True whenever the protobuf
changes.  Here is the PersistentContact class, which has a _p_changed
attribute.

    >>> class FakePersistent(object):
    ...     __slots__ = ('_changed',)
    ...     def _get_changed(self):
    ...         return getattr(self, '_changed', False)
    ...     def _set_changed(self, value):
    ...         self._changed = value
    ...     _p_changed = property(_get_changed, _set_changed)
    ...
    >>> class PersistentContact(FakePersistent):
    ...     __metaclass__ = ProtobufState
    ...     protobuf_type = ContactPB
    ...

    >>> c3 = PersistentContact()
    >>> c3.create_time = 1003
    >>> c3.name = u'Snoopy'
    >>> c3._p_changed = False; c3.__getstate__() and None

Reading an attribute does not set _p_changed.

    >>> c3.name
    u'Snoopy'
    >>> c3._p_changed
    False

Writing an attribute sets _p_changed.

    >>> c3.name = u'Woodstock'
    >>> c3._p_changed
    True

Adding to a repeated element sets _p_changed.

    >>> c3._p_changed = False; c3.__getstate__() and None
    >>> c3._p_changed
    False
    >>> c3.guardians.add()
    <keas.pbstate.testclasses_pb2.Ref object at ...>
    >>> c3._p_changed
    True
    >>> del c3.guardians[0]

A copy of c3 should initially have _p_changed = False; setting an attribute
should set _p_changed to true.

    >>> c4 = PersistentContact.__new__(PersistentContact)
    >>> c4.__setstate__(c3.__getstate__())
    >>> c4._p_changed
    False
    >>> c4.name = u'Linus'
    >>> c4._p_changed
    True

The tuple returned by __getstate__ is actually a subclass of tuple.  This
might tell the serializer in ZODB to save the state without pickling.

TODO: __getstate__ returns StateTuple

TODO: mixins

