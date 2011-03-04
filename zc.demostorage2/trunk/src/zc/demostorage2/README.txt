Configuration
-------------

The section below shows how to create zc.demostorage2 storages from
Python. If you're using ZConfig, you need to:

- import zc.demostorage2

- include a demostorage2 section
  (must contain two storages, one with the name 'base'
  and one with the name 'changes').

Here's an example that shows how to configure demo storage and how to
use the configuration from python:

    >>> import ZODB.config
    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %import zc.demostorage2
    ...
    ... <demostorage2>
    ...    <filestorage base>
    ...       path base.fs
    ...    </filestorage>
    ...    <filestorage changes>
    ...       path changes.fs
    ...    </filestorage>
    ... </demostorage2>
    ... """)

This creates a demo storage that gets base data from a file storage
named base.fs and stores changes in a file storage named changes.fs.

    >>> storage
    <DemoStorage2: DemoStorage2(base.fs, changes.fs)>

    >>> storage.close()

Demo (doctest)
--------------

Note that most people will configure the storage through ZConfig.  If
you are one of those people, you may want to stop here. :)  The
examples below show you how to use the storage from Python, but they
also exercise lots of details you might not be interested in.

To see how this works, we'll start by creating a base storage and
puting an object (in addition to the root object) in it:

    >>> from ZODB.FileStorage import FileStorage
    >>> base = FileStorage('base.fs')
    >>> from ZODB.DB import DB
    >>> db = DB(base)
    >>> from persistent.mapping import PersistentMapping
    >>> conn = db.open()
    >>> conn.root()['1'] = PersistentMapping({'a': 1, 'b':2})
    >>> import transaction
    >>> transaction.commit()
    >>> db.close()
    >>> import os
    >>> original_size = os.path.getsize('base.fs')

Now, lets reopen the base storage in read-only mode:

    >>> base = FileStorage('base.fs', read_only=True)

And open a new storage to store changes:

    >>> changes = FileStorage('changes.fs')

and combine the 2 in a demofilestorage:

    >>> from zc.demostorage2 import DemoStorage2
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
    >>> transaction.commit()

    >>> conn.root()['2']['c'] = 5
    >>> transaction.commit()

Here we can see that we haven't modified the base storage:

    >>> original_size == os.path.getsize('base.fs')
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

    >>> serial = base.getTid(p64(0))
    >>> storage.loadSerial(p64(0), serial) == base.loadSerial(p64(0), serial)
    True

    >>> serial = changes.getTid(p64(0))
    >>> storage.loadSerial(p64(0), serial) == changes.loadSerial(p64(0),
    ...                                                          serial)
    True

The object id of the new object is quite large:

    >>> u64(conn.root()['2']._p_oid)
    4611686018427387905

Let's look at some other methods:

    >>> storage.getName()
    'DemoStorage2(base.fs, changes.fs)'

    >>> storage.sortKey() == changes.sortKey()
    True

    >>> storage.getSize() == changes.getSize()
    True

    >>> len(storage) == len(changes)
    True


Undo methods are simply copied from the changes storage:

    >>> [getattr(storage, name) == getattr(changes, name)
    ...  for name in ('supportsUndo', 'undo', 'undoLog', 'undoInfo')
    ...  ]
    [True, True, True, True]

