Version Control
===============

This package provides a framework for managing multiple versions of objects
within a ZODB database.  The framework defines several interfaces that objects
may provide to participate with the framework.  For an object to participate in
version control, it must provide `IVersionable`.  `IVersionable` is an
interface that promises that there will be adapters to:

- `INonVersionedData`, and

- `IPhysicallyLocatable`.

It also requires that instances support `IPersistent` and `IAnnotatable`.

Normally, these interfaces will be provided by adapters.  To simplify the
example, we'll just create a class that already implements the required
interfaces directly.  We need to be careful to avoid including the `__name__`
and `__parent__` attributes in state copies, so even a fairly simple
implementation of INonVersionedData has to deal with these for objects that
contain their own location information.

    >>> import persistent
    >>> from zope import component, interface
    >>> import zope.app.annotation.attribute
    >>> import zope.app.annotation.interfaces
    >>> import zope.app.traversing.interfaces
    >>> from zope.app.versioncontrol import interfaces

    >>> marker = object()

    >>> class Sample(persistent.Persistent):
    ...     interface.implements(
    ...         interfaces.IVersionable,
    ...         interfaces.INonVersionedData,
    ...         zope.app.annotation.interfaces.IAttributeAnnotatable,
    ...         zope.app.traversing.interfaces.IPhysicallyLocatable,
    ...         )
    ...
    ...     # Methods defined by INonVersionedData
    ...     # This is a trivial implementation; using INonVersionedData
    ...     # is discussed later.
    ...
    ...     def listNonVersionedObjects(self):
    ...         return ()
    ...
    ...     def removeNonVersionedData(self):
    ...         if "__name__" in self.__dict__:
    ...             del self.__name__
    ...         if "__parent__" in self.__dict__:
    ...             del self.__parent__
    ...
    ...     def getNonVersionedData(self):
    ...         return (getattr(self, "__name__", marker),
    ...                 getattr(self, "__parent__", marker))
    ...
    ...     def restoreNonVersionedData(self, data):
    ...         name, parent = data
    ...         if name is not marker:
    ...             self.__name__ = name
    ...         if parent is not marker:
    ...             self.__parent__ = parent
    ...
    ...     # Method from IPhysicallyLocatable that is actually used:
    ...     def getPath(self):
    ...         return '/' + self.__name__
    ...
    ...     def __repr__(self):
    ...         return "<%s object>" % self.__class__.__name__

    >>> component.provideAdapter(
    ...     zope.app.annotation.attribute.AttributeAnnotations)

Now we need to create a database with an instance of our sample object to work
with:

    >>> from ZODB.tests import util
    >>> import transaction

    >>> db = util.DB()
    >>> connection = db.open()
    >>> root = connection.root()

    >>> samp = Sample()
    >>> samp.__name__ = "samp"
    >>> root["samp"] = samp
    >>> transaction.commit()

Some basic queries may be asked of objects without using an instance of
`IRepository`.  In particular, we can determine whether an object can be
managed by version control by checking for the `IVersionable` interface:

    >>> interfaces.IVersionable.providedBy(samp)
    True
    >>> interfaces.IVersionable.providedBy(42)
    False

We can also determine whether an object is actually under version
control using the `IVersioned` interface:

    >>> interfaces.IVersioned.providedBy(samp)
    False
    >>> interfaces.IVersioned.providedBy(42)
    False

Placing an object under version control requires an instance of an
`IRepository` object.  This package provides an implementation of this
interface on the `Repository` class (from
`zope.app.versioncontrol.repository`).  Only the `IRepository` instance is
responsible for providing version control operations; an object should never
be asked to perform operations directly.

    >>> import zope.app.versioncontrol.repository
    >>> import zope.interface.verify

    >>> repository = zope.app.versioncontrol.repository.Repository()
    >>> zope.interface.verify.verifyObject(
    ...     interfaces.IRepository,
    ...	  repository)
    True

In order to actually use version control, there must be an
interaction.  This is needed to allow the framework to determine the
user making changes.  Let's set up an interaction now. 

    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal('bob')
    >>> participation = zope.security.testing.Participation(principal)

    >>> import zope.security.management
    >>> zope.security.management.newInteraction(participation)

Let's register some subscribers so we can check that interesting
events are being fired for version control actions:

    >>> def showEvent(label, object, event):
    ...     print label, "for", object

    >>> component.provideHandler(
    ...     (lambda ob, evt: showEvent("applied version control", ob, evt)),
    ...     (interface.Interface, interfaces.IVersionControlApplied))

Now, let's put an object under version control and verify that we can
determine that fact by checking against the interface:

    >>> repository.applyVersionControl(samp)
    applied version control to <Sample object>
    >>> interfaces.IVersioned.providedBy(samp)
    True
    >>> transaction.commit()

Once an object is under version control, it's possible to get an
information object that provides some interesting bits of data:

    >>> info = repository.getVersionInfo(samp)
    >>> type(info.history_id)
    <type 'str'>

It's an error to ask for the version info for an object which isn't
under revision control:

    >>> samp2 = Sample()
    >>> repository.getVersionInfo(samp2)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.

    >>> repository.getVersionInfo(42)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.

The function `queryVersionInfo` returns a default value if an object
isn't under version control:

    >>> print repository.queryVersionInfo(samp2)
    None

    >>> print repository.queryVersionInfo(samp2, 0)
    0

    >>> repository.queryVersionInfo(samp).version_id
    '1'


You can retrieve a version of an object using the `.history_id` and a
version selector.  A version selector is a string that specifies which
available version to return.  The value `mainline` tells the
`IRepository` to return the most recent version on the main branch.

    >>> ob = repository.getVersionOfResource(info.history_id, 'mainline')
    retrieved <Sample object>, version 1
    >>> type(ob)
    <class 'zope.app.versioncontrol.README.Sample'>
    >>> ob is samp
    False
    >>> root["ob"] = ob
    >>> ob.__name__ = "ob"
    >>> ob_info = repository.getVersionInfo(ob)
    >>> ob_info.history_id == info.history_id
    True
    >>> ob_info is info
    False

Once version control has been applied, the object can be "checked
out", modified and "checked in" to create new versions.  For many
applications, this parallels form-based changes to objects, but this
is a matter of policy.

Let's save some information about the current version of the object so
we can see that it changes:

    >>> orig_history_id = info.history_id
    >>> orig_version_id = info.version_id

Now, let's check out the object and add an attribute:

    >>> repository.checkoutResource(ob)
    checked out <Sample object>, version 1
    >>> ob.value = 42
    >>> repository.checkinResource(ob)
    checked in <Sample object>, version 2
    >>> transaction.commit()

We can now compare information about the updated version with the
original information:

    >>> newinfo = repository.getVersionInfo(ob)
    >>> newinfo.history_id == orig_history_id
    True
    >>> newinfo.version_id != orig_version_id
    True

Retrieving both versions of the object allows use to see the
differences between the two:

    >>> o1 = repository.getVersionOfResource(orig_history_id,
    ...                                      orig_version_id)
    retrieved <Sample object>, version 1
    >>> o2 = repository.getVersionOfResource(orig_history_id,
    ...                                      newinfo.version_id)
    retrieved <Sample object>, version 2
    >>> o1.value
    Traceback (most recent call last):
      ...
    AttributeError: 'Sample' object has no attribute 'value'
    >>> o2.value
    42

We can determine whether an object that's been checked out is
up-to-date with the most recent version from the repository:

    >>> repository.isResourceUpToDate(o1)
    False
    >>> repository.isResourceUpToDate(o2)
    True

Asking whether a non-versioned object is up-to-date produces an error:

    >>> repository.isResourceUpToDate(42)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.

    >>> repository.isResourceUpToDate(samp2)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.

It's also possible to check whether an object has been changed since
it was checked out.  Since we're only looking at changes that have
been committed to the database, we'll start by making a change and
committing it without checking a new version into the version control
repository.

    >>> repository.updateResource(samp)
    updated <Sample object> from version 1 to 2
    >>> repository.checkoutResource(samp)
    checked out <Sample object>, version 2
    >>> transaction.commit()

    >>> repository.isResourceChanged(samp)
    False
    >>> samp.value += 1
    >>> transaction.commit()

We can now see that the object has been changed since it was last
checked in:

    >>> repository.isResourceChanged(samp)
    True

Checking in the object and commiting shows that we can now veryify
that the object is considered up-to-date after a subsequent checkout.
We'll also demonstrate that `checkinResource()` can take an optional
message argument; we'll see later how this can be used.

    >>> repository.checkinResource(samp, 'sample checkin')
    checked in <Sample object>, version 3
    >>> transaction.commit()

    >>> repository.checkoutResource(samp)
    checked out <Sample object>, version 3
    >>> transaction.commit()

    >>> repository.isResourceUpToDate(samp)
    True
    >>> repository.isResourceChanged(samp)
    False
    >>> repository.getVersionInfo(samp).version_id
    '3'

It's also possible to use version control to discard changes that
haven't been checked in yet, even though they've been committed to the
database for the "working copy".  This is done using the
`uncheckoutResource()` method of the `IRepository` object:

    >>> samp.value
    43
    >>> samp.value += 2
    >>> samp.value
    45
    >>> transaction.commit()
    >>> repository.isResourceChanged(samp)
    True
    >>> repository.uncheckoutResource(samp)
    reverted <Sample object> to version 3
    >>> transaction.commit()

    >>> samp.value
    43
    >>> repository.isResourceChanged(samp)
    False
    >>> version_id = repository.getVersionInfo(samp).version_id
    >>> version_id
    '3'

An old copy of an object can be "updated" to the most recent version
of an object:

    >>> ob = repository.getVersionOfResource(orig_history_id, orig_version_id)
    retrieved <Sample object>, version 1
    >>> ob.__name__ = "foo"
    >>> repository.isResourceUpToDate(ob)
    False
    >>> repository.getVersionInfo(ob).version_id
    '1'
    >>> repository.updateResource(ob, version_id)
    updated <Sample object> from version 1 to 3
    >>> repository.getVersionInfo(ob).version_id == version_id
    True
    >>> ob.value
    43

It's possible to get a list of all the versions of a particular object
from the repository as well.  We can use any copy of the object to
make the request:

    >>> list(repository.getVersionIds(samp))
    ['1', '2', '3']
    >>> list(repository.getVersionIds(ob))
    ['1', '2', '3']

No version information is available for objects that have not had
version control applied:

    >>> repository.getVersionIds(samp2)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.

    >>> repository.getVersionIds(42)
    Traceback (most recent call last):
      ...
    VersionControlError: Object is not under version control.


Naming specific revisions
-------------------------

Similar to other version control systems, specific versions may be
given symbolic names, and these names may be used to retrieve versions
from the repository.  This package calls these names *labels*; they
are similar to *tags* in CVS.

Labels can be assigned to objects that are checked into the
repository:

    >>> repository.labelResource(samp, 'my-first-label')
    created label my-first-label from version 3 of <Sample object>
    >>> repository.labelResource(samp, 'my-second-label')
    created label my-second-label from version 3 of <Sample object>

The list of labels assigned to some version of an object can be
retrieved using the repository's `getLabelsForResource()` method:

    >>> list(repository.getLabelsForResource(samp))
    ['my-first-label', 'my-second-label']

The labels can be retrieved using any object that refers to the same
line of history in the repository:

    >>> list(repository.getLabelsForResource(ob))
    ['my-first-label', 'my-second-label']

Labels can be used to retrieve specific versions of an object from the
repository:

    >>> repository.getVersionInfo(samp).version_id
    '3'
    >>> ob = repository.getVersionOfResource(orig_history_id, 'my-first-label')
    retrieved <Sample object>, version 3
    >>> repository.getVersionInfo(ob).version_id
    '3'

It's also possible to move a label from one version to another, but
only when this is specifically indicated as allowed:

    >>> ob = repository.getVersionOfResource(orig_history_id, orig_version_id)
    retrieved <Sample object>, version 1
    >>> ob.__name__ = "bar"
    >>> repository.labelResource(ob, 'my-second-label')
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    VersionControlError: The label my-second-label is already associated 
    with a version.

    >>> repository.labelResource(ob, 'my-second-label', force=True)
    created label my-second-label from version 1 of <Sample object>

Labels can also be used to update an object to a specific version:

    >>> repository.getVersionInfo(ob).version_id
    '1'
    >>> repository.updateResource(ob, 'my-first-label')
    updated <Sample object> from version 1 to 3
    >>> repository.getVersionInfo(ob).version_id
    '3'
    >>> ob.value
    43


Sticky settings
---------------

Similar to CVS, this package supports a sort of "sticky" updating: if
an object is updated to a specific date, determination of whether
it is up-to-date or changed is based on the version it was updated to.

    >>> repository.updateResource(samp, orig_version_id)
    updated <Sample object> from version 3 to 1
    >>> transaction.commit()

    >>> samp.value
    Traceback (most recent call last):
      ...
    AttributeError: 'Sample' object has no attribute 'value'

    >>> repository.getVersionInfo(samp).version_id == orig_version_id
    True
    >>> repository.isResourceChanged(samp)
    False
    >>> repository.isResourceUpToDate(samp)
    False

The `isResourceUpToDate()` method indicates whether
`checkoutResource()` will succeed or raise an exception:

    >>> repository.checkoutResource(samp)
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    VersionControlError: The selected resource has been updated to a
    particular version, label or date. The resource must be updated to
    the mainline or a branch before it may be checked out.


TODO: Figure out how to write date-based tests.  Perhaps the
repository should implement a hook used to get the current date so
tests can hook that.


Examining the change history
----------------------------

    >>> actions = {
    ...	  interfaces.ACTION_CHECKIN: "Check in",
    ...	  interfaces.ACTION_CHECKOUT: "Check out",
    ...	  interfaces.ACTION_UNCHECKOUT: "Uncheckout",
    ...	  interfaces.ACTION_UPDATE: "Update",
    ... }

    >>> entries = repository.getLogEntries(samp)
    >>> for entry in entries:
    ...	  print "Action:", actions[entry.action]
    ...	  print "Version:", entry.version_id
    ...	  print "Path:", entry.path
    ...	  if entry.message:
    ...	      print "Message:", entry.message
    ...	  print "--"
    Action: Update
    Version: 1
    Path: /samp
    --
    Action: Update
    Version: 3
    Path: /bar
    --
    Action: Update
    Version: 3
    Path: /foo
    --
    Action: Uncheckout
    Version: 3
    Path: /samp
    --
    Action: Check out
    Version: 3
    Path: /samp
    --
    Action: Check in
    Version: 3
    Path: /samp
    Message: sample checkin
    --
    Action: Check out
    Version: 2
    Path: /samp
    --
    Action: Update
    Version: 2
    Path: /samp
    --
    Action: Check in
    Version: 2
    Path: /ob
    --
    Action: Check out
    Version: 1
    Path: /ob
    --
    Action: Check in
    Version: 1
    Path: /samp
    Message: Initial checkin.
    --

Note that the entry with the checkin entry for version 3 includes the
comment passed to `checkinResource()`.

The version history also contains the principal id related to each
entry:

    >>> entries[0].user_id
    'bob'

Branches
--------

We may wish to create parallel versions of objects.  For example, we 
might want to create a version of content from an old version. We can
do this by making a branch. To make a branch, we need to get an object
for the version we want to branch from.  Here's we'll get an object
for revision 2:

    >>> obranch = repository.getVersionOfResource(orig_history_id, '2')
    retrieved <Sample object>, version 2
    >>> obranch.__name__ = "obranch"
    >>> root["obranch"] = obranch
    >>> repository.getVersionInfo(obranch).version_id
    '2'

Now we can use this object to make a branch:

    >>> repository.makeBranch(obranch)
    created branch 2.1 from version 2 of <Sample object>
    '2.1'

The `makeBranch` method returns the new branch name.  This is needed
to check out a working version for the branch.

To create a new version on the branch, we first have to check out the
object on the branch:

    >>> repository.updateResource(obranch, '2.1')
    updated <Sample object> from version 2 to 2
    >>> repository.checkoutResource(obranch)
    checked out <Sample object>, version 2

    >>> repository.getVersionInfo(obranch).version_id
    '2'

    >>> obranch.value
    42

    >>> obranch.value = 100

    >>> repository.checkinResource(obranch)
    checked in <Sample object>, version 2.1.1
    >>> transaction.commit()

    >>> repository.getVersionInfo(obranch).version_id
    '2.1.1'

Note that the new version number is the branch name followed by a
number on the branch.

Supporting separately versioned subobjects
------------------------------------------

`INonVersionedData` is responsible for dealing with parts of the object
state that should *not* be versioned as part of this object.  This can
include both subobjects that are versioned independently as well as
object-specific data that isn't part of the abstract resource the
version control framework is supporting.

For the sake of examples, let's create a simple class that actually
implements these two interfaces.  In this example, we'll create a
simple object that excludes any versionable subobjects and any
subobjects with names that start with "bob".  Note that, as for the
`Sample` class above, we're still careful to consider the values for
`__name__` and `__parent__` to be non-versioned:

    >>> def ignored_item(name, ob):
    ...     """Return True for non-versioned items."""
    ...     return (interfaces.IVersionable.providedBy(ob)
    ...             or name.startswith("bob")
    ...             or (name in ["__name__", "__parent__"]))

    >>> class SampleContainer(Sample):
    ...   
    ...     # Methods defined by INonVersionedData
    ...     def listNonVersionedObjects(self):
    ...         return [ob for (name, ob) in self.__dict__.items()
    ...                 if ignored_item(name, ob)
    ...                 ]
    ...
    ...     def removeNonVersionedData(self):
    ...         for name, value in self.__dict__.items():
    ...             if ignored_item(name, value):
    ...                 del self.__dict__[name]
    ...
    ...     def getNonVersionedData(self):
    ...         return [(name, ob) for (name, ob) in self.__dict__.items()
    ...                 if ignored_item(name, ob)
    ...                 ]
    ...
    ...     def restoreNonVersionedData(self, data):
    ...         for name, value in data:
    ...             if name not in self.__dict__:
    ...                 self.__dict__[name] = value

Let's take a look at how the `INonVersionedData` interface is used.
We'll start by creating an instance of our sample container and
storing it in the database:

    >>> box = SampleContainer()
    >>> box.__name__ = "box"
    >>> root[box.__name__] = box

We'll also add some contained objects:

    >>> box.aList = [1, 2, 3]

    >>> samp1 = Sample()
    >>> samp1.__name__ = "box/samp1"
    >>> samp1.__parent__ = box
    >>> box.samp1 = samp1

    >>> box.bob_list = [3, 2, 1]

    >>> bob_samp = Sample()
    >>> bob_samp.__name__ = "box/bob_samp"
    >>> bob_samp.__parent__ = box
    >>> box.bob_samp = bob_samp

    >>> transaction.commit()

Let's apply version control to the container:

    >>> repository.applyVersionControl(box)
    applied version control to <SampleContainer object>

We'll start by showing some basics of how the INonVersionedData
interface is used.  

The `getNonVersionedData()`, `removeNonVersionedData()`, and
`restoreNonVersionedData()` methods work together, allowing the
version control framework to ensure that data that is not versioned as
part of the object is not lost or inappropriately stored in the
repository as part of version control operations.

The basic pattern for this trio of operations is simple:

1. Use `getNonVersionedData()` to get a value that can be used to
   restore the current non-versioned data of the object.

2. Use `removeNonVersionedData()` to remove any non-versioned data
   from the object so it doesn't enter the repository as object state
   is copied around.

3. Make object state changes based on the version control operation
   being performed.

4. Use `restoreNonVersionedData()` to restore the data retrieved using
   `getNonVersionedData()`.

This is fairly simple to see in an example.  Step 1 is to save the
non-versioned data:

    >>> saved = box.getNonVersionedData()

While the version control framework treats this as an opaque value, we
can take a closer look to make sure we got what we expected (since we
know our implementation):

    >>> names = [name for (name, ob) in saved]
    >>> names.sort()
    >>> names
    ['__name__', 'bob_list', 'bob_samp', 'samp1']

Step 2 is to remove the data from the object:

    >>> box.removeNonVersionedData()

The non-versioned data should no longer be part of the object:

    >>> box.bob_samp
    Traceback (most recent call last):
      ...
    AttributeError: 'SampleContainer' object has no attribute 'bob_samp'

While versioned data should remain present:

    >>> box.aList
    [1, 2, 3]

At this point, the version control framework will perform any
appropriate state copies are needed.

Once that's done, `restoreNonVersionedData()` will be called with the
saved data to perform the restore operation:

    >>> box.restoreNonVersionedData(saved)

We can verify that the restoraion has been performed by checking the
non-versioned data:

    >>> box.bob_list
    [3, 2, 1]
    >>> type(box.samp1)
    <class 'zope.app.versioncontrol.README.Sample'>

We can see how this is affects object state by making some changes to
the container object's versioned and non-versioned data and watching
how those attributes are affected by updating to specific versions
using `updateResource()` and retrieving specific versions using
`getVersionOfResource()`.  Let's start by generating some new
revisions in the repository:

    >>> repository.checkoutResource(box)
    checked out <SampleContainer object>, version 1
    >>> transaction.commit()
    >>> version_id = repository.getVersionInfo(box).version_id

    >>> box.aList.append(4)
    >>> box.bob_list.append(0)
    >>> repository.checkinResource(box)
    checked in <SampleContainer object>, version 2
    >>> transaction.commit()

    >>> box.aList
    [1, 2, 3, 4]
    >>> box.bob_list
    [3, 2, 1, 0]

    >>> repository.updateResource(box, version_id)
    updated <SampleContainer object> from version 2 to 1
    >>> box.aList
    [1, 2, 3]
    >>> box.bob_list
    [3, 2, 1, 0]

The remaining `listNonVersionedObjects()` method of the
`INonVersionedData` interface is a little different, but remains very
tightly tied to the details of the object's state. It should return
a sequence of all the objects that should not be copied as part of the
object's state.  The difference between this method and
`getNonVersionedData()` may seem simple, but is significant in
practice.

The `listNonVersionedObjects()` method allows the version control
framework to identify data that should not be included in state
copies, without saying anything else about the data.  The
`getNonVersionedData()` method allows the INonVersionedData
implementation to communicate with itself (by providing data to be
restored by the `restoreNonVersionedData()` method) without exposing
any information about how it communicates with itself (it could store
all the relevant data into an external file and use the value returned
to locate the state file again, if that was needed for some reason).
