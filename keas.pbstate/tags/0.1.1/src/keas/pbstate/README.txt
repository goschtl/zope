
Overview
========

Google's Protocol Buffers project provides an interesting way to serialize
data.  Protocol Buffer messages are efficient to produce and parse, flexible
enough to weather schema changes, fairly expressive, and are usable in
several programming languages.

What if we combined those properties with an object database?  Object
databases often provide an excellent software foundation.  Unfortunately,
object databases are generally bound to a single programming language.
This package provides object serialization using Protocol Buffers,
conceivably making it possible to build an object database that
multiple programming languages can access.

Using this package also provides schema documentation.  The Protocol Buffers
package requires programmers to write the schema of their data in a
concise form that also serves as documentation of the schema.  While it's
usually possible to guess at the schema by looking at application
code, having it written out in Protocol Buffer format is much more
direct and informative.

This package is designed to be combined with an object database such as
ZODB, but this package does not require ZODB.


Tests
=====

The tests below describe how to use this package.
These tests depend on the module named testclasses_pb2.py, which
is generated from testclasses.proto using the following command,
available once the Google Protocol Buffers package is installed::

    protoc --python_out . *.proto

Create a Contact class.  Notice its metaclass.  The metaclass adds
properties to the class so that you can read and write protocol
buffer message fields using simple attribute access.  The
'create_time' attribute is one such field.

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
attributes.  These attributes are all described in the .proto file.

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
from the class), and the references from the message.  References will be
discussed later.

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


Mixins
------

A class can mix in properties that access sub-messages.  This is
useful when subclassing (although subclassing should be avoided in general).

Here is a class that mixes the ContactPB properties and the AddressPB
properties in a single class.

    >>> class MixedContact(object):
    ...     __metaclass__ = ProtobufState
    ...     protobuf_type = ContactPB
    ...     protobuf_mixins = ('address',)

    >>> mc = MixedContact()
    >>> mc.line1 = u'180 Market St.'
    >>> mc.line1
    u'180 Market St.'
    >>> mc.address.line1
    u'180 Market St.'


Serialization
-------------

The ProtobufState also provides __getstate__ and __setstate__ methods,
which Python uses for serialization purposes.

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


Object References
-----------------

Classes using the ProtobufState metaclass support references to arbitrary
objects through the use of the 'protobuf_refs' attribute.

Our Contact class has a 'guardians' attribute that contains a list of
references.  The ProtobufState metaclass treats any message or sub-message
with a _p_refid field as a reference.

Add a guardian to c2, but don't say who the guardian is yet.

    >>> guardian_ref = c2.guardians.add()

Call protobuf_refs.set() to make guardian_ref refer to c.

    >>> c2.protobuf_refs.set(guardian_ref, c)

Let's go over what happened.  The set method generated a reference ID, then
that ID was assigned to guardian_ref._p_refid, and the refid and target object
were added to the internal state of the protobuf_refs instance.  Any message
with a _p_refid field is a reference.  Every _p_refid field should be
of type uint32.

Read the reference.

    >>> c2.protobuf_refs.get(guardian_ref) is c
    True

Verify the reference gets serialized correctly.

    >>> data, targets = c2.__getstate__()
    >>> targets[c2.guardians[0]._p_refid] is c
    True

Delete the reference.

    >>> c2.protobuf_refs.delete(guardian_ref)
    >>> c2.protobuf_refs.get(guardian_ref, 'gone')
    'gone'

Verify the reference is no longer contained in the serialized state.

    >>> data, targets = c2.__getstate__()
    >>> len(targets)
    0


Features Designed for ZODB
--------------------------

This package provides enough features for storing ProtobufState objects
in ZODB, although without the keas.pbpersist package, the stored objects
will still be wrapped inside a Python pickle, making them hard for
languages other than Python to access.  See the keas.pbpersist package
for a straightforward method of storing ProtobufState objects in ZODB
without using Python pickles.

In ZODB, objects have a _p_changed attribute to indicate when they
are dirty.  The ProtobufState metaclass causes instances to modify
the _p_changed attribute if it exists; it is set to True whenever the
message changes.

Here is a PersistentContact class, which has a _p_changed attribute.
(We also define a FakePersistent base class in order to avoid
depending on ZODB.)

    >>> class FakePersistent(object):
    ...     __slots__ = ('_changed',)
    ...     def _get_changed(self):
    ...         return getattr(self, '_changed', False)
    ...     def _set_changed(self, value):
    ...         self._changed = value
    ...         if not value:
    ...             # reset the _cache_byte_size_dirty flags
    ...             self.protobuf.ByteSize()
    ...     _p_changed = property(_get_changed, _set_changed)
    ...
    >>> class PersistentContact(FakePersistent):
    ...     __metaclass__ = ProtobufState
    ...     protobuf_type = ContactPB
    ...

    >>> c3 = PersistentContact()
    >>> c3._p_changed
    False
    >>> c3.create_time = 1003
    >>> c3.name = u'Snoopy'
    >>> c3._p_changed = False

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

    >>> c3._p_changed = False
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

The tuple returned by __getstate__ is actually a subclass of tuple.  The
StateTuple suggests to the ZODB serializer that it can save the state
in a different format than the default pickle format.

    >>> type(c.__getstate__())
    <class 'keas.pbstate.state.StateTuple'>
    >>> c.__getstate__().serial_format
    'protobuf'


Edge Cases
----------

Synthesize a refid hash collision.  This is a rare occurrence, but
this package should handle it transparently as long as no single object
holds more than about one billion (2**30) references to other objects.

First make a reference:

    >>> guardian_ref = c2.guardians.add()
    >>> c2.protobuf_refs.set(guardian_ref, c)

Covertly change the target of that reference:

    >>> c2.protobuf_refs._targets[guardian_ref._p_refid] = mc

Add a new reference to the original target.  The first generated refid
will collide, but he protobuf_refs should should choose a different
refid automatically.

    >>> guardian2_ref = c2.guardians.add()
    >>> c2.protobuf_refs.set(guardian2_ref, c)
    >>> guardian_ref._p_refid == guardian2_ref._p_refid
    False


Exception Conditions
--------------------

Deleting message attributes is not allowed.

    >>> del c.name
    Traceback (most recent call last):
    ...
    AttributeError: can't delete attribute
    >>> del mc.line1
    Traceback (most recent call last):
    ...
    AttributeError: can't delete attribute

Mixin names are checked.

    >>> class MixedUpContact(object):
    ...     __metaclass__ = ProtobufState
    ...     protobuf_type = ContactPB
    ...     protobuf_mixins = ('bogus',)
    Traceback (most recent call last):
    ...
    AttributeError: Field 'bogus' not defined for protobuf type <...>

Create a broken reference by setting a reference using the wrong
protobuf_refs.  To prevent this condition, the protobuf_refs attribute
and the first argument to protobuf_refs.set() must descend from the
same containing object.

    >>> c.guardians.add()
    <keas.pbstate.testclasses_pb2.Ref object at ...>
    >>> c2.protobuf_refs.set(c.guardians[0], c)
    >>> c.__getstate__()
    Traceback (most recent call last):
    ...
    KeyError: 'Object contains broken references: <Contact object at ...>'
    >>> del c.guardians[0]

Don't omit the protobuf_type attribute.

    >>> class FailedContact(object):
    ...     __metaclass__ = ProtobufState
    Traceback (most recent call last):
    ...
    TypeError: Class ...FailedContact needs a protobuf_type attribute
    