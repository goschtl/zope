

Tests of keas.pbpersist
=======================

Create a PContact instance.  PContact is a Persistent class that stores
its state in a protobuf instance.

    >>> from keas.pbpersist.tests import PContact
    >>> pc = PContact()
    >>> pc.__getstate__()
    Traceback (most recent call last):
    ...
    EncodeError: Required field ContactPB.name is not set.
    >>> pc.name = u'Joe'
    >>> pc.__getstate__()
    ('\x08\x01\x12\x03Joe', {})

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
    >>> conn1.root()['contact'] = pc
    >>> transaction.commit()

Read the PContact from another connection.

    >>> conn2 = db.open()
    >>> pc2 = conn2.root()['contact']
    >>> pc2.name
    u'Joe'
    >>> conn2.close()

Close the object database.

    >>> transaction.abort()
    >>> conn1.close()
    >>> db.close()
