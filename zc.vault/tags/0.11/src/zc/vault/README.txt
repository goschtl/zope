=====
Vault
=====

Vaults model versioned containers.  A single revision of a vault is
typically viewed and (if not yet frozen) manipulated as an "inventory".
Inventories actually manipulate lower-level objects called manifests
that are only touched on in this document.  Inventories are the primary
API.

Inventories *model* containers, but are not traditional mappings:
containment is external to the actual objects in the inventory.  You
must query the inventory to discover the hierarchy, rather than the
objects themselves.  For instance, if you put an object in an inventory
and want to treat it as a versioned folder, you don't put children in
the object, but in the inventory node that wraps the object.  This will
be demonstrated repeatedly and in-depth below.

Vaults only contain versioned, frozen manifests, accessed as
inventories.  Working inventories can be made from any inventory in a
vault.  They can then be modified, and committed themselves in the
vault. Committing an inventory freezes it and all objects it
"contains".

Let's look at an example.  Vaults store manifests, so when you first
create one it is empty.  Vaults have a basic sequence API, so a `len`
will return `0`.

    >>> from zc.vault.vault import Vault, Inventory
    >>> from zc.vault.core import Manifest
    >>> from zc.vault import interfaces
    >>> from zope.interface.verify import verifyObject
    >>> v = Vault()
    >>> len(v)
    0
    >>> verifyObject(interfaces.IVault, v)
    True

The last inventory--the -1 index--is the current one.  A shorthand to this
inventory is the inventory attribute.

    >>> v.inventory # None

Vaults and inventories must have a database connection in order to store their
data.  We'll assume we have a ZODB folder named "app" in which we can store
our information.  This is set up in tests.py when this file is run as a test.

    >>> app['vault'] = v

Creating an initial working inventory requires us to merely instantiate it.
Usually we pass a versioned inventory on which to base the new inventory, but
without that we at least pass the vault.

    >>> i = Inventory(vault=v)
    >>> verifyObject(interfaces.IInventory, i)
    True

Technically, what we have done is create a manifest--the core API for managing
the contents--and wrapped an inventory API around it.

    >>> verifyObject(interfaces.IManifest, i.manifest)
    True

We could have created the manifest explicitly instead.

    >>> manifest = Manifest(vault=v)
    >>> verifyObject(interfaces.IManifest, manifest)
    True
    >>> i = Inventory(manifest)
    >>> verifyObject(interfaces.IInventory, i)
    True

Inventories--or at least the manifests on which they rely--must be
stored somewhere in the database before being committed. They provide
zope.app.location.interfaces.ILocation so that they can be stored in
standard Zope containers as they are being developed.

    >>> app['inventory'] = i

Inventories have contents that can seem to directly contain objects.  They have
a mapping API, and follow the IInventoryContents interface.

    >>> verifyObject(interfaces.IInventoryContents, i.contents)
    True
    >>> len(i.contents.keys())
    0
    >>> len(i.contents.values())
    0
    >>> len(i.contents.items())
    0
    >>> list(i.contents)
    []
    >>> i.contents.get('mydemo') # None
    >>> 'mydemo' in i
    False
    >>> i.contents['mydemo']
    Traceback (most recent call last):
    ...
    KeyError: 'mydemo'
    >>> del i.contents['mydemo']
    Traceback (most recent call last):
    ...
    KeyError: 'mydemo'

(ADVANCED SIDE NOTE: feel free to ignore)

The contents object is an API convenience to wrap a relationship.
Relationships connect a token to various pieces of information.  The
token for all inventory contents (the top node) is stored on the vault
as the top_token attribute, and lower levels get unique tokens that
represent a given location in a vault across inventories.

Contents and items (seen below) essentially get all their data from the
relationships and the associated manifest that holds them.

    >>> verifyObject(interfaces.IRelationship, i.contents.relationship)
    True
    >>> i.contents.relationship.token == i.vault.top_token
    True
    >>> verifyObject(interfaces.IRelationshipContainment,
    ...              i.contents.relationship.containment)
    True
    >>> i.contents.relationship.object # None, because contents.

(end ADVANCED SIDE NOTE)

Because it is often convenient to use tokens as a globally unique identifier
of a particular object, all inventory items have a "token" attribute.

    >>> i.contents.token
    1234567

Unlike typical Zope 3 containment as defined in zope.app.container, this
containment does not affect the __parent__ or __name__ of the object.

All objects stored in an inventory must be None, or be adaptable to
zope.app.keyreference.interfaces.IKeyReference.  In standard Zope 3,
this includes any instance of a class that extends
persistent.Persistent.

All non-None objects must also be adaptable to
zc.freeze.interfaces.IFreezable.

Here, we create an object, add it to the application, and try to add it to
an inventory.

    >>> import persistent
    >>> from zope.app.container.contained import Contained
    >>> class Demo(persistent.Persistent, Contained):
    ...     def __repr__(self):
    ...         return "<%s %r>" % (self.__class__.__name__, self.__name__)
    ...
    >>> app['d1'] = Demo()
    >>> i.contents['mydemo'] = app['d1']
    Traceback (most recent call last):
    ...
    ValueError: can only place freezable objects in vault, or None

This error occurs because committing an inventory must freeze itself
and freeze all of its contained objects, so that looking at an
historical inventory displays the objects as they were at the time of
commit.  Here's a simple demo adapter for the Demo objects.  We also
declare that Demo is IFreezable, an important marker.

    >>> import pytz
    >>> import datetime
    >>> from zope import interface, component, event
    >>> from zc.freeze.interfaces import (
    ...     IFreezing, ObjectFrozenEvent, IFreezable)
    >>> from zc.freeze import method
    >>> class DemoFreezingAdapter(object):
    ...     interface.implements(IFreezing)
    ...     component.adapts(Demo)
    ...     def __init__(self, context):
    ...         self.context = context
    ...     @property
    ...     def _z_frozen(self):
    ...         return (getattr(self.context, '_z__freeze_timestamp', None)
    ...                 is not None)
    ...     @property
    ...     def _z_freeze_timestamp(self):
    ...         return getattr(self.context, '_z__freeze_timestamp', None)
    ...     @method
    ...     def _z_freeze(self):
    ...         self.context._z__freeze_timestamp = datetime.datetime.now(
    ...             pytz.utc)
    ...         event.notify(ObjectFrozenEvent(self))
    ...
    >>> component.provideAdapter(DemoFreezingAdapter)
    >>> interface.classImplements(Demo, IFreezable)

As an aside, it's worth noting that the manifest objects provide
IFreezing natively, so they can already be queried for the freezing
status and timestamp without adaptation.  When a manifest is frozen,
all "contained" objects should be frozen as well.

It's not frozen now--and neither is our demo instance.

    >>> manifest._z_frozen
    False
    >>> IFreezing(app['d1'])._z_frozen
    False

Now that Demo instances are freezable we can add the object to the inventory.
That means adding and removing objects.  Here we add one.

    >>> i.contents['mydemo'] = app['d1']
    >>> i.contents['mydemo']
    <Demo u'd1'>
    >>> i.__parent__ is app
    True
    >>> i.contents.__parent__ is i
    True
    >>> i.contents.get('mydemo')
    <Demo u'd1'>
    >>> list(i.contents.keys())
    ['mydemo']
    >>> i.contents.values()
    [<Demo u'd1'>]
    >>> i.contents.items()
    [('mydemo', <Demo u'd1'>)]
    >>> list(i.contents)
    ['mydemo']
    >>> 'mydemo' in i.contents
    True

Now our effective hierarchy simply looks like this::

                     (top node)
                         |
                      'mydemo'
                   (<Demo u'd1'>)

We will update this hierarchy as we proceed.

Adding an object fires a (special to the package!) IObjectAdded event.
This event is not from the standard lifecycleevents package because
that one has a different connotation--for instance, as noted before,
putting an object in an inventory does not set the __parent__ or
__name__ (unless it does not already have a location, in which case it
is put in a possibly temporary "held" container, discussed below).

    >>> interfaces.IObjectAdded.providedBy(events[-1])
    True
    >>> isinstance(events[-1].object, int)
    True
    >>> i.manifest.get(events[-1].object).object is app['d1']
    True
    >>> events[-1].mapping is i.contents.relationship.containment
    True
    >>> events[-1].key
    'mydemo'

Now we remove the object.

    >>> del i.contents['mydemo']
    >>> len(i.contents.keys())
    0
    >>> len(i.contents.values())
    0
    >>> len(i.contents.items())
    0
    >>> list(i.contents)
    []
    >>> i.contents.get('mydemo') # None
    >>> 'mydemo' in i.contents
    False
    >>> i.contents['mydemo']
    Traceback (most recent call last):
    ...
    KeyError: 'mydemo'
    >>> del i.contents['mydemo']
    Traceback (most recent call last):
    ...
    KeyError: 'mydemo'

Removing an object fires a special IObjectRemoved event (again, not from
lifecycleevents).

    >>> interfaces.IObjectRemoved.providedBy(events[-1])
    True
    >>> isinstance(events[-1].object, int)
    True
    >>> i.manifest.get(events[-1].object).object is app['d1']
    True
    >>> events[-1].mapping is i.contents.relationship.containment
    True
    >>> events[-1].key
    'mydemo'

In addition to a mapping API, the inventory contents support an ordered
container API very similar to the ordered container in
zope.app.container.ordered.  The ordered nature of the contents mean that
iterating is on the basis of the order in which objects were added, by default
(earliest first); and that the inventory supports an "updateOrder" method.
The method takes an iterable of names in the container: the new order will be
the given order.  If the set of given names differs at all with the current
set of keys, the method will raise ValueError.

    >>> i.contents.updateOrder(())
    >>> i.contents.updateOrder(('foo',))
    Traceback (most recent call last):
    ...
    ValueError: Incompatible key set.
    >>> i.contents['donald'] = app['d1']
    >>> app['b1'] = Demo()
    >>> i.contents['barbara'] = app['b1']
    >>> app['c1'] = Demo()
    >>> app['a1'] = Demo()
    >>> i.contents['cathy'] = app['c1']
    >>> i.contents['abe'] = app['a1']
    >>> list(i.contents.keys())
    ['donald', 'barbara', 'cathy', 'abe']
    >>> i.contents.values()
    [<Demo u'd1'>, <Demo u'b1'>, <Demo u'c1'>, <Demo u'a1'>]
    >>> i.contents.items() # doctest: +NORMALIZE_WHITESPACE
    [('donald', <Demo u'd1'>), ('barbara', <Demo u'b1'>),
     ('cathy', <Demo u'c1'>), ('abe', <Demo u'a1'>)]
    >>> list(i.contents)
    ['donald', 'barbara', 'cathy', 'abe']
    >>> 'cathy' in i.contents
    True
    >>> i.contents.updateOrder(())
    Traceback (most recent call last):
    ...
    ValueError: Incompatible key set.
    >>> i.contents.updateOrder(('foo',))
    Traceback (most recent call last):
    ...
    ValueError: Incompatible key set.
    >>> i.contents.updateOrder(iter(('abe', 'barbara', 'cathy', 'donald')))
    >>> list(i.contents.keys())
    ['abe', 'barbara', 'cathy', 'donald']
    >>> i.contents.values()
    [<Demo u'a1'>, <Demo u'b1'>, <Demo u'c1'>, <Demo u'd1'>]
    >>> i.contents.items() # doctest: +NORMALIZE_WHITESPACE
    [('abe', <Demo u'a1'>), ('barbara', <Demo u'b1'>),
     ('cathy', <Demo u'c1'>), ('donald', <Demo u'd1'>)]
    >>> list(i.contents)
    ['abe', 'barbara', 'cathy', 'donald']
    >>> i.contents.updateOrder(('abe', 'cathy', 'donald', 'barbara', 'edward'))
    Traceback (most recent call last):
    ...
    ValueError: Incompatible key set.
    >>> list(i.contents)
    ['abe', 'barbara', 'cathy', 'donald']
    >>> del i.contents['cathy']
    >>> list(i.contents.keys())
    ['abe', 'barbara', 'donald']
    >>> i.contents.values()
    [<Demo u'a1'>, <Demo u'b1'>, <Demo u'd1'>]
    >>> i.contents.items() # doctest: +NORMALIZE_WHITESPACE
    [('abe', <Demo u'a1'>), ('barbara', <Demo u'b1'>), ('donald', <Demo u'd1'>)]
    >>> list(i.contents)
    ['abe', 'barbara', 'donald']
    >>> i.contents.updateOrder(('barbara', 'abe', 'donald'))
    >>> list(i.contents.keys())
    ['barbara', 'abe', 'donald']
    >>> i.contents.values()
    [<Demo u'b1'>, <Demo u'a1'>, <Demo u'd1'>]

Now our _`hierarchy` looks like this::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>

Reordering a container fires an event.

    >>> interfaces.IOrderChanged.providedBy(events[-1])
    True
    >>> events[-1].object is i.contents.relationship.containment
    True
    >>> events[-1].old_keys
    ('abe', 'barbara', 'donald')

In some circumstances it's easier to set the new order from a set of
tokens.  In that case the "updateOrderFromTokens" method is useful.

    >>> def getToken(key):
    ...     return i.contents(k).token

    >>> new_order = [getToken(k) for k in ('abe', 'donald', 'barbara')]
    >>> i.contents.updateOrderFromTokens(new_order)
    >>> list(i.contents.keys())
    ['abe', 'donald', 'barbara']

Just like "updateOrder", an event is fired.

    >>> interfaces.IOrderChanged.providedBy(events[-1])
    True
    >>> events[-1].object is i.contents.relationship.containment
    True
    >>> events[-1].old_keys
    ('barbara', 'abe', 'donald')

It's just as easy to put them back so that the `hierarchy`_ still looks the
same as it did at the end of the previous example.

    >>> new_order = [getToken(k) for k in ('barbara', 'abe', 'donald')]
    >>> i.contents.updateOrderFromTokens(new_order)
    >>> list(i.contents.keys())
    ['barbara', 'abe', 'donald']

As noted in the introduction to this document, the versioned hierarchy
is kept external from the objects themselves.  This means that objects
that are not containers themselves can still be branch
nodes--containers, of a sort--within an inventory.  In fact, until a
reasonable use case emerges for the pattern, the author discourages the
use of true containers within a vault as branch nodes: two dimensions
of "containerish" behavior is too confusing.

In order to get an object that can act as a container for one of the objects
in the inventory, one calls the inventory contents: "i.contents('abe')".  This
returns an IInventoryItem, if the key exists.  It raises a KeyError for a
missing key by default, but can take a default.

    >>> i.contents['abe']
    <Demo u'a1'>
    >>> item = i.contents('abe')
    >>> verifyObject(interfaces.IInventoryItem, item)
    True
    >>> i.contents('foo')
    Traceback (most recent call last):
    ...
    KeyError: 'foo'
    >>> i.contents('foo', None) # None

IInventoryItems extend IInventoryContents to add an 'object' attribute, which
is the object they represent. Like IInventoryContents, a mapping interface
allows one to manipulate the hierarchy beneath the top level. For instance,
here we effectively put the 'cathy' demo object in the container space of the
'abe' demo object.

    >>> item.object
    <Demo u'a1'>
    >>> item.name
    'abe'
    >>> item.parent.relationship is i.contents.relationship
    True
    >>> item.__parent__ is item.inventory
    True
    >>> list(item.values())
    []
    >>> list(item.keys())
    []
    >>> list(item.items())
    []
    >>> list(item)
    []
    >>> item.get('foo') # None
    >>> item['foo']
    Traceback (most recent call last):
    ...
    KeyError: 'foo'
    >>> item('foo')
    Traceback (most recent call last):
    ...
    KeyError: 'foo'
    >>> item['catherine'] = app['c1']
    >>> item['catherine']
    <Demo u'c1'>
    >>> item.get('catherine')
    <Demo u'c1'>
    >>> list(item.keys())
    ['catherine']
    >>> list(item.values())
    [<Demo u'c1'>]
    >>> list(item.items())
    [('catherine', <Demo u'c1'>)]
    >>> catherine = item('catherine')
    >>> catherine.object
    <Demo u'c1'>
    >>> catherine.name
    'catherine'
    >>> catherine.parent.name
    'abe'
    >>> catherine.parent.object
    <Demo u'a1'>
    >>> list(catherine.keys())
    []

Now our hierarchy looks like this::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>

It's worthwhile noting that the same object can be in multiple places in an
inventory.  This does not duplicate the hierarchy, or keep changes in sync.
If desired, this policy should be performed in code that uses the vault;
similarly if a vault should only contain an object in one location at a time,
this should be enforced in code that uses a vault.

    >>> i.contents('abe')('catherine')['anna'] = app['a1']
    >>> i.contents('abe')('catherine').items()
    [('anna', <Demo u'a1'>)]
    >>> i.contents('abe')('catherine')('anna').parent.parent.object
    <Demo u'a1'>

Now our hierarchy looks like this::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

Even though a1 contains c1 contains a1, this does not constitute a cycle: the
hierarchy is separate from the objects.

InventoryItems and InventoryContents are currently created on the fly, and
not persisted.  They should be compared with "==", not "is".  They represent
a persistent core data object that provides zc.vault.interfaces.IRelationship.
The IRelationship itself is hidden from the majority of this discussion and
only introduced at the end of the document.  But in any case...

    >>> i.contents('abe') is i.contents('abe')
    False
    >>> i.contents('abe') == i.contents('abe')
    True
    >>> i.contents is i.contents
    False
    >>> i.contents == i.contents
    True
    >>> i.contents == None
    False
    >>> i.contents('abe') == None
    False

Comparing inventories will also compare their contents:

    >>> i == None
    False
    >>> i == i
    True
    >>> i != i
    False

Another important characteristic of inventory items is that they continue to
have the right information even as objects around them are changed--for
instance, if an object's parent is changed from one part of the hierarchy to
another (see `moveTo`, below), an item generated before the move will still
reflect the change correctly.

It's worth noting that, thanks to the wonder of the zc.shortcut code, views can
exist for the object and also, from a proxy, have access to the InventoryItem's
information: this needs to be elaborated (TODO).

Now we'll try to commit.

    >>> v.commit(i) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ConflictError: <zc.vault.core.Manifest object at ...>

Conflicts?  We don't need no stinking conflicts!  We didn't even merge!  Where
did this come from?

The default vault takes a very strict approach to keeping track of conflicts:
for instance, if you add something and then delete it in the same inventory,
it will regard this as an "orphan conflict": a change that happened in this
inventory that will not be committed.  You must explicitly say that it is
OK for these orphaned changes to be lost.  Let's look at the orphans.

    >>> orphans = list(i.iterOrphanConflicts())
    >>> sorted(repr(item.object) for item in orphans)
    ["<Demo u'c1'>", "<Demo u'd1'>"]
    >>> orphans[0].parent # None
    >>> orphans[0].name # None

Ah yes--you can see that we deleted these objects above: we deleted "mydemo"
(d1) and cathy (c1).  We'll just tell the inventory that it is ok to not
include them.  If vault clients want to have more automation so that deletions
automatically resolve, then they have the tools to do so.  After the
resolution, iterOrphanConflicts will then be empty, and iterOrphanResolutions
will include the objects.

    >>> for o in orphans:
    ...     o.resolveOrphanConflict()
    ...
    >>> len(list(i.iterOrphanConflicts()))
    0
    >>> sorted(repr(item.object) for item in i.iterOrphanResolutions())
    ["<Demo u'c1'>", "<Demo u'd1'>"]

Now when we commit, all objects will be versioned, and we will receive events
for the freezing and the committing.  The events list represents recent
events; when this document is run as a test, it is populated by listening for
all events and attaching them to the list.

    >>> v.commit(i)
    >>> interfaces.IManifestCommitted.providedBy(events[-1])
    True
    >>> events[-1].object is manifest
    True
    >>> manifest.__parent__ is v
    True
    >>> IFreezing(app['a1'])._z_frozen
    True
    >>> IFreezing(app['b1'])._z_frozen
    True
    >>> IFreezing(app['c1'])._z_frozen
    True
    >>> IFreezing(app['d1'])._z_frozen
    True
    >>> manifest._z_frozen
    True
    >>> v.manifest is manifest
    True
    >>> len(v)
    1

After the committing, the inventory enforces the freeze: no more changes
can be made.

    >>> i.contents['foo'] = Demo()
    Traceback (most recent call last):
    ...
    FrozenError
    >>> i.contents.updateOrder(())
    Traceback (most recent call last):
    ...
    FrozenError
    >>> i.contents('abe')('catherine')['foo'] = Demo()
    Traceback (most recent call last):
    ...
    FrozenError

    >>> v.manifest._z_frozen
    True

Enforcing the freezing of the inventory's objects is the responsibility of
other code or configuration, not the vault package.

The manifest now has an __name__ which is the string of its index.  This is
of very limited usefulness, but with the right traverser might still allow
items in the held container to be traversed to.

    >>> i.manifest.__name__
    u'0'

After every commit, the vault should be able to determine the previous and
next versions of every relationship.  Since this is the first commit, previous
will be None, but we'll check it now anyway, building a function that checks
the most recent manifest of the vault.

    >>> def checkManifest(m):
    ...     v = m.vault
    ...     for r in m:
    ...         p = v.getPrevious(r)
    ...         assert (p is None or
    ...                 r.__parent__.vault is not v or
    ...                 p.__parent__.vault is not v or
    ...                 v.getNext(p) is r)
    ...
    >>> checkManifest(v.manifest)

Creating a new working inventory requires a new manifest, based on the old
manifest.

For better or worse, the package offers four approaches to this.  We
can create a new working inventory by specifying a vault, from which
the most recent manifest will be selected, and "mutable=True";

    >>> i = Inventory(vault=v, mutable=True)
    >>> manifest = i.manifest
    >>> manifest._z_frozen
    False

by specifying an inventory, from which its manifest will be
extracted, and "mutable=True";

    >>> i = Inventory(inventory=v.inventory, mutable=True)
    >>> manifest = i.manifest
    >>> manifest._z_frozen
    False

by specifying a versioned manifest and "mutable=True";

    >>> i = Inventory(v.manifest, mutable=True)
    >>> manifest = i.manifest
    >>> manifest._z_frozen
    False

or by specifying a mutable manifest.

    >>> i = Inventory(Manifest(v.manifest))
    >>> i.manifest._z_frozen
    False

These multiple spellings should be reexamined at a later date, and may have
a deprecation period.  The last spelling--an explicit pasing of a manifest to
an inventory--is the most likely to remain stable, because it clearly allows
instantiation of the inventory wrapper for a working manifest or a versioned
manifest.

Note that, as mentioned above, the inventory is just an API wrapper around the
manifest: therefore, changes to inventories that share a manifest will be
shared among them.

    >>> i_extra = Inventory(i.manifest)
    >>> manifest._z_frozen
    False

In any case, we now have an inventory that has the same contents as the
original.

    >>> i.contents.keys() == v.inventory.contents.keys()
    True
    >>> i.contents['barbara'] is v.inventory.contents['barbara']
    True
    >>> i.contents['abe'] is v.inventory.contents['abe']
    True
    >>> i.contents['donald'] is v.inventory.contents['donald']
    True
    >>> i.contents('abe')['catherine'] is v.inventory.contents('abe')['catherine']
    True
    >>> i.contents('abe')('catherine')['anna'] is \
    ... v.inventory.contents('abe')('catherine')['anna']
    True

We can now manipulate the new inventory as we did the old one.

    >>> app['d2'] = Demo()
    >>> i.contents['donald'] = app['d2']
    >>> i.contents['donald'] is v.inventory.contents['donald']
    False

Now our hierarchy looks like this::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd2'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

Now we can observe our local changes.  One way to do this is to examine
the results of iterChangedItems.

    >>> len(list(i.iterChangedItems()))
    1
    >>> iter(i.iterChangedItems()).next() == i.contents('donald')
    True

Another is to look at each inventory item.  The items specify the type of
information in the item: whether it is from the 'base', the 'local' changes,
or a few other options we'll see when we examine merges.

    >>> i.contents('abe').type
    'base'
    >>> i.contents('donald').type
    'local'

This will be true whether or not the change is returned to the original value
by hand.

    >>> i.contents['donald'] = app['d1']
    >>> v.inventory.contents['donald'] is i.contents['donald']
    True

However, unchanged local copies are not included in the iterChangedItems
results; they are also discarded on commit, as we will see below.

    >>> len(list(i.iterChangedItems()))
    0

Now our hierarchy looks like this again::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

Each inventory item represents a single collection of data that stores an
object and its effective hierarchy.  Therefore, changing either (or both) will
generate a local inventory item.

    >>> app['e1'] = Demo()
    >>> i.contents('barbara').type
    'base'
    >>> i.contents('barbara')['edna'] = app['e1']
    >>> i.contents('barbara').type
    'local'
    >>> i.contents['barbara'] is v.inventory.contents['barbara']
    True
    >>> len(list(i.iterChangedItems()))
    2

Those are two changes: one new node (edna) and one changed node (barbara got a
new child).

Now our hierarchy looks like this ("*" indicates a changed node)::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'*  'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>
                 /            |
                /             |
             'edna'*     'catherine'
         <Demo u'e1'>    <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

Modifying the collection of the top level contents means that we have a change
as well: even though the inventory does not keep track of a single object at
the top of the hierarchy, it does keep track of containment at the top level.

    >>> i.contents.type
    'base'
    >>> app['f1'] = Demo()
    >>> i.contents['fred'] = app['f1']
    >>> i.contents.type
    'local'
    >>> len(list(i.iterChangedItems()))
    4

That's four changes: edna, barbara, fred, and the top node.

Now our hierarchy looks like this ("*" indicates a changed or new node)::

                               (top node)*
                              /   /  \  \
                          ----   /    \  ---------
                         /      |      |          \
                'barbara'*    'abe'   'donald'     'fred'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>  <Demo u'f1'>
                 /            |
                /             |
             'edna'*     'catherine'
         <Demo u'e1'>    <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

You can actually examine the base from the changed item--and even switch back.
The `base_item` attribute always returns an item with the original object and
containment.  The `local_item` returns an item with local changes, or None if
no changes have been made.  A `select` method allows you to switch the given
item to look at one or the other by default.  The readonly `selected`
attribute allows introspection.

    >>> list(i.contents.keys())
    ['barbara', 'abe', 'donald', 'fred']
    >>> i.contents == i.contents.local_item
    True
    >>> list(i.contents('barbara').keys())
    ['edna']
    >>> i.contents('barbara') == i.contents('barbara').local_item
    True
    >>> i.contents('barbara').local_item.selected
    True
    >>> i.contents('barbara').base_item.selected
    False
    >>> len(i.contents('barbara').base_item.keys())
    0
    >>> list(i.contents.base_item.keys())
    ['barbara', 'abe', 'donald']
    >>> i.contents('barbara').base_item.select()
    >>> len(list(i.iterChangedItems()))
    3

That's fred, the top level, /and/ edna: edna still is a change, even though
she is inaccessible with the old version of barbara.  If we were to commit now,
we would have to resolve the orphan, as shown above.

    >>> v.commit(i) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ConflictError: <zc.vault.core.Manifest object at ...>
    >>> list(item.object for item in i.iterOrphanConflicts())
    [<Demo u'e1'>]

Let's look around a little more and switch things back:

    >>> i.contents('barbara').local_item.selected
    False
    >>> i.contents('barbara').base_item.selected
    True
    >>> len(i.contents('barbara').keys())
    0
    >>> i.contents('barbara') == i.contents('barbara').local_item
    False
    >>> i.contents('barbara') == i.contents('barbara').base_item
    True
    >>> i.contents('barbara').local_item.select()
    >>> len(list(i.iterChangedItems()))
    4
    >>> i.contents('barbara').local_item.selected
    True
    >>> i.contents('barbara').base_item.selected
    False
    >>> list(i.contents('barbara').keys())
    ['edna']

The inventory has booleans to examine whether a base item or local item exists,
as a convenience (and optimization opportunity).

    >>> i.contents('fred').has_local
    True
    >>> i.contents('fred').has_base
    False
    >>> i.contents('abe')('catherine').has_local
    False
    >>> i.contents('abe')('catherine').has_base
    True
    >>> i.contents('barbara').has_local
    True
    >>> i.contents('barbara').has_base
    True

It also has four other similar properties, `has_updated`, `has_suggested`,
`has_modified`, and `has_merged`, which we will examine later.

Before we commit we are going to make one more change to the inventory.  We'll
make a change to "anna".  Notice how we spell this in the code: it this is the
first object we have put in an inventory that does not already have a location
in app.  When an inventory is asked to version an object without an ILocation,
it stores it in a special folder on the manifest named "held".  Held objects
are assigned names using the standard Zope 3 name chooser pattern and can be
moved out even after being versioned.  In this case we will need to register a
name chooser for our demo objects.  We'll use the standard one.

    >>> from zope.app.container.contained import NameChooser
    >>> from zope.app.container.interfaces import IWriteContainer
    >>> component.provideAdapter(NameChooser, adapts=(IWriteContainer,))
    >>> len(i.manifest.held)
    0
    >>> i.contents('abe')('catherine')['anna'] = Demo()
    >>> len(i.manifest.held)
    1
    >>> i.manifest.held.values()[0] is i.contents('abe')('catherine')['anna']
    True

Now our hierarchy looks like this ("*" indicates a changed or new node)::

                               (top node)*
                              /   /  \  \
                          ----   /    \  ---------
                         /      |      |          \
                'barbara'*    'abe'   'donald'     'fred'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>  <Demo u'f1'>
                 /            |
                /             |
             'edna'*     'catherine'
         <Demo u'e1'>    <Demo u'c1'>
                              |
                              |
                           'anna'*
                         <Demo ...>

In our previous inventory commit, objects were versioned in place.  The vault
code provides a hook to generate objects for committing to vault: it tries to
adapt objects it wants to version to zc.vault.interfaces.IVersionFactory.
This interface specifies any callable object.  Let's provide an example.

The policy here is that if the object is in the inventories' held container,
just return it, but otherwise "make a copy"--which for our demo just makes a
new instance and slams the old one's name on it as an attribute.

    >>> @interface.implementer(interfaces.IVersionFactory)
    ... @component.adapter(interfaces.IVault)
    ... def versionFactory(vault):
    ...     def makeVersion(obj, manifest):
    ...         if obj.__parent__ is manifest.held:
    ...             return obj
    ...         res = Demo()
    ...         res.source_name = obj.__name__
    ...         return res
    ...     return makeVersion
    ...
    >>> component.provideAdapter(versionFactory)

Let's commit now, to show the results.  We'll discard the change to barbara.

    >>> len(list(i.iterChangedItems()))
    5
    >>> i.contents('barbara')('edna').resolveOrphanConflict()
    >>> i.contents('barbara').base_item.select()
    >>> len(list(i.iterChangedItems()))
    4

Edna is included even though she is resolved.

Now our hierarchy looks like this ("*" indicates a changed or new node)::

                               (top node)*
                              /   /  \  \
                          ----   /    \  ---------
                         /      |      |          \
                'barbara'     'abe'   'donald'     'fred'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>  <Demo u'f1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'*
                         <Demo ...>

    >>> changed = dict(
    ...     (getattr(item, 'name', None), item)
    ...     for item in i.iterChangedItems())
    >>> changed['anna'].parent.name
    'catherine'
    >>> changed['fred'].object
    <Demo u'f1'>
    >>> changed['edna'].object
    <Demo u'e1'>
    >>> list(changed[None].keys())
    ['barbara', 'abe', 'donald', 'fred']
    >>> old_objects = dict(
    ...     (k, i.object) for k, i in changed.items() if k is not None)
    >>> v.commit(i)
    >>> checkManifest(v.manifest)
    >>> len(v)
    2
    >>> v.manifest is i.manifest
    True
    >>> v.inventory == i
    True

We committed the addition of fred, but not the addition of edna.  Once an
inventory is committed, unselected changes are discarded.  Also, as mentioned
above, the data for local item for `donald` has been discarded, since it did
not include any changes.

    >>> i.contents.local_item == i.contents
    True
    >>> i.contents.type
    'local'
    >>> i.contents('barbara').local_item # None
    >>> i.contents('barbara').type
    'base'
    >>> i.contents('donald').local_item # None
    >>> i.contents('donald').type
    'base'
    >>> IFreezing(app['e1'])._z_frozen
    False

Our changes are a bit different than what we had when we began the commit,
because of the version Factory.  The f1 is not versioned, because we have made
a copy instead.

    >>> IFreezing(app['f1'])._z_frozen
    False
    >>> new_changed = dict(
    ...     (getattr(item, 'name', None), item)
    ...     for item in i.iterChangedItems())
    >>> new_changed['anna'].parent.name
    'catherine'
    >>> new_changed['anna'].object is old_objects['anna']
    True
    >>> new_changed['fred'].object is old_objects['fred']
    False
    >>> new_changed['fred'].object is app['f1']
    False
    >>> new_changed['fred'].object.source_name
    u'f1'
    >>> IFreezing(new_changed['anna'].object)._z_frozen
    True
    >>> IFreezing(new_changed['fred'].object)._z_frozen
    True

Now that we have two versions in the vault, we can introduce two
additional attributes of the inventories, contents, and items: `next` and
`previous`.  These attributes let you time travel in the vault's history.

We also look at similar attributes on the manifest, and at the vault's
`getInventory` method.

For instance, the current inventory's `previous` attribute points to the
original inventory, and vice versa.

    >>> i.previous == v.getInventory(0)
    True
    >>> i.manifest.previous is v[0]
    True
    >>> v.getInventory(0).next == i == v.inventory
    True
    >>> v[0].next is i.manifest is v.manifest
    True
    >>> i.next # None
    >>> manifest.next # None
    >>> v.getInventory(0).previous # None
    >>> v[0].previous # None

The same is true for inventory items.

    >>> list(v.inventory.contents.previous.keys())
    ['barbara', 'abe', 'donald']
    >>> list(v.getInventory(0).contents.next.keys())
    ['barbara', 'abe', 'donald', 'fred']
    >>> v.inventory.contents.previous.next == v.inventory.contents
    True
    >>> v.inventory.contents('abe')('catherine')('anna').previous.object
    <Demo u'a1'>
    >>> (v.inventory.contents('abe').relationship is
    ...  v.inventory.contents.previous('abe').relationship)
    True

Once you step to a previous or next item, further steps from the item remain
in the previous or next inventory.

    >>> v.inventory.contents('abe')('catherine')['anna'].__name__ == 'a1'
    False
    >>> v.inventory.contents.previous('abe')('catherine')['anna']
    <Demo u'a1'>

In addition, inventory items support `previous_version` and `next_version`.
The difference between these and `previous` and `next` is that the `*_version`
variants skip to the item that was different than the current item.  For
instance, while the previous_version of the 'anna' is the old 'a1' object,
just like the `previous` value, the previous_version of 'abe' is None, because
it has no previous version.

    >>> v.inventory.contents(
    ...     'abe')('catherine')('anna').previous_version.object
    <Demo u'a1'>
    >>> v.inventory.contents('abe').previous_version # None

These leverage the `getPrevious` and `getNext` methods on the vault, which work
with relationships.

The previous and next tools are even more interesting when tokens move: you
can see positions change within the hierarchy.  Inventories have a `moveTo`
method that can let the inventory follow the moves to maintain history.  We'll
create a new inventory copy and demonstrate.  As we do, notice that
inventory items obtained before the move correctly reflect the move, as
described above.

    >>> manifest = Manifest(v.manifest)
    >>> del app['inventory']
    >>> i = app['inventory'] = Inventory(manifest)
    >>> item = i.contents('abe')('catherine')
    >>> item.parent.name
    'abe'
    >>> i.contents('abe')('catherine').moveTo(i.contents('fred'))
    >>> item.parent.name
    'fred'
    >>> len(i.contents('abe').keys())
    0
    >>> list(i.contents('fred').keys())
    ['catherine']

The change actually only affects the source and target of the move.

    >>> changes = dict((getattr(item, 'name'), item)
    ...                for item in i.iterChangedItems())
    >>> len(changes)
    2
    >>> changes['fred'].values()
    [<Demo u'c1'>]
    >>> len(changes['abe'].keys())
    0

So now our hierarchy looks like this ("*" indicates a changed node)::

                               (top node)
                              /   /  \  \
                          ----   /    \  ---------
                         /      |      |          \
                'barbara'     'abe'*  'donald'     'fred'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>  <Demo u'f1'>
                                                       |
                                                       |
                                                  'catherine'
                                                  <Demo u'c1'>
                                                       |
                                                       |
                                                    'anna'
                                                  <Demo ...>

If you try to move parts of the hierarchy to someplace that has the same name,
you will receive a ValueError unless you specify a name that does not
conflict.

    >>> i.contents('abe')['donald'] = app['d2']
    >>> i.contents('donald').moveTo(i.contents('abe'))
    Traceback (most recent call last):
    ...
    ValueError: Object with same name already exists in new location
    >>> i.contents('donald').moveTo(i.contents('abe'), 'old_donald')
    >>> i.contents('abe').items()
    [('donald', <Demo u'd2'>), ('old_donald', <Demo u'd1'>)]

Now our hierarchy looks like this ("*" indicates a changed or new node)::

                             (top node)*
                              /  |   \
                          ----   |     ----
                         /       |         \
                'barbara'     'abe'*        'fred'*
            <Demo u'b1'>   <Demo u'a1'>     <Demo u'f1'>
                           /         \             |
                          /           \            |
                     'donald'*    'old_donald'  'catherine'
                   <Demo u'd2'>   <Demo u'd1'>  <Demo u'c1'>
                                                   |
                                                   |
                                                 'anna'
                                                <Demo ...>

If you try to move part of the hierarchy to someplace within itself, you will
also receive a ValueError.

    >>> i.contents('fred').moveTo(i.contents('fred')('catherine')('anna'))
    Traceback (most recent call last):
    ...
    ValueError: May not move item to within itself

It is for this reason that the contents does not support the moveTo operation.

    >>> hasattr(i.contents, 'moveTo')
    False

If you move an object to the same folder it is a silent noop, unless you are
using the move as a rename operation and the new name conflicts.

    >>> i.contents('abe')('old_donald').moveTo(i.contents('abe'))
    >>> i.contents('abe').items()
    [('donald', <Demo u'd2'>), ('old_donald', <Demo u'd1'>)]
    >>> i.contents('abe')('old_donald').moveTo(i.contents('abe'), 'donald')
    Traceback (most recent call last):
    ...
    ValueError: Object with same name already exists in new location
    >>> i.contents('abe').items()
    [('donald', <Demo u'd2'>), ('old_donald', <Demo u'd1'>)]
    >>> i.contents('abe')('donald').moveTo(i.contents('abe'),
    ...                                    'new_donald')
    >>> i.contents('abe').items()
    [('old_donald', <Demo u'd1'>), ('new_donald', <Demo u'd2'>)]

Notice in the last part of the example above that the move within the folder
also changed the order.

It's also interesting to note that, with all these changes, we only have two
additional changed items: the addition of new_donald, and the changed
containment of the contents.  old_donald, for instance, is not considered to
be changed; only its containers were.

    >>> changes = dict((getattr(item, 'name', None), item)
    ...                for item in i.iterChangedItems())
    >>> len(changes)
    4
    >>> changes['fred'].items()
    [('catherine', <Demo u'c1'>)]
    >>> changes['abe'].items()
    [('old_donald', <Demo u'd1'>), ('new_donald', <Demo u'd2'>)]
    >>> changes['new_donald'].object
    <Demo u'd2'>
    >>> list(changes[None].keys())
    ['barbara', 'abe', 'fred']

Now that we have moved some objects that existed in previous inventories--
catherine (containing anna) was moved from abe to fred, and donald was moved
from the root contents to abe and renamed to 'old_donald'--we can examine
the previous and previous_version pointers.

    >>> i.contents('abe')('old_donald').previous.parent == i.previous.contents
    True
    >>> i.contents('abe')('old_donald').previous_version # None

The previous_version is None because, as seen in the iterChangedItems example,
donald didn't actually change--only its containers did.  previous_version does
work for both local changes and changes in earlier inventories, though.

    >>> list(i.contents('abe').keys())
    ['old_donald', 'new_donald']
    >>> list(i.contents('abe').previous.keys())
    ['catherine']
    >>> (i.contents('fred')('catherine')('anna').previous.inventory ==
    ...  v.inventory)
    True
    >>> (i.contents('fred')('catherine')('anna').previous_version.inventory ==
    ...  v.getInventory(0))
    True

The previous_version of anna is the first one that was committed in the
initial inventory--it didn't change in this version, but in the most recently
committed inventory, so the previous version is the very first one committed.

By the way, notice that, while previous and previous_version point to the
inventories from which the given item came, the historical, versioned
inventories in the vault don't point to this working inventory in next or
next_version because this inventory has not been committed yet.

    >>> v.inventory.contents('abe').next # None
    >>> v.inventory.contents('abe').next_version # None

As mentioned above, only inventory items support `moveTo`, not the top-node
inventory contents.  Both contents and inventory items support a `copyTo`
method.  This is similar to moveTo but it creates new additional locations in
the inventory for the same objects; the new locations don't maintain any
history.  It is largely a short hand for doing "location1['foo'] =
location2['foo']" for all objects in a part of the inventory.  The only
difference is when copying between inventories, as we will see below.

The basic `copyTo` machinery is very similar to `moveTo`.  We'll first copy
catherine and anna to within the contents.

    >>> i.contents('fred')('catherine').copyTo(i.contents)
    >>> list(i.contents.keys())
    ['barbara', 'abe', 'fred', 'catherine']
    >>> list(i.contents('catherine').keys())
    ['anna']
    >>> i.contents['catherine'] is i.contents('fred')['catherine']
    True
    >>> (i.contents('catherine')('anna').object is
    ...  i.contents('fred')('catherine')('anna').object)
    True

Now our hierarchy looks like this ("*" indicates a changed or new node)::

                                (top node)*
                       --------/  /   \   \-----------
                      /          /     \              \
                     /          /       \              \
            'barbara'      'abe'*        'fred'*        'catherine'*
        <Demo u'b1'>   <Demo u'a1'>     <Demo u'f1'>   <Demo u'c1'>
                       /         \             |             |
                      /           \            |             |
              'new_donald'*   'old_donald'  'catherine'    'anna'*
               <Demo u'd2'>   <Demo u'd1'>  <Demo u'c1'>   <Demo ...>
                                               |
                                               |
                                             'anna'
                                            <Demo ...>

Now we have copied objects from one location to another.  The copies are unlike
the originals because they do not have any history.

    >>> i.contents('fred')('catherine')('anna').previous is None
    False
    >>> i.contents('catherine')('anna').previous is None
    True

However, they do know their copy source.

    >>> (i.contents('catherine')('anna').copy_source ==
    ...  i.contents('fred')('catherine')('anna'))
    True

As with `moveTo`, you may not override a name, but you may explicitly provide
one.

    >>> i.contents['anna'] = Demo()
    >>> i.contents('catherine')('anna').copyTo(i.contents)
    Traceback (most recent call last):
    ...
    ValueError: Object with same name already exists in new location
    >>> i.contents('catherine')('anna').copyTo(i.contents, 'old_anna')
    >>> list(i.contents.keys())
    ['barbara', 'abe', 'fred', 'catherine', 'anna', 'old_anna']
    >>> del i.contents['anna']
    >>> del i.contents['old_anna']

Unlike with `moveTo`, if you try to copy a part of the hierarchy on top of
itself (same location, same name), the inventory will raise an error.

    >>> i.contents('catherine')('anna').copyTo(i.contents('catherine'))
    Traceback (most recent call last):
    ...
    ValueError: Object with same name already exists in new location

You can actually copyTo a location in a completely different inventory, even
from a separate vault.

    >>> another = app['another'] = Vault()
    >>> another_i = app['another_i'] = Inventory(vault=another)
    >>> len(another_i.contents)
    0
    >>> i.contents('abe').copyTo(another_i.contents)
    >>> another_i.contents['abe']
    <Demo u'a1'>
    >>> another_i.contents('abe')['new_donald']
    <Demo u'd2'>
    >>> another_i.contents('abe')['old_donald']
    <Demo u'd1'>

We haven't committed for awhile, so let's commit this third revision.  We did
a lot of deletes, so let's just accept all of the orphan conflicts.

    >>> for item in i.iterOrphanConflicts():
    ...     item.resolveOrphanConflict()
    ...
    >>> v.commit(i)
    >>> checkManifest(v.manifest)

In a future revision of the zc.vault package, it may be possible to move and
copy between inventories. At the time of writing, this use case is
unnecessary, and doing so will have unspecified behavior.

.. topic:: A test for a subtle bug in revision <= 78553

    One important case, at least for the regression testing is an
    attempt to rename an item after the vault has been frozen.
    Since we have just committed, this is the right time to try that.
    Let's create a local copy of an inventory and try to rename some
    items on it.

    >>> v.manifest._z_frozen
    True
    >>> l = Inventory(Manifest(v.manifest))
    >>> l.manifest._z_frozen
    False
    >>> l.contents('abe').items()
    [('old_donald', <Demo u'd1'>), ('new_donald', <Demo u'Demo-2'>)]
    >>> l.contents('abe')('old_donald').moveTo(l.contents('abe'), 'bob')
    >>> l.contents('abe')('new_donald').moveTo(l.contents('abe'), 'donald')
    >>> l.contents('abe').items()
    [('bob', <Demo u'd1'>), ('donald', <Demo u'Demo-2'>)]


We have now discussed the core API for the vault system for basic use.  A
number of other use cases are important, however:

- revert to an older inventory;

- merge concurrent changes;

- track an object in a vault; and

- traverse through a vault using URL or TALES paths.

Reverting to an older inventory is fairly simple: use the 'commitFrom'
method to copy and commit an older version into a new copy.  The same
works with manifests.

    >>> v.commitFrom(v[0])

The data is now as it was in the old version.

    >>> list(v.inventory.contents.keys())
    ['barbara', 'abe', 'donald']

Now our hierarchy looks like this again::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'   'abe'    'donald'
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

The `commitFrom` method will take any committed manifest from a vault that
shares the same intids utility.  It creates a new manifest that duplicates the
provided one.

    >>> v.inventory.contents('abe')('catherine').previous.parent.name
    'fred'
    >>> v.manifest.previous is v[-2]
    True
    >>> v.manifest.base_source is v[-2]
    True
    >>> v.manifest.base_source is v[0]
    False
    >>> v[-2].base_source is v[-3]
    True

Note that this approach will cause an error:

    >>> v.commit(Manifest(v[0])) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OutOfDateError: <zc.vault.core.Manifest object at ...>

Again, use `commitFrom` to revert.

Now we come to the most complex vault use case: concurrent changes to a vault,
merging inventories.  The vault design supports a number of features for these
sorts of use cases.

The basic merge story is that if one or more commits happen to a vault while
an inventory from the vault is being worked on, so that the base of a working
inventory is no longer the most recent committed inventory, and thus cannot
be committed normally...

    >>> long_running = Inventory(Manifest(v.manifest))
    >>> short_running = Inventory(Manifest(v.manifest))
    >>> long_running.manifest.base_source is v.manifest
    True
    >>> short_running.contents['donald'] = app['d2']
    >>> short_running.contents.items()
    [('barbara', <Demo u'b1'>), ('abe', <Demo u'a1'>), ('donald', <Demo u'd2'>)]
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> short_running = Inventory(Manifest(v.manifest))
    >>> short_running.contents('barbara')['fred'] = app['f1']
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> long_running.manifest.base_source is v.manifest
    False
    >>> long_running.manifest.base_source is v.manifest.previous.previous
    True
    >>> long_running.contents['edna'] = app['e1']
    >>> long_running.contents.items() # doctest: +NORMALIZE_WHITESPACE
    [('barbara', <Demo u'b1'>), ('abe', <Demo u'a1'>),
     ('donald', <Demo u'd1'>), ('edna', <Demo u'e1'>)]
    >>> v.commit(long_running) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OutOfDateError: <zc.vault.core.Manifest object at ...>

...then the inventory can be updated; and, if there are no problems with the
update, then the inventory can be committed.

short_running, and the head of the vault, looks like this now ("*" indicates a
change from the previous version)::

                         (top node)
                         /    |    \
                        /     |     \
                'barbara'*  'abe'    'donald'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd2'>
                |             |
                |             |
             'fred'*      'catherine'
          <Demo u'f1'>    <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

long_running looks like this::

                                (top node)*
                         ------/  /   \  \----------
                        /        /     \            \
                'barbara'   'abe'    'donald'       'edna'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd1'>  <Demo u'e1'>
                              |
                              |
                         'catherine'
                         <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

The contents node changed and 'edna' was added.

By default, an update is to the current inventory of the inventory base's vault.

Here's the update.  It will produce no conflicts, because the node changes do
not overlap (review diagrams above).

    >>> long_running.beginUpdate()
    >>> long_running.updating
    True

Post-merge, long_running looks like this ('M' indicates a merged node)::

                                (top node)*
                         ------/  /   \  \----------
                        /        /     \            \
               'barbara'M   'abe'    'donald'M      'edna'*
            <Demo u'b1'> <Demo u'a1'> <Demo u'd2'>  <Demo u'e1'>
                 |            |
                 |            |
              'fred'M    'catherine'
           <Demo u'f1'>  <Demo u'c1'>
                              |
                              |
                           'anna'
                         <Demo u'a1'>

(ADVANCED)

During an update, the local relationships may not be changed, even though they
are not versioned.

    >>> long_running.contents('edna').type
    'local'
    >>> long_running.contents('edna').relationship.object = Demo()
    Traceback (most recent call last):
    ...
    UpdateError: cannot change local relationships while updating
    >>> long_running.contents('edna').relationship.object
    <Demo u'e1'>
    >>> long_running.contents('edna').relationship._z_frozen
    False
    >>> long_running.manifest.getType(long_running.contents.relationship)
    'local'
    >>> long_running.contents.relationship.containment.updateOrder(
    ...     ('abe', 'barbara', 'edna', 'donald'))
    Traceback (most recent call last):
    ...
    UpdateError: cannot change local relationships while updating
    >>> long_running.contents.relationship.containment.keys()
    ('barbara', 'abe', 'donald', 'edna')

When you change an item or contents, this is hidden by switching to a MODIFIED
relationship, as seen below.

(end ADVANCED)

Now that we have updated, our `update_source` on the inventory shows the
inventory used to do the update.

    >>> long_running.manifest.base_source is v[-3]
    True
    >>> long_running.manifest.update_source is short_running.manifest
    True

What changes should the update reflect?  iterChangedItems takes an optional
argument which can use an alternate base to calculate changes, so we can use
that with the long_running.base to see the effective merges.

    >>> changed = dict((getattr(item, 'name', None), item) for item in
    ...                short_running.iterChangedItems(
    ...                     long_running.manifest.base_source))
    >>> changed['donald'].object.source_name
    u'd2'
    >>> changed['fred'].object.source_name
    u'f1'
    >>> list(changed['barbara'].keys())
    ['fred']

Our contents show these merged results.

    >>> list(long_running.contents.keys())
    ['barbara', 'abe', 'donald', 'edna']
    >>> long_running.contents['donald'].source_name
    u'd2'
    >>> long_running.contents('barbara')['fred'].source_name
    u'f1'

You cannot update to another inventory until you `abortUpdate` or
`completeUpdate`, as we discuss far below.

    >>> long_running.beginUpdate(v[-2])
    Traceback (most recent call last):
    ...
    UpdateError: cannot begin another update while updating

We'll show `abortUpdate`, then redo the update.  A characteristic of
abortUpdate is that it should revert all changes you made while updating.  For
instance, we'll select another version of the contents and even add an item.
The changes will all go away when we abort.

    >>> len(list(long_running.iterChangedItems()))
    5
    >>> long_running.contents['fred'] = app['f1']
    >>> list(long_running.contents.keys())
    ['barbara', 'abe', 'donald', 'edna', 'fred']
    >>> len(list(long_running.iterChangedItems()))
    6
    >>> long_running.abortUpdate()
    >>> long_running.manifest.update_source # None
    >>> long_running.contents.items() # doctest: +NORMALIZE_WHITESPACE
    [('barbara', <Demo u'b1'>), ('abe', <Demo u'a1'>),
     ('donald', <Demo u'd1'>), ('edna', <Demo u'e1'>)]
    >>> len(list(long_running.iterChangedItems()))
    2
    >>> long_running.beginUpdate()
    >>> list(long_running.contents.keys())
    ['barbara', 'abe', 'donald', 'edna']
    >>> long_running.contents['donald'].source_name
    u'd2'
    >>> long_running.contents('barbara')['fred'].source_name
    u'f1'

Now we'll look around more at the state of things.  We can use
iterChangedItems to get a list of all changed and updated.  As already seen in
the examples, `update_source` on the inventory shows the inventory used to do
the update.

    >>> updated = {}
    >>> changed = {}
    >>> for item in long_running.iterChangedItems():
    ...     name = getattr(item, 'name', None)
    ...     if item.type == interfaces.LOCAL:
    ...         changed[name] = item
    ...     else:
    ...         assert item.type == interfaces.UPDATED
    ...         updated[name] = item
    ...
    >>> len(updated)
    3
    >>> updated['donald'].object.source_name
    u'd2'
    >>> updated['fred'].object.source_name
    u'f1'
    >>> list(updated['barbara'].keys())
    ['fred']
    >>> len(changed)
    2
    >>> list(changed[None].keys())
    ['barbara', 'abe', 'donald', 'edna']
    >>> changed['edna'].object
    <Demo u'e1'>

The `has_updated` and `updated_item` attributes, which only come into effect
when an inventory is in the middle of an update, let you examine the changes
from a more local perspective.

    >>> long_running.contents('donald').has_local
    False
    >>> long_running.contents('donald').has_updated
    True
    >>> (long_running.contents('donald').updated_item.relationship is
    ...  long_running.contents('donald').relationship)
    True

There are three kinds of problems that can prevent a post-merge commit: item
conflicts, orphans, and parent conflicts.  Item conflicts are item updates
that conflicted with local changes and that the system could not merge (more
on that below). Orphans are accepted item changes (local or updated) that are
not accessible from the top contents, and so will be lost.  Parent conflicts
are items that were moved to one location in the source and another location
in the local changes, and so now have two parents: an illegal state because it
makes future merges and sane historical analysis difficult.

These three kinds of problem can be analyzed with
`iterUpdateConflicts`, `iterOrphanConflicts`, and `iterParentConflicts`,
respectively.  We have already seen iterOrphanConflicts.  In our current merge,
we have none of these problems, and we can commit (or completeUpdate)
successfully.

    >>> list(long_running.iterUpdateConflicts())
    []
    >>> list(long_running.iterOrphanConflicts())
    []
    >>> list(long_running.iterParentConflicts())
    []
    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

We had a lot of discussion between the most important points here, so to
review, all we had to do in the simple case was this::

    long_running.beginUpdate()
    v.commit(long_running)

We could have rejected some of the updates and local changes, which might
have made things more interesting; and the two steps let you analyze the update
changes to tweak things as desired.  But the simplest case allows a simple
spelling.

Now let's explore the possible merging problems.  The first, and arguably most
complex, is item conflict.  An item conflict is easy to provoke.  We can do it
by manipulating the containment or the object of an item.  Here we'll
manipulate the containment order of the root.

    >>> list(v.inventory.contents.keys())
    ['barbara', 'abe', 'donald', 'edna']
    >>> short_running = Inventory(Manifest(v.manifest))
    >>> long_running = Inventory(Manifest(v.manifest))
    >>> short_running.contents.updateOrder(
    ...     ('abe', 'barbara', 'edna', 'donald'))
    >>> long_running.contents.updateOrder(
    ...     ('abe', 'barbara', 'donald', 'edna'))
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> long_running.beginUpdate()
    >>> v.commit(long_running)
    Traceback (most recent call last):
    ...
    UpdateError: cannot complete update with conflicts
    >>> conflicts = list(long_running.iterUpdateConflicts())
    >>> len(conflicts)
    1
    >>> conflict = conflicts[0]
    >>> conflict.type
    'local'
    >>> list(conflict.keys())
    ['abe', 'barbara', 'donald', 'edna']
    >>> conflict.is_update_conflict
    True
    >>> conflict.selected
    True
    >>> conflict.has_updated
    True
    >>> list(conflict.updated_item.keys())
    ['abe', 'barbara', 'edna', 'donald']

As you can see, we have the tools to find out the conflicts and examine them.
To resolve this conflict, we merely need to use the `resolveUpdateConflict`
method.  We can select the desired one we want, or even create a new one and
modify it, before or after marking it resolved.

Let's create a new one.  All you have to do is start changing the item, and a
new one is created.  You are not allowed to directly modify local changes when
you are updating, so that the system can revert to them; but you may create
'modified' versions (that will be discarded if the update is aborted).

    >>> len(list(conflict.iterModifiedItems()))
    0
    >>> conflict.has_modified
    False
    >>> conflict.selected
    True
    >>> conflict.type
    'local'
    >>> list(conflict.keys())
    ['abe', 'barbara', 'donald', 'edna']
    >>> conflict.updateOrder(['abe', 'donald', 'barbara', 'edna'])
    >>> len(list(conflict.iterModifiedItems()))
    1
    >>> conflict.has_modified
    True
    >>> conflict.selected
    True
    >>> conflict.type
    'modified'
    >>> conflict.copy_source.type
    'local'
    >>> conflict.copy_source == conflict.local_item
    True
    >>> conflict == list(conflict.iterModifiedItems())[0]
    True
    >>> list(conflict.local_item.keys())
    ['abe', 'barbara', 'donald', 'edna']
    >>> list(conflict.keys())
    ['abe', 'donald', 'barbara', 'edna']
    >>> list(conflict.updated_item.keys())
    ['abe', 'barbara', 'edna', 'donald']

Now we're going to resolve it.

    >>> conflict.resolveUpdateConflict()
    >>> conflict.is_update_conflict
    False
    >>> len(list(long_running.iterUpdateConflicts()))
    0
    >>> resolved = list(long_running.iterUpdateResolutions())
    >>> len(resolved)
    1
    >>> resolved[0] == conflict
    True

Now if we called abortUpdate, the local_item would look the way it did before
the update, because we modified a separate object.  Let's commit, though.

    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

Our hierarchy looks like this now::

                                (top node)*
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'M      'barbara'M   'edna'*
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                 |                          |
                 |                          |
            'catherine'                 'fred'M
           <Demo u'c1'>                 <Demo u'f1'>
                 |
                 |
               'anna'
            <Demo u'a1'>

The vault code allows for adapters to try and suggest merges.  For instance, a
simple merge might have a policy that one version with an object change and
another version with a containment change can be merged simply.  This uses
some APIs we haven't talked about yet: if there is a core.txt in this
directory, you're in luck; otherwise, hope for help in interfaces.py and
bother Gary for docs (sorry).

    >>> from zc.vault.core import Relationship
    >>> @component.adapter(interfaces.IVault)
    ... @interface.implementer(interfaces.IConflictResolver)
    ... def factory(vault):
    ...     def resolver(manifest, local, updated, base):
    ...         if local.object is not base.object:
    ...             if updated.object is base.object:
    ...                 object = local.object
    ...             else:
    ...                 return
    ...         else:
    ...             object = updated.object
    ...         if local.containment != base.containment:
    ...             if updated.containment != base.containment:
    ...                 return
    ...             else:
    ...                 containment = local.containment
    ...         else:
    ...             containment = updated.containment
    ...         suggested = Relationship(local.token, object, containment)
    ...         manifest.addSuggested(suggested)
    ...         manifest.select(suggested)
    ...         manifest.resolveUpdateConflict(local.token)
    ...     return resolver
    ...
    >>> component.provideAdapter(factory)

Now if we merge changes that this policy can handle, we'll have smooth updates.

    >>> short_running = Inventory(Manifest(v.manifest))
    >>> long_running = Inventory(Manifest(v.manifest))
    >>> app['c2'] = Demo()
    >>> short_running.contents('abe')['catherine'] = app['c2']
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> long_running.contents('abe')('catherine')['fred'] = app['f1']
    >>> long_running.beginUpdate()
    >>> cath = long_running.contents('abe')('catherine')
    >>> cath.has_suggested
    True
    >>> cath.type
    'suggested'
    >>> cath.has_updated
    True
    >>> cath.selected
    True
    >>> cath.has_local
    True
    >>> suggestedItems = list(cath.iterSuggestedItems())
    >>> len(suggestedItems)
    1
    >>> suggestedItems[0] == cath
    True
    >>> cath.object.source_name
    u'c2'
    >>> list(cath.keys())
    ['anna', 'fred']
    >>> cath.local_item.object
    <Demo u'c1'>
    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

This means we automatically merged this... ::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                 |                          |
                 |                          |
            'catherine'*                 'fred'
           <Demo u'c2'>                 <Demo u'f1'>
                 |
                 |
               'anna'
            <Demo u'a1'>

...with this (that would normally produce a conflict with the 'catherine'
node)... ::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                 |                          |
                 |                          |
            'catherine'*                'fred'
           <Demo u'c1'>                 <Demo u'f1'>
            /        \
           /          \
        'anna'        'fred'*
     <Demo u'a1'>    <Demo u'f1'>

...to produce this::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                 |                          |
                 |                          |
            'catherine'*                'fred'
           <Demo u'c2'>                 <Demo u'f1'>
            /        \
           /          \
        'anna'        'fred'*
     <Demo u'a1'>    <Demo u'f1'>

This concludes our tour of item conflicts.  We are left with orphans and
parent conflicts.

As mentioned above, orphans are accepted, changed items, typically from the
update or local changes, that are inaccessible from the root of the inventory.
For example, consider the following.

    >>> short_running = Inventory(Manifest(v.manifest))
    >>> long_running = Inventory(Manifest(v.manifest))
    >>> list(short_running.contents('abe').keys())
    ['catherine']
    >>> list(short_running.contents('abe')('catherine').keys())
    ['anna', 'fred']
    >>> del short_running.contents('abe')['catherine']
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> long_running.contents('abe')('catherine')['anna'] = Demo()
    >>> long_running.beginUpdate()
    >>> v.commit(long_running)
    Traceback (most recent call last):
    ...
    UpdateError: cannot complete update with conflicts
    >>> orphans =list(long_running.iterOrphanConflicts())
    >>> len(orphans)
    1
    >>> orphan = orphans[0]
    >>> orphan.parent.name
    'catherine'
    >>> orphan.selected
    True
    >>> orphan.type
    'local'
    >>> orphan.parent.selected
    True
    >>> orphan.parent.type
    'base'
    >>> orphan.parent.parent.type
    'base'
    >>> orphan.parent.parent.selected
    False
    >>> orphan.parent.parent.selected_item.type
    'updated'

To reiterate in a diagram, the short_running inventory deleted the
'catherine' branch::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                                            |
                                            |
                                         'fred'
                                      <Demo u'f1'>

However, the long running branch made a change to an object that had
been removed ('anna')::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                 |                          |
                 |                          |
            'catherine'                 'fred'
           <Demo u'c2'>                 <Demo u'f1'>
            /        \
           /          \
        'anna'*       'fred'
     <Demo ...>     <Demo u'f1'>

So, given the orphan, you can discover the old version of the node that let the
change occur, and thus the change that hid the orphan.

To resolve an orphan, as seen before, you can `resolveOrphanConflict`, or
somehow change the tree so that the orphan is within the tree again (using
`moveTo`).  We'll just resolve it.  Note that resolving keeps it selected: it
just stops the complaining.

    >>> orphan.selected
    True
    >>> orphan.resolveOrphanConflict()
    >>> orphan.selected
    True
    >>> len(list(long_running.iterOrphanConflicts()))
    0
    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

The same happens if the change occurs because of a reversal--the long_running
inventory performs the delete.

It also can happen if the user explicitly selects a choice that eliminates an
accepted change, even outside of a merge, as we have seen above.

Parent conflicts are the last sort of conflict.

Our hierarchy now looks like this::

                                (top node)
                     ----------/  /   \  \----------
                    /            /     \            \
               'abe'     'donald'       'barbara'    'edna'
            <Demo u'a1'> <Demo u'd2'>  <Demo u'b1'> <Demo u'e1'>
                                            |
                                            |
                                         'fred'
                                      <Demo u'f1'>

The short_running version will be changed to look like this::

                           (top node)
                     ------/   |    \-------
                    /          |            \
               'abe'        'barbara'*      'edna'
            <Demo u'a1'>   <Demo u'b1'>  <Demo u'e1'>
                            /      \
                           /        \
                        'fred'     'donald'
                   <Demo u'f1'>   <Demo u'd2'>

The long_running version will look like this. ::

                           (top node)
                     ------/   |    \-------
                    /          |            \
               'abe'        'barbara'      'edna'
            <Demo u'a1'>   <Demo u'b1'>  <Demo u'e1'>
                               |
                               |
                             'fred'*
                           <Demo u'f1'>
                               |
                               |
                            'donald'
                          <Demo u'd2'>

Post-merge the tree looks like this::

                           (top node)
                     ------/   |    \-------
                    /          |            \
               'abe'        'barbara'*      'edna'
            <Demo u'a1'>   <Demo u'b1'>  <Demo u'e1'>
                            /      \
                           /        \
                        'fred'*    'donald'
                   <Demo u'f1'>   <Demo u'd2'>
                        |
                        |
                     'donald'
                   <Demo u'd2'>

The problem is Donald.  It is one token in two or more places: a parent
conflict.

    >>> short_running = Inventory(Manifest(v.manifest))
    >>> long_running = Inventory(Manifest(v.manifest))
    >>> short_running.contents('donald').moveTo(
    ...     short_running.contents('barbara'))
    >>> v.commit(short_running)
    >>> checkManifest(v.manifest)
    >>> long_running.contents('donald').moveTo(
    ...     long_running.contents('barbara')('fred'))
    >>> long_running.beginUpdate()
    >>> conflicts = list(long_running.iterParentConflicts())
    >>> v.commit(long_running)
    Traceback (most recent call last):
    ...
    UpdateError: cannot complete update with conflicts
    >>> conflicts = list(long_running.iterParentConflicts())
    >>> len(conflicts)
    1
    >>> conflict = conflicts[0]
    >>> conflict.name
    Traceback (most recent call last):
    ...
    ParentConflictError
    >>> conflict.parent
    Traceback (most recent call last):
    ...
    ParentConflictError
    >>> selected = list(conflict.iterSelectedParents())
    >>> len(selected)
    2
    >>> sorted((s.type, s.name) for s in selected)
    [('local', 'fred'), ('updated', 'barbara')]
    >>> all = dict((s.type, s) for s in conflict.iterParents())
    >>> len(all)
    3
    >>> sorted(all)
    ['base', 'local', 'updated']

You can provoke these just by accepting a previous version, outside of merges.
For instance, we can now make a three-way parent conflict by selecting the
root node.

    >>> all['base'].select()
    >>> selected = list(conflict.iterSelectedParents())
    >>> len(selected)
    3

Now if we resolve the original problem by rejecting the local change,
we'll still have a problem, because of accepting the baseParent.

    >>> all['local'].base_item.select()
    >>> selected = list(conflict.iterSelectedParents())
    >>> len(selected)
    2
    >>> v.commit(long_running)
    Traceback (most recent call last):
    ...
    UpdateError: cannot complete update with conflicts
    >>> all['base'].local_item.select()
    >>> len(list(long_running.iterParentConflicts()))
    0

Now our hierarchy looks like short_running again::

                           (top node)
                     ------/   |    \-------
                    /          |            \
               'abe'        'barbara'      'edna'
            <Demo u'a1'>   <Demo u'b1'>  <Demo u'e1'>
                            /      \
                           /        \
                        'fred'     'donald'
                   <Demo u'f1'>   <Demo u'd2'>

We can't check this in because there are no effective changes between this
and the last checkin.

    >>> v.commit(long_running) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    NoChangesError: <zc.vault.core.Manifest object at ...>

So actually, we'll reinstate the local change, reject the short_running
change (the placement within barbara), and commit.

    >>> all['local'].select()
    >>> all['updated'].base_item.select()
    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

Note that even though we selected the base_item, the relationship generated by
completing the update is actually local because it is a change from the
previous updated source.

    >>> v.inventory.contents('barbara').type
    'local'

There is actually a fourth kind of error: having child nodes in selected
relationships for which there are no selected relationships.  The code tries to
disallow this, so it should not be encountered.

Next, we will talk about using vaults to create and manage branches.
The simple basics of this are that you can commit an inventory based on one
vault into a fresh vault, and you can then update across the two vaults.  To
create a vault that can have merged manifests, you must share the internal
'intids' attribute.  The `createBranch` method is sugar for doing that and then
(by default) committing the most recent manifest of the current vault as the first
revision of the branch.

    >>> branch = app['branch'] = v.createBranch()
    >>> bi = Inventory(Manifest(branch.manifest))
    >>> branch_start_inventory = v.inventory
    >>> bi.contents['george'] = Demo()
    >>> branch.commit(bi)
    >>> checkManifest(branch.manifest)
    >>> i = Inventory(Manifest(v.manifest))
    >>> i.contents['barbara'] = app['b2'] = Demo()
    >>> v.commit(i)
    >>> checkManifest(v.manifest)
    >>> i.contents['barbara'].source_name
    u'b2'
    >>> bi = Inventory(Manifest(branch.manifest))
    >>> bi.contents('barbara')['henry'] = app['h1'] = Demo()
    >>> branch.commit(bi)
    >>> checkManifest(branch.manifest)

Now we want to merge the mainline changes with the branch.

    >>> bi = Inventory(Manifest(branch.manifest))
    >>> (bi.manifest.base_source is bi.manifest.getBaseSource(branch) is
    ...  branch.manifest)
    True
    >>> (bi.manifest.getBaseSource(v) is branch_start_inventory.manifest is
    ...  v[-2])
    True
    >>> bi.beginUpdate(v.inventory)
    >>> bi.contents['barbara'].source_name
    u'b2'
    >>> bi.contents('barbara')['henry'].source_name
    u'h1'

A smooth update.  But what happens if meanwhile someone changes the branch,
before this is committed?  We use `completeUpdate`, and then update again on
the branch.  `completeUpdate` moves all selected changes to be `local`,
whatever the source, the same way commit does (in fact, commit uses
completeUpdate).

    >>> bi2 = Inventory(Manifest(branch.manifest))
    >>> bi2.contents['edna'] = app['e2'] = Demo()
    >>> branch.commit(bi2)
    >>> checkManifest(branch.manifest)
    >>> branch.commit(bi) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OutOfDateError: <zc.vault.core.Manifest object at ...>
    >>> bi.completeUpdate()
    >>> bi.beginUpdate()
    >>> branch.commit(bi)
    >>> checkManifest(branch.manifest)

Once we have done this, the head of the branch is based on the head of the
original vault, so we can immediately check in a branch inventory in the
trunk inventory.

    >>> v.commit(Inventory(Manifest(branch.manifest)))
    >>> checkManifest(v.manifest)

Finally, cherry-picking changes is possible as well, though it can
cause normal updates to be confused.  `beginCollectionUpdate` takes an
iterable of items (such as is produced by iterChangedItems) and applies
the update with the usual conflict and examination approaches we've
seen above.  `completeUpdate` can then accept the changes for
additional updates.

    >>> long_running = Inventory(Manifest(v.manifest))
    >>> discarded = Inventory(Manifest(v.manifest))
    >>> discarded.contents['ignatius'] = app['i1'] = Demo()
    >>> discarded.contents['jacobus'] = app['j1'] = Demo()
    >>> long_running.beginCollectionUpdate((discarded.contents('ignatius'),))
    >>> len(list(long_running.iterOrphanConflicts()))
    1
    >>> o = iter(long_running.iterOrphanConflicts()).next()
    >>> o.selected
    True
    >>> o.name # None
    >>> o.parent # None
    >>> o.object
    <Demo u'i1'>
    >>> o.moveTo(long_running.contents, 'ignatius')
    >>> len(list(long_running.iterOrphanConflicts()))
    0
    >>> long_running.contents['ignatius']
    <Demo u'i1'>
    >>> long_running.contents('ignatius')['jacobus'] = app['j1']
    >>> list(long_running.contents('ignatius').keys())
    ['jacobus']
    >>> long_running.contents('ignatius')('jacobus').selected
    True
    >>> list(discarded.contents('ignatius').keys())
    []
    >>> v.commit(long_running)
    >>> checkManifest(v.manifest)

The code will stop you if you try to add a set of relationships that result in
the manifest having keys that don't map to values--or more precisely, child
tokens that don't have matching selected relationships.  For instance, consider
this.

    >>> long_running = Inventory(Manifest(v.manifest))
    >>> discarded = Inventory(Manifest(v.manifest))
    >>> discarded.contents['katrina'] = app['k1'] = Demo()
    >>> discarded.contents('katrina')['loyola'] = app['l1'] = Demo()
    >>> long_running.beginCollectionUpdate((discarded.contents('katrina'),))
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: cannot update from a set that includes children tokens...

It is disallowed because the katrina node includes the 'loyola' node, but we
didn't include the matching 'loyola' item.

If you include both, the merge will proceed as usual.

    >>> long_running.beginCollectionUpdate(
    ...     (discarded.contents('katrina'),
    ...      discarded.contents('katrina')('loyola')))
    >>> long_running.updating
    True
    >>> len(list((long_running.iterOrphanConflicts())))
    2
    >>> orphans = dict((o.name, o) for o in long_running.iterOrphanConflicts())
    >>> orphans[None].moveTo(long_running.contents, 'katrina')
    >>> long_running.contents['katrina']
    <Demo u'k1'>
    >>> long_running.contents('katrina')['loyola']
    <Demo u'l1'>

The combination of `beginCollectionUpdate` and `iterChangedItems` can provide
a powerful way to apply arbitrary changesets to a revision.

Storing None
============

Sometimes you want to just make an empty node for organizational purposes.
While normally stored objects must be versionable and adaptable to
IKeyReference, None is a special case.  We can store None in any node.  Let's
make a quick example.

    >>> v = app['v'] = Vault()
    >>> i = Inventory(vault=v)
    >>> i.contents['foo'] = None
    >>> i.contents('foo')['bar'] = None
    >>> i.contents('foo')('bar')['baz'] = app['d1']
    >>> i.contents['foo'] # None
    >>> i.contents('foo')['bar'] # None
    >>> i.contents('foo')('bar')['baz'] is app['d1']
    True
    >>> i.contents['bing'] = app['a1']
    >>> i.contents['bing'] is app['a1']
    True
    >>> v.commit(i)
    >>> i = Inventory(vault=v, mutable=True)
    >>> i.contents['bing'] = None
    >>> del i.contents('foo')['bar']
    >>> i.contents['foo'] = app['d1']
    >>> v.commit(i)
    >>> v.inventory.contents.previous['bing'] is app['a1']
    True
    >>> v.inventory.contents.previous['foo'] is None
    True

Special "held" Containers
=========================

It is sometimes useful to specify a "held" container for all objects stored
in a vault, overriding the "held" containers for each manifest as described
above.  Vaults can be instantiated with specifying a held container.

    >>> from zc.vault.core import HeldContainer
    >>> held = app['held'] = HeldContainer()
    >>> v = app['vault_held'] = Vault(held=held)
    >>> i = Inventory(vault=v)
    >>> o = i.contents['foo'] = Demo()
    >>> o.__parent__ is held
    True
    >>> held[o.__name__] is o
    True

If you create a branch, by default it will use the same held container.

    >>> v.commit(i)
    >>> v2 = app['vault_held2'] = v.createBranch()
    >>> i2 = Inventory(vault=v2, mutable=True)
    >>> o2 = i2.contents['bar'] = Demo()
    >>> o2.__parent__ is held
    True
    >>> held[o2.__name__] is o2
    True

You can also specify another held container when you create a branch.

    >>> another_held = app['another_held'] = HeldContainer()
    >>> v3 = app['vault_held3'] = v.createBranch(held=another_held)
    >>> i3 = Inventory(vault=v3, mutable=True)
    >>> o3 = i3.contents['baz'] = Demo()
    >>> o3.__parent__ is another_held
    True
    >>> another_held[o3.__name__] is o3
    True

Committing the transaction
==========================

We'll make sure that all these changes can in fact be committed to the ZODB.

    >>> import transaction
    >>> transaction.commit()

-----------

.. Other topics.

    ...commit messages?  Could be added to event, so object log could use.

    Need commit datetime stamp, users.  Handled now by objectlog.

    Show traversal adapters that use zc.shortcut code...

    Talk about tokens.

    Then talk about use case of having a reference be updated to a given object
    within a vault...

    ...a vault mirror that also keeps track of hierarchy?

    A special reference that knows both vault and token?
