Experimental Monkey Patch to Subscribe to invalidations
=======================================================

Sometimes, we wanna know when objects change.  zc.zodbobjecteventsmp
provides a monkey patch that let's us do this.  Let's create a
database and patch it.

    >>> import ZODB.utils, ZODB.tests.util, transaction
    >>> db = ZODB.tests.util.DB()


To be notified of changes, we need to provide a function that takes a
tid and iterable of object ids:

    >>> def notify(tid, oids):
    ...     # check that the tids are right:
    ...     conn = db.open()
    ...     for oid in oids:
    ...         if not conn.get(oid)._p_serial != tid:
    ...             print 'oops'
    ...     print 'changed', sorted(ZODB.utils.u64(oid) for oid in oids)

    >>> import zc.zodbobjecteventsmp
    >>> zc.zodbobjecteventsmp.patch(db, notify)

    >>> conn = db.open()
    >>> conn.root.x = conn.root().__class__()
    >>> conn.root.y = conn.root().__class__()
    >>> transaction.commit()
    changed [0]

Note that we're not told about new objects.

    >>> conn.root.x.x = 1
    >>> conn.root.y.x = 1
    >>> transaction.commit()
    changed [1, 2]

Other databases aren't affected:

    >>> db = ZODB.tests.util.DB()
    >>> conn = db.open()
    >>> conn.root.x = conn.root().__class__()
    >>> conn.root.y = conn.root().__class__()
    >>> transaction.commit()
    >>> conn.root.x.x = 1
    >>> conn.root.y.x = 1
    >>> transaction.commit()

    >>> db.close()

Typically, you'll be interested in a particular set of objects.  To
look for changes in a specific set, you'd keep track of the set by oid
and dispatch to an app-level function only when invalidated oids are
in the set.
