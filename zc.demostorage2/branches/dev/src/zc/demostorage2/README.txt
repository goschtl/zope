Second-generation demo storage
==============================

The demostorage2 module provides a storage implementation that
wraps two storages, a base storage and a storage to hold changes.
The base storage is never written to.  All new records are written to
the changes storage.  Both storages are expected to:

- Use packed 64-bit unsigned integers as object ids,

- Allocate object ids sequentially, starting from 0, and

- in the case of the changes storage, accept object ids assigned externally.

In addition, it is assumed that less than 2**63 object ids have been
allocated in the first storage. 

Note that DemoStorage also assumes that it's base storage uses 64-bit
unsigned integer object ids allocated sequentially.

To see how this works, we'll start by creating a base storage and
puting an object (in addition to the root object) in it:

    >>> import os, tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> base_path = os.path.join(tempdir, 'base.fs')

    >>> from ZODB.FileStorage import FileStorage
    >>> base = FileStorage(base_path)
    >>> from ZODB.DB import DB
    >>> db = DB(base)
    >>> from ZODB.PersistentMapping import PersistentMapping
    >>> conn = db.open()
    >>> conn.root()['1'] = PersistentMapping({'a': 1, 'b':2})
    >>> get_transaction().commit()
    >>> db.close()
    >>> original_size = os.path.getsize(base_path)

Now, lets reopen the base storage in read-only mode:

    >>> base = FileStorage(base_path, read_only=True)

And open a new storage to store changes:

    >>> changes_path = os.path.join(tempdir, 'changes.fs')
    >>> changes = FileStorage(changes_path)

and combine the 2 in a demofilestorage:

    >>> from demostorage2 import DemoStorage2
    >>> storage = DemoStorage2(base, changes)

If there are no transactions, the storage reports the lastTransaction
of the base database:

    >>> storage.lastTransaction() == base.lastTransaction()
    True

Let's add some data:

    >>> db = DB(storage)
    >>> conn = db.open()
    >>> items = conn.root()['1'].items()
    >>> items.sort()
    >>> items
    [('a', 1), ('b', 2)]

    >>> conn.root()['2'] = PersistentMapping({'a': 3, 'b':4})
    >>> get_transaction().commit()

    >>> conn.root()['2']['c'] = 5
    >>> get_transaction().commit()

Here we can see that we haven't modified the base storage:

    >>> original_size == os.path.getsize(base_path)
    True

But we have modified the changes database:

    >>> len(changes)
    2

Our lastTransaction reflects the lastTransaction of the changes:

    >>> storage.lastTransaction() > base.lastTransaction()
    True

    >>> storage.lastTransaction() == changes.lastTransaction()
    True


Let's walk over some of the methods so ewe can see how we delegate to
the new oderlying storages:

    >>> from ZODB.utils import p64, u64
    >>> storage.load(p64(0), '') == changes.load(p64(0), '')
    True
    >>> storage.load(p64(0), '') == base.load(p64(0), '')
    False
    >>> storage.load(p64(1), '') == base.load(p64(1), '')
    True

    >>> serial = base.getSerial(p64(0)) 
    >>> storage.loadSerial(p64(0), serial) == base.loadSerial(p64(0), serial)
    True

    >>> serial = changes.getSerial(p64(0)) 
    >>> storage.loadSerial(p64(0), serial) == changes.loadSerial(p64(0),
    ...                                                          serial)
    True

The object id of the new object is quite large:

    >>> u64(conn.root()['2']._p_oid)
    9223372036854775809L

Versions aren't supported:

    >>> storage.supportsVersions()
    False
    >>> storage.versions()
    ()
    >>> storage.versionEmpty(p64(0))
    True
    >>> storage.versionEmpty(p64(60))
    True
    >>> storage.modifiedInVersion(p64(0))
    ''
    >>> storage.modifiedInVersion(p64(60))
    ''
    
Many methods are simply copied from the base storage:

    >>> [getattr(storage, name) == getattr(changes, name)
    ...  for name in ('getName', 'sortKey', 'getSize', '__len__', 
    ...               'supportsUndo', 'undo', 'undoLog', 'undoInfo',
    ...               'supportsTransactionalUndo')
    ...  ]
    [True, True, True, True, True, True, True, True, True]

