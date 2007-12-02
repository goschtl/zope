=================
zc.virtualstorage
=================

------------
Introduction
------------

zc.virtualstorage allows largely transparent versioning of ZODB object
collections. This can be used to provide staging semantics for a collection of
objects such as dev-staged-prod for a retail site hierarchy or
sandboxes-branches-trunk for a collection of interconnected configuration
objects [#zc.vault]_.

Basic Usage
===========

To use zc.virtualstorage, you must wrap a real storage (any type, in theory;
the developer will use and directly support FileStorage and ZEO client
storage) with a custom DB subclass.  

    >>> import ZODB.FileStorage
    >>> storage = ZODB.FileStorage.FileStorage(
    ...     'HistoricalConnectionTests.fs', create=True)
    >>> import zc.virtualstorage.base
    >>> db = zc.virtualstorage.base.DB(storage)

A connection from this DB instance returns a subclass of the ZODB Connection
called a Coordinator. The coordinator does everything that a normal connection
does and can be used for normal database interactions.

    >>> coordinator = db.open()
    >>> isinstance(coordinator, zc.virtualstorage.base.Coordinator)
    True

The Coordinator also coordinates the two-phase commit process for itself and
any subsidiary connections to virtual storages.

You can add a virtual storage anywhere in the database.  Without using it to
open a virtual connection, it's just another persistent object with nothing
particularly unusual. We'll add one in the root.

    >>> zero = zc.virtualstorage.base.VirtualStorage()
    >>> coordinator.root()['zero'] = zero

To actually connect to a virtual storage, the storage must have a _p_jar and
a _p_oid to the coordinator (the main connection). There are three ways of
doing that: committing the transaction, explicitly ``add``ing the object to the
coordinator connection, or providing an adapter to ZODB.interfaces.IConnection
that does the job. We'll ``add`` for now, and then ask the db to get a virtual
connection.

    >>> coordinator.add(zero)
    >>> conn0 = db.getVirtualConnection(zero)

You now have an open virtual connection to the virtual storage. As long as this
virtual connection is open, you can call ``getVirtualConnection`` again with
the same virtual storage and get the same connection [#get_is_recallable]_.

Initially the virtual storage doesn't have a root: you need to ``add`` an object to a
connection to register a root.

    >>> conn0.root()
    Traceback (most recent call last):
    ...
    POSKeyError: 0x00
    >>> import persistent.mapping
    >>> root = persistent.mapping.PersistentMapping()
    >>> conn0.add(root)
    >>> conn0.root() is root
    True

We can modify the root as desired.

    >>> conn0.root()['answer'] = 17
    >>> conn0.root()
    {'answer': 17}
    >>> conn0.root()['nested'] = persistent.mapping.PersistentMapping()
    >>> conn0.root()['nested']['foo'] = 'bar'

Now you can simply commit the transaction, and close the main connection if
needed or desired.

    >>> import transaction
    >>> transaction.commit()
    >>> coordinator.close()

Additional connections get the same data, with invalidations working even on
closed connections.  Virtual connections to the same virtual storage are
reused.

    >>> coordinator = db.open()
    >>> transaction2 = transaction.TransactionManager()
    >>> coordinatorB = db.open(transaction_manager=transaction2)

    >>> conn0B = db.getVirtualConnection(coordinatorB.root()['zero'])
    >>> sorted(conn0B.root().keys())
    ['answer', 'nested']
    >>> coordinatorB.close()

    >>> conn0 = db.getVirtualConnection(coordinator.root()['zero'])
    >>> conn0 is conn0B # reusing the virtual connection
    True
    >>> conn0.root()['answer'] = 42
    >>> transaction.commit()

    >>> coordinatorB is db.open()
    True
    >>> conn0B = db.getVirtualConnection(coordinatorB.root()['zero'])
    >>> conn0B.root()['answer']
    42
    >>> coordinatorB.close()

These virtual connections to virtual storages can work with blobs, savepoints,
ZEO, historical connections, and undo, as seen in the advanced demonstrations
at the end of the document.

Storage Revisions
=================

This virtual storage is really just a curiosity until you start letting one
virtual storage be based on another--allowing a frozen production version and
an editable development version, for instance. To have one virtual storage
based on another, the base must be readonly.  In the base implementation,
making a virtual storage is accomplished by the ``freeze`` method.

    >>> zero = coordinator.root()['zero']
    >>> zero.freeze()
    >>> one = zc.virtualstorage.base.VirtualStorage(zero)
    >>> coordinator.root()['one'] = one
    >>> transaction.commit()

Now the new storage looks like the old one.

    >>> conn1 = db.getVirtualConnection(one)
    >>> sorted(conn1.root().keys())
    ['answer', 'nested']
    >>> conn1.root()['answer']
    42
    >>> conn1.root()['nested']
    {'foo': 'bar'}

We can mutate the new one, though, without affecting the old one.

    >>> conn1.root()['blackjack'] = 21
    >>> sorted(conn1.root().keys())
    ['answer', 'blackjack', 'nested']
    
    >>> conn0 = db.getVirtualConnection(zero)
    >>> sorted(conn0.root().keys())
    ['answer', 'nested']

    >>> transaction.commit()

The original storage is now frozen.  If a connection to it is mutated,
the transaction cannot be committed.

    >>> conn0.root()['seven'] = 11
    >>> transaction.commit()
    Traceback (most recent call last):
    ...
    ReadOnlyError

We'll abort our changes.

    >>> transaction.abort()
    >>> sorted(conn0.root().keys())
    ['answer', 'nested']

Caches and Memory
=================

When you open a connection to a virtual storage, this is a full-fledged
connection as far as memory usage is concerned. The object cache is the biggest
memory concern. It is very easy, then, to open many connections, if you have
many storages, and quickly eat up unexpectedly large amounts of memory.

The package offers three pairs of methods to try and protect memory usage:
``getVirtualConnectionCacheSize`` and ``setVirtualConnectionCacheSize``;
``getVirtualConnectionTimeout`` and ``setVirtualConnectionTimeout``; and
``getVirtualConnectionPoolSize`` and ``setVirtualConnectionPoolSize``.

* The cache size controls the target maximum number of objects in each virtual
  connection's object cache.

* The timeout controls the minimum number of seconds a closed virtual
  connection is kept before it is discarded.

* The count controls the maximum count of total virtual connections that are
  kept when they close.  The newest ones win.

Of course, these have the same limitation as other standard ZODB object cache
settings: the cache size is based on the number of objects rather than their
actual total memory size. [#testcachecontrols]_.

ZConfig
=======

To use virtual storage with ZConfig, simply ``%import zc.virtualstorage`` and
use ``zodb_with_virtualstorage_support`` instead of ``zodb`` for the database
you want to use with virtual storage. Here's the simplest example.

    >>> import ZODB.config
    >>> zconfig_db = ZODB.config.databaseFromString('''
    ... %import zc.virtualstorage
    ... <zodb_with_virtualstorage_support>
    ...     <mappingstorage/>
    ... </zodb_with_virtualstorage_support>
    ... ''')
    >>> isinstance(zconfig_db, zc.virtualstorage.base.DB)
    True
    >>> zconfig_db.close()

Within a multi-database process you can mix and match, using both
the standard ``zodb`` and the custom ``zodb_with_virtualstorage_support``
within your configuration file for different databases.  Also, it's worth
noting that you should be able to switch back to ``zodb`` if you decide to
no longer use virtual storages: as mentioned before, from the perspective of
the main connection, they are just persistent objects.

You can provide all the same options to ``zodb_with_virtualstorage_support`` as
to a standard ``zodb`` section. You can also specify the cache settings that we
discussed in `Caches and Memory`_ above.

    >>> zconfig_db = ZODB.config.databaseFromString('''
    ... %import zc.virtualstorage
    ... <zodb_with_virtualstorage_support>
    ...     virtual-cache-size 1492
    ...     virtual-timeout 12m
    ...     virtual-pool-size 7
    ...     <mappingstorage/>
    ... </zodb_with_virtualstorage_support>
    ... ''')
    >>> zconfig_db.getVirtualConnectionCacheSize()
    1492
    >>> zconfig_db.getVirtualConnectionTimeout() # 12 minutes * 60 seconds
    720
    >>> zconfig_db.getVirtualConnectionPoolSize()
    7
    >>> zconfig_db.close()

Summary
=======

That's the basics of virtual storage: not much to it, which is the idea.  To
integrate with it, just use persistent objects as usual.

The remainder of the document discusses how the virtual storage works and gives
some advanced demonstrations of virtual storages working with standard ZODB
features such as savepoints and blobs.

------------
How It Works
------------

While the virtual storage has to participate in the delicate dances of commit
and cache invalidation, the basic concepts are simple. A virtual storage maps
effective OIDs to real OIDs when necessary. This means that, for instance, when
you ask for the object at the root OID of a virtual storage, the virtual
storage maps the virtual root OID to a real OID, asks the real storage for that
value, and then passes it back.

We'll get an idea of this by looking at our two storages.

The ``base`` attribute is a reference to the base storage.

    >>> coordinator = db.open()
    >>> one = coordinator.root()['one']
    >>> zero = coordinator.root()['zero']
    >>> one.base is zero
    True
    >>> zero.base is None
    True

If we look at the OIDs for the two persistent objects in each storage, they
are the same.

    >>> import ZODB.utils
    >>> conn0 = db.getVirtualConnection(zero)
    >>> conn1 = db.getVirtualConnection(one)
    >>> conn1.root()._p_oid == ZODB.utils.z64
    True
    >>> conn0.root()._p_oid == conn1.root()._p_oid
    True
    
    >>> conn1.root()['nested']._p_oid == conn0.root()['nested']._p_oid
    True

However, the roots are different objects, while the 'nested' mappings share the
same underlying object. The storages manage this with four data structures,
which should generally be regarded as protected except during delicate jobs
like generation scripts. ``local`` is a mapping from local overridden OID to
real OID. Even for a storage without a base, this contains a mapping from the
standard root OID, ZODB.utils.z64, to the real object used for this purpose.
Storages with a base will also include any objects that mask ones in its base.

    >>> list(zero.local.keys()) == [ZODB.utils.z64]
    True
    >>> list(one.local.keys()) == [ZODB.utils.z64]
    True

The ``reverse_local`` mapping is the mirror image of the ``local`` mapping,
used for getLocalOID.

    >>> list(zero.reverse_local.values()) == [ZODB.utils.z64]
    True
    >>> list(one.reverse_local.values()) == [ZODB.utils.z64]
    True

The ``new`` set is comprised of new objects within a storage that do not need
mapping.  Right now, zero.new contains the OID of the nested object, and
one.new is empty.

    >>> nested_oid = conn1.root()['nested']._p_oid
    >>> set(zero.new) == set((nested_oid,))
    True
    >>> len(one.new)
    0

Finally, the ``bucket`` attribute keeps a mapping of all local OIDs, new and
local, to the actual objects used.  The use case for this map is packing:
we want the storage to have a direct, standard reference to all used objects
so packing algorithms unaware of the zc.virtualstorage approach still keep
the necessary objects around.

    >>> dict((k, v._p_oid) for k, v in zero.bucket.items()) == {
    ...     ZODB.utils.z64: zero.local[ZODB.utils.z64],
    ...     nested_oid: nested_oid}
    True
    >>> dict((k, v._p_oid) for k, v in one.bucket.items()) == {
    ...     ZODB.utils.z64: one.local[ZODB.utils.z64]}
    True
    >>> (list(zero.reverse_local.keys()) == list(zero.local.values()) ==
    ...  [zero.bucket[ZODB.utils.z64]._p_oid])
    True
    >>> (list(one.reverse_local.keys()) == list(one.local.values()) ==
    ...  [one.bucket[ZODB.utils.z64]._p_oid])
    True

The ``bucket`` mapping may also be useful for jobs like generations scripts.
While frozen storages will not allow changes to objects in the virtual
connections, the collaborators will allow the commit, so you can use the
bucket to iterate over all local objects in a frozen storage and do database
generation work on them.

Note that all four of these collections are typically only updated on a
transaction commit.  The only exception is the ``new`` collection, which will
be modified when a virtual connection's ``add`` method is used successfuly.
Even then, the modification will be discarded if the pertinent transaction is
aborted.

-----------------------
Advanced Demonstrations
-----------------------

This section exercises built-in ZODB tricks to show that they can work with the
virtual storage.  As such, they are largely just confirmations and tests rather
than new information.

Savepoints
==========

Savepoints should work as they normally do.  First we'll show a rollback.

    >>> conn1.root()['abraham'] = 'abe'
    >>> conn1.root()['nested']['emily'] = 'emma'
    >>> sp = transaction.savepoint()
    >>> conn1.root()['nested']['james'] = 'jim'
    >>> conn1.root()['nested']['m'] = persistent.mapping.PersistentMapping()
    >>> sp.rollback()

Now we'll make some changes after a savepoint and commit.

    >>> 'james' in conn1.root()['nested']
    False
    >>> 'm' in conn1.root()['nested']
    False
    >>> conn1.root()['abraham']
    'abe'
    >>> conn1.root()['nested']['emily']
    'emma'
    >>> conn1.root()['nested']['gerbrand'] = 'bran'
    >>> transaction.commit()

Blobs
=====

To show blobs, we need to use the storage with a blob proxy.  We'll close our
db, wrap our storage with a proxy, and make a new db.

    >>> coordinator.close()
    >>> from ZODB.blob import BlobStorage, Blob
    >>> from tempfile import mkdtemp
    >>> blob_dir = mkdtemp()
    >>> blob_storage = BlobStorage(blob_dir, storage)
    >>> db = zc.virtualstorage.base.DB(blob_storage)

Now we'll put a blob in a virtual connection.

    >>> blob = Blob()
    >>> data = blob.open("w")
    >>> data.write("I'm a happy Blob.")
    >>> data.close()

    >>> coordinator = db.open()
    >>> conn1 = db.getVirtualConnection(coordinator.root()['one'])
    >>> conn1.root()['nested']['blob'] = blob
    >>> transaction.commit()

The blob is available from other connections, as expected.

    >>> coordinatorB = db.open(transaction_manager=transaction2)
    >>> conn1B = db.getVirtualConnection(coordinatorB.root()['one'])
    >>> conn1B.root()['nested']['blob'].open('r').read()
    "I'm a happy Blob."
    
    >>> conn1.close()
    >>> coordinatorB.close()
    
Basing one virtual storage on another also works with blobs: the original
blob is untouched.

    >>> coordinator.root()['one'].freeze()
    >>> coordinator.root()['two'] = zc.virtualstorage.base.VirtualStorage(
    ...     coordinator.root()['one'])
    >>> transaction.commit()

    >>> conn2 = db.getVirtualConnection(coordinator.root()['two'])
    >>> f = conn2.root()['nested']['blob'].open('w')
    >>> f.write('I am an ecstatic Blob.')
    >>> f.close()
    >>> transaction.commit()

    >>> coordinatorB = db.open(transaction_manager=transaction2)
    >>> conn1B = db.getVirtualConnection(coordinatorB.root()['one'])
    >>> conn1B.root()['nested']['blob'].open('r').read()
    "I'm a happy Blob."

    >>> conn2B = db.getVirtualConnection(coordinatorB.root()['two'])
    >>> conn2B.root()['nested']['blob'].open('r').read()
    'I am an ecstatic Blob.'

Conflict Errors
===============

Conflict errors work as usual.

    >>> conn2.root()['nested']['yrag'] = 'gary'
    >>> conn2B.root()['nested']['nyrak'] = 'karyn'
    >>> transaction2.commit()
    >>> transaction.commit() # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ConflictError: ...
    >>> 'yrag' in conn2.root()['nested']
    False
    >>> conn2.root()['nested']['nyrak']
    'karyn'

If you abort and retry, everything will work again, as usual.

    >>> transaction.abort()
    >>> conn2.root()['nested']['yrag'] = 'gary'
    >>> transaction.commit()
    >>> conn2.root()['nested']['yrag']
    'gary'
    >>> conn2.root()['nested']['nyrak']
    'karyn'

Historical Connections
======================

If you open up a main "coordinator" connection that is historical (using ``at``
or ``before``) then the virtual storages and virtual connections are also tied
to that time.  We'll show this by opening up an historical connection when
the "one" virtual storage was frozen.

    >>> coordinatorB.close() # so we can reuse the transaction manager
    >>> coordinator.sync()
    >>> historical_coordinator = db.open(
    ...     transaction_manager=transaction2,
    ...     at=coordinator.root()['one']._p_serial)

Way back then, the blob was merely happy, not ecstatic, and 'yrag' and 'nyrak'
were not in the "nested: mapping.

    >>> h_two = historical_coordinator.root()['two']
    >>> h_conn = db.getVirtualConnection(h_two)
    >>> h_conn.root()['nested']['blob'].open('r').read()
    "I'm a happy Blob."
    >>> 'nyrak' in h_conn.root()['nested']
    False
    >>> 'yrag' in h_conn.root()['nested']
    False

The storage is readonly, even though it is not frozen, because it is
based on a historical, readonly coordinator connection.

    >>> h_two._readonly
    False
    >>> h_two.isReadOnly()
    True

    >>> historical_coordinator.close()

----
TODO
----

Historical Base or Base from Another Database
=============================================

This should be possible.  Stay tuned.

.. ......... ..
.. Footnotes ..
.. ......... ..

.. [#zc.vault] The ideas in zc.virtualstorage grow from zc.vault, which has
    been used very successfully for similar use cases. However, zc.vault
    requires significantly more developer knowledge and care when developing
    applications that use it. In contrast, zc.virtualstorage should be very
    natural and comfortable to ZODB developers, with very little extra to
    learn.

    On the other hand, zc.vault does currently have merge and resolution
    stories that zc.virtualstorage does not yet have. zc.virtualstorage also
    replaces low-level ZODB components such as the DB and Connection objects so
    it is, at least arguably in some dimensions, riskier than zc.vault.

    But the vastly improved developer story of zc.virtualstorage--which should
    be so transparent that an already existing ZODB-based application could use
    it without much modification--is intended to make zc.virtualstorage a
    compelling replacement.

.. [#get_is_recallable]

    >>> conn0 is db.getVirtualConnection(zero)
    True

.. [#testcachecontrols] To examine these settings, we will look at internal
    data structures.

    Here's the cache size.

    >>> db.getVirtualConnectionCacheSize()
    1000
    >>> def check_cache_size():
    ...     size = db.getVirtualConnectionCacheSize()
    ...     for call in db.virtual_pool.all.as_weakref_list():
    ...         c = call()
    ...         if c is None:
    ...             continue
    ...         if c._cache.cache_size != size:
    ...             raise RuntimeError('hm, I have encountered an error')
    ...
    >>> check_cache_size()
    >>> db.setVirtualConnectionCacheSize(1500)
    >>> db.getVirtualConnectionCacheSize()
    1500
    >>> check_cache_size()
    >>> db.setVirtualConnectionCacheSize(500)
    >>> db.getVirtualConnectionCacheSize()
    500
    >>> check_cache_size()

    Here's the timeout. Old connections are discarded when you open or close a
    virtual connection.

    >>> db.getVirtualConnectionTimeout()
    300
    >>> db.setVirtualConnectionTimeout(200)
    >>> db.getVirtualConnectionTimeout()
    200
    >>> DB_module = __import__('ZODB.DB', globals(), locals(), ['chicken'])
    >>> original_time = DB_module.time
    >>> OFFSET = 0
    >>> def stub_time():
    ...     return original_time() + OFFSET
    ...
    >>> DB_module.time = stub_time
    >>> OFFSET = 200
    >>> len(db.virtual_pool.all) # conn0, conn1, conn0B
    3
    >>> bool(conn0._opened), bool(conn1._opened)
    (True, True)
    >>> bool(conn0B._opened)
    False
    >>> set(c() for c in db.virtual_pool.all.as_weakref_list()) == set((
    ... conn0, conn1, conn0B))
    True
    >>> coordinator.close() # virtual closes and connects triggers cleanup
    >>> len(db.virtual_pool.all) # conn0, conn1
    2
    >>> set(c() for c in db.virtual_pool.all.as_weakref_list()) == set((
    ... conn0, conn1))
    True

    Here's the count.

    >>> print db.getVirtualConnectionPoolSize()
    3
    >>> len(db.virtual_pool.all) # conn0, conn1
    2
    >>> db.setVirtualConnectionPoolSize(1)
    >>> db.getVirtualConnectionPoolSize()
    1
    >>> len(db.virtual_pool.all)
    1