==============
Object Locking
==============

This package provides a framework for object locking. The implementation
is intended to provide a simple general-purpose locking architecture upon
which other locking applications can be built (WebDAV locking, for example).

The locking system is purely *advisory* - it provides a way to associate a
lock with an object, but it does not enforce locking in any way. It is up
to application-level code to ensure that locked objects are restricted in
a way appropriate to the application.

The Zope 3 locking model defines interfaces and a default implementation
that:

  - allows for a single lock on an object, owned by a specific principal

  - does not necessarily impose inherent semantic meaning (exclusive
    vs. non-exclusive, write vs. read) on locks, though it will
    provide fields that higher-level application components can use
    to implement and enforce such semantics

  - can potentially be used to build more ambitious locking
    mechanisms (such as WebDAV locking equivalent to Zope 2)

  - supports common use cases that have been uncovered in several years
    of development of real-world applications (such as reporting all of
    the objects locked by a given user)


The Zope3 locking architecture defines an `ILockable` interface and
provides a default adapter implementation that requires only that an
object be adaptable to `IKeyReference`. All persistent objects can be
adapted to this interface by default in Zope 3, so in practice all
persistent objects are lockable.

The default `ILockable` adapter implementation provides support for:

  - locking and unlocking an object

  - breaking an existing lock on an object

  - obtaining the lock information for an object


Locking operations (lock, unlock, break lock) fire events that may be
handled by applications or other components to interact with the locking
system in a loosely-coupled way.

Lock information is accessible through an object that supports the
`ILockInfo` interface. The `ILockInfo` interface implies `IAnnotatable`,
so that other locking implementations (superseding or complementing the
default implementation) can store more information if needed to support
extended locking semantics.

The locking architecture also supports an efficient method of lock tracking
that allows you to determine what locks are held on objects. The default
implementation provides an `ILockTracker` utility that can be used by
applications to quickly find all objects locked by a particular principal.


Locking essentials
------------------

Normally, locking is provided by the default locking implementation. In
this example, we'll create a simple content class. The content class
is persistent, which allows us to use the default locking adapters and
utilities.

  >>> import persistent

  >>> class Content(persistent.Persistent):
  ...     """A sample content object"""
  ...
  ...     def __init__(self, value):
  ...         self.value = value
  ...
  ...     def __call__(self):
  ...         return self
  ...
  ...     def __hash__(self):
  ...         return self.value
  ...
  ...     def __cmp__(self, other):
  ...         return cmp(self.value, other.value)


Now we will create a few sample objects to work with:

  >>> item1 = Content("item1")
  >>> item1.__name__ = "item1"

  >>> item2 = Content("item2")
  >>> item2.__name__ = "item2"

  >>> item3 = Content("item3")
  >>> item3.__name__ = "item3"


It is possible to test whether an object supports locking by attempting
to adapt it to the ILockable interface:

  >>> from zope.app.locking.interfaces import ILockable
  >>> from zope.app.locking.interfaces import ILockInfo

  >>> ILockable(item1, None)
  <Locking adapter for...

  >>> ILockable(42, None)


There must be an active interaction to use locking, to allow the framework
to determine the principal performing locking operations. This example sets
up some sample principals and a helper to switch principals for further
examples:

  >>> class FauxPrincipal:
  ...    def __init__(self, id):
  ...        self.id = id

  >>> britney = FauxPrincipal('britney')
  >>> tim = FauxPrincipal('tim')

  >>> class FauxParticipation:
  ...     interaction = None
  ...     def __init__(self, principal):
  ...         self.principal = principal

  >>> import zope.security.management
  >>> def set_principal(principal):
  ...     if zope.security.management.queryInteraction():
  ...         zope.security.management.endInteraction()
  ...     participation = FauxParticipation(principal)
  ...     zope.security.management.newInteraction(participation)

  >>> set_principal(britney)


Now, let's look at basic locking. To perform locking operations, we first
have to adapt an object to `ILockable`:

  >>> obj = ILockable(item1)
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(ILockable, obj)
  True

We can ask if the object is locked:

  >>> obj.locked()
  False


If it were locked, we could get the id of the principal that owns the
lock. Since it is not locked, this will return `None`:

  >>> obj.locker()


Now let's lock the object. Note that the lock method return an instance
of an object that implements `ILockInfo` on success:

  >>> info = obj.lock()
  >>> verifyObject(ILockInfo, info)
  True

  >>> obj.locked()
  True

  >>> obj.locker()
  'britney'


Methods are provided to check whether the current principal already has
the lock on an object and whether the lock is already owned by a different
principal:

  >>> obj.ownLock()
  True

  >>> obj.isLockedOut()
  False


If we switch principals, we see that the answers reflect the current
principal:

  >>> set_principal(tim)
  >>> obj.ownLock()
  False

  >>> obj.isLockedOut()
  True


A principal can only release his or her own locks:

  >>> obj.unlock()
  Traceback (most recent call last):
    ...
  LockingError: Principal is not lock owner


If we switch back to the original principal, we see that the original
principal can unlock the object:

  >>> set_principal(britney)
  >>> obj.unlock()


There is a mechanism for breaking locks that does not take the current
principal into account. This will break any existing lock on an object:

  >>> obj.lock()
  <...LockInfo...>

  >>> set_principal(tim)
  >>> obj.locked()
  True

  >>> obj.breaklock()
  >>> obj.locked()
  False


Locks can be created with an optional timeout. If a timeout is provided,
it should be an integer number of seconds from the time the lock is
created.

  >>> # fake time function to avoid a time.sleep in tests!
  >>> import time
  >>> def faketime():
  ...    return time.time() + 3600.0

  >>> obj.lock(timeout=10)
  <...LockInfo...>

  >>> obj.locked()
  True

  >>> import zope.app.locking.storage
  >>> zope.app.locking.storage.timefunc = faketime
  >>> obj.locked()
  False

(Note that we undo our time hack in the tearDown of this module.)

Finally, it is possible to explicitly get an `ILockInfo` object that
contains the lock information for the object. Note that locks that do
not have a timeout set have a timeout value of `None`.

  >>> obj = ILockable(item2)
  >>> obj.lock()
  <...LockInfo...>

  >>> info = obj.getLockInfo()
  >>> info.principal_id
  'tim'
  >>> info.timeout


It is possible to get the object associated with a lock directly from
an `ILockInfo` instance:

  >>> target = info.target
  >>> target.__name__ == 'item2'
  True


The `ILockInfo` interface extends the IMapping interface, so application
code can store extra information on locks if necessary. It is recommended
that keys for extra data use qualified names following the convention that
is commonly used for annotations:

  >>> info['my.namespace.extra'] = 'spam'
  >>> info['my.namespace.extra']
  'spam'
  >>> obj.unlock()
  >>> obj.locked()
  False


Lock tracking
-------------

It is often desirable to be able to report on the currently held locks in
a system (particularly on a per-user basis), without requiring an expensive
brute-force search. An `ILockTracker` utility allows an application to get
the current locks for a principal, or all current locks:

  >>> set_principal(tim)
  >>> obj = ILockable(item2)
  >>> obj.lock()
  <...LockInfo...>

  >>> set_principal(britney)
  >>> obj = ILockable(item3)
  >>> obj.lock()
  <...LockInfo...>

  >>> from zope.app.locking.interfaces import ILockTracker
  >>> from zope.component import getUtility
  >>> util = getUtility(ILockTracker)
  >>> verifyObject(ILockTracker, util)
  True

  >>> items = util.getLocksForPrincipal('britney')
  >>> len(items) == 1
  True

  >>> items = util.getAllLocks()
  >>> len(items) >= 2
  True


These methods allow an application to create forms and other code that
performs unlocking or breaking of locks on sets of objects:

  >>> items = util.getAllLocks()
  >>> for item in items:
  ...     obj = ILockable(item.target)
  ...     obj.breaklock()

  >>> items = util.getAllLocks()
  >>> len(items)
  0

The lock storage utility provides further capabilities, and is a part of the
standard lock adapter implementation, but the ILockable interface does not
depend on ILockStorage.  Other implementations of ILockable may not use
ILockStorage.  However, if used by the adapter, it provides useful
capabilties.

  >>> from zope.app.locking.interfaces import ILockStorage
  >>> util = getUtility(ILockStorage)
  >>> verifyObject(ILockStorage, util)
  True

Locking events
--------------

Locking operations (lock, unlock, break lock) fire events that can be used
by applications. Note that expiration of a lock *does not* fire an event
(because the current implementation uses a lazy expiration approach).

  >>> import zope.event

  >>> def log_event(event):
  ...     print event

  >>> zope.event.subscribers.append(log_event)

  >>> obj = ILockable(item2)
  >>> obj.lock()
  LockedEvent ...

  >>> obj.unlock()
  UnlockedEvent ...

  >>> obj.lock()
  LockedEvent ...

  >>> obj.breaklock()
  BreakLockEvent ...


TALES conditions based on locking
---------------------------------

TALES expressions can use a named path adapter to get information
about the lock status for an object, including whether or not the
object can be locked.  The default registration for this adapter uses
the name "locking", so a condition might be expressed like
"context/locking:ownLock", for example.

For objects that aren't lockable, the adapter provides information
that makes sense::

  >>> from zope.component import getAdapter
  >>> from zope.traversing.interfaces import IPathAdapter

  >>> ns = getAdapter(42, IPathAdapter, "locking")
  >>> ns.lockable
  False

  >>> ns.locked
  False

  >>> ns.lockedOut
  False

  >>> ns.ownLock
  False

Using an object that's lockable, but unlocked, also gives the expected
results::

  >>> ns = getAdapter(item1, IPathAdapter, "locking")
  >>> ns.lockable
  True

  >>> ns.locked
  False

  >>> ns.lockedOut
  False

  >>> ns.ownLock
  False

If we lock the object, the adapter indicates that the object is locked
and that we own it::

  >>> ob = ILockable(item1)
  >>> ob.lock()
  LockedEvent for ...

  >>> ns.lockable
  True

  >>> ns.locked
  True

  >>> ns.lockedOut
  False

  >>> ns.ownLock
  True
