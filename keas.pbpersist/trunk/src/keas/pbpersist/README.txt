

Tests and Documentation of keas.pbpersist
=========================================

Overview
--------

The keas.pbpersist package provides a way to store ZODB objects using
Google Protocol Buffer encoding rather than pickling.  The Protocol
Buffer format is more limited than pickles, but it is also simpler,
better documented, and not dependent on any particular programming
language.

Only Persistent objects that use the ProtobufState metaclass are eligible
for this kind of serialization, so applications that want to take advantage
of keas.pbpersist need to be refactored at the model level.  However,
applications can be refactored gradually, since protobuf
encoded objects and pickled objects can coexist and hold references
to each other within a single database.

This package is expected to be fully compatible with most ZODB
storages, including FileStorage, ZEO, RelStorage, and any other storage
that treats object records as opaque binary streams.


How to Use This Package
-----------------------

Register the protobuf serializer with ZODB.  This only needs to happen
once per application run, but it does no harm if it happens more than once.

    >>> from keas.pbpersist.pbformat import register
    >>> register()
    >>> register()

Create a PContact instance.  PContact is a simple Persistent class that
stores its state in a protobuf message.  Fill out the required field.

    >>> from keas.pbpersist.tests import PContact
    >>> bob = PContact()
    >>> bob.name = u'Bob'

Set up an in-memory object database and put the PContact in it.

    >>> from ZODB.DemoStorage import DemoStorage
    >>> from ZODB.DB import DB
    >>> import transaction
    >>> storage = DemoStorage()
    >>> db = DB(storage, database_name='main')
    >>> conn1 = db.open()
    >>> conn1.root()['bob'] = bob
    >>> transaction.commit()

Let's take a peek at what got stored in the database.  Look Ma, no pickles!

    >>> data, serial = storage.load(bob._p_oid, '')
    >>> data
    '{protobuf}\n \n\x14keas.pbpersist.tests\x12\x08PContact\x12\x07\x08\x01\x12\x03Bob'

Here is a demonstration of how to crack open that record using nothing but
language independent operations.  The ObjectRecord message holds the object's
class, state, and references; the state field holds a class-specific
protobuf message.

    >>> from keas.pbpersist.persistent_pb2 import ObjectRecord
    >>> rec = ObjectRecord()
    >>> rec.MergeFromString(data[10:])  # skip the {protobuf} prefix
    43
    >>> rec.class_meta.module_name
    u'keas.pbpersist.tests'
    >>> rec.class_meta.class_name
    u'PContact'
    >>> len(rec.references)
    0
    >>> pbuf = PContact.protobuf_type()
    >>> pbuf.MergeFromString(rec.state)
    7
    >>> pbuf.name
    u'Bob'

Ok, I'm happy that's possible, but now let's cut the noise and use nice
ZODB operations to read the object.

    >>> conn2 = db.open()
    >>> bob2 = conn2.root()['bob']
    >>> bob2.name
    u'Bob'
    >>> conn2.close()

Create another PContact and assign that contact to be a guardian for Bob.
The add() method below is part of Google's protobuf API.  The
protobuf_refs attribute is provided by the ProtobufState metaclass
in keas.pbstate.

    >>> alice = PContact()
    >>> alice.name = u'Alice'
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, alice)
    >>> transaction.commit()

[Ed: I sure don't like the way we manage references right now.  I'd much
rather see "bob.guardians.add().target = alice", but that is not yet
possible.]

Get Alice through Bob in another ZODB connection.

    >>> conn2 = db.open()
    >>> bob2 = conn2.root()['bob']
    >>> alice2 = bob2.protobuf_refs.get(bob2.guardians[0])
    >>> alice2.name
    u'Alice'

Note that alice2 is a duplicate of alice, not the same object, because
the two come from different ZODB connections.

    >>> alice is alice2
    False

We also have the option of referring to objects by OID, but that
is rarely necessary.

    >>> conn3 = db.open()
    >>> bob3 = conn3[bob._p_oid]

ZODB loads all objects lazily, including objects serialized using
this package.  When a persistent object's _p_changed
attribute is None, the object is in the "ghost" state; it does not
yet contain data.  Accessing an attribute transparently loads the object
state.

    >>> bob3._p_changed is None
    True
    >>> bob3.name
    u'Bob'
    >>> bob3._p_changed
    False

Clean up the extra connections.
    
    >>> conn3.close()
    >>> conn2.close()


Packing
-------

Storages need to be able to follow chains of references in order to pack,
so let's make sure the referencesf() function still does what it should.

    >>> from ZODB.serialize import referencesf
    >>> data, serial = storage.load(conn1.root()._p_oid, '')
    >>> referencesf(data) == [bob._p_oid]
    True
    >>> data, serial = storage.load(bob._p_oid, '')
    >>> referencesf(data) == [alice._p_oid]
    True
    >>> data, serial = storage.load(alice._p_oid, '')
    >>> referencesf(data)
    []


Reference Capabilities And Limitations
---------------------------------------

Objects serialized using this package can refer to any other Persistent
objects.  (Note that we already demonstrated that pickled objects
can refer to protobuf serialized objects when we added "bob" to the
root object in the database.)

    >>> from persistent.mapping import PersistentMapping
    >>> len(bob.guardians)
    1
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, PersistentMapping())
    >>> transaction.commit()
    >>> len(bob.guardians)
    2

However, objects serialized using this package can not hold a reference
to non-Persistent objects.  (This is a limitation of keas.pbpersist, but
not a limitation of keas.pbstate, which does not depend on ZODB.)  We don't
detect bad references until the first phase of transaction commit.

    >>> len(bob.guardians)
    2
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, {})
    >>> len(bob.guardians)
    3
    >>> transaction.commit()
    Traceback (most recent call last):
    ...
    POSError: Protobuf reference target is not a Persistent object: {}

Aborting the transaction undoes the damage.

    >>> transaction.abort()
    >>> len(bob.guardians)
    2

We can make weak references, though!

    >>> from persistent.wref import WeakRef
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, WeakRef(PersistentMapping()))
    >>> transaction.commit()
    >>> len(bob.guardians)
    3

We can also make cross-database references.

    >>> storage_beta = DemoStorage()
    >>> db_beta = DB(storage_beta, database_name='beta', databases=db.databases)
    >>> root_beta = conn1.get_connection('beta').root()
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, root_beta)
    >>> transaction.commit()

Access all of those references in another connection.

    >>> conn2 = db.open()
    >>> bob2 = conn2.root()['bob']
    >>> bob2.protobuf_refs.get(bob2.guardians[0])
    <keas.pbpersist.tests.PContact object at ...>
    >>> bob2.protobuf_refs.get(bob2.guardians[1])
    {}
    >>> bob2.protobuf_refs.get(bob2.guardians[1])._p_jar is conn2
    True
    >>> bob2.protobuf_refs.get(bob2.guardians[2])
    <persistent.wref.WeakRef object at ...>
    >>> bob2.protobuf_refs.get(bob2.guardians[2])()
    {}
    >>> bob2.protobuf_refs.get(bob2.guardians[3])
    {}
    >>> bob2.protobuf_refs.get(bob2.guardians[3])._p_jar is conn2
    False
    >>> conn2.close()


Clean Up
--------

Close the object database.

    >>> transaction.abort()
    >>> conn1.close()
    >>> db.close()
