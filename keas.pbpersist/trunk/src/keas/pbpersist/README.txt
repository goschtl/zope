

Tests of keas.pbpersist
=======================

Create a PContact instance.  PContact is a Persistent class that stores
its state in a protobuf instance.

    >>> from keas.pbpersist.tests import PContact
    >>> bob = PContact()

Can't serialize it yet.

    >>> bob.__getstate__()
    Traceback (most recent call last):
    ...
    EncodeError: Required field ContactPB.name is not set.

Fill out the required fields, then verify we can serialize it.

    >>> bob.name = u'Bob'
    >>> bob.__getstate__()
    ('\x08\x01\x12\x03Bob', {})

Register the protobuf serializer with ZODB.

    >>> from keas.pbpersist.pbformat import register
    >>> register()

Set up an in-memory database and put the PContact in it.

    >>> from ZODB.DemoStorage import DemoStorage
    >>> from ZODB.DB import DB
    >>> import transaction
    >>> storage = DemoStorage()
    >>> db = DB(storage)
    >>> conn1 = db.open()
    >>> conn1.root()['bob'] = bob
    >>> transaction.commit()

Read the PContact from another connection.

    >>> conn2 = db.open()
    >>> bob2 = conn2.root()['bob']
    >>> bob2.name
    u'Bob'
    >>> conn2.close()

Create another PContact and assign that contact to be a guardian for Bob.
[Ed: I sure don't like the way we manage references right now.  I'd much
rather see "bob.guardians.add().target = alice", but that is not yet
possible.]

    >>> alice = PContact()
    >>> alice.name = u'Alice'
    >>> ref = bob.guardians.add()
    >>> bob.protobuf_refs.set(ref, alice)
    >>> transaction.commit()

Find Alice through Bob in another connection.

    >>> conn2 = db.open()
    >>> bob2 = conn2.root()['bob']
    >>> alice2 = bob2.protobuf_refs.get(bob2.guardians[0])
    >>> alice2.name
    u'Alice'
    >>> conn2.close()

Close the object database.

    >>> transaction.abort()
    >>> conn1.close()
    >>> db.close()
