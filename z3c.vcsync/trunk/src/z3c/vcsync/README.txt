Version Control Synchronization
===============================

This package contains code that helps with handling synchronization of
persistent content with a version control system. This can be useful
in software that needs to be able to work offline. The web application
runs on a user's laptop that may be away from an internet
connection. When connected again, the user syncs with a version
control server, receiving updates that may have been made by others,
and committing their own changes.

The synchronization sequence (ISequences) is as follows (example given
with SVN as the version control system):
 
  1) save persistent state (IState) to svn checkout (ICheckout) on the
     same machine as the Zope application.

  2) ``svn up``. Subversion merges in changed made by others users
     that were checked into the svn server.

  3) Any svn conflicts are automatically resolved.

  4) reload changes in svn checkout into persistent Python objects

  5) ``svn commit``.

This is all happening in a single step. It can happen over and over
again in a reasonably safe manner, as after the synchronization has
concluded, the state of the persistent objects and that of the local
SVN checkout will always be perfectly in sync.

During synchronizing, the system tries to take care only to
synchronize those objects and files that have changed. That is, in
step 1) only those objects that have been modified, added or removed
will have an effect on the checkout. In step 4) only those files that
have been changed, added or removed on the filesystem due to the
``up`` action will change the persistent object state.

SVN difficulties
----------------

Changing a file into a directory with SVN requires the following
procedure::
  
  * svn remove file

  * svn commit file

  * svn up

  * mdkir file

  * svn add file

If during the serialization procedure a file changed into a directory,
it would require an ``svn up`` to be issued during step 1. This is too
early. As we see later, we instead ask the application developer to
avoid this situation altogether.

To start
--------

Let's first grok this package::

  >>> import grok
  >>> grok.grok('z3c.vcsync')

Serialization
-------------

In order to export content to a version control system, it first needs
to be possible to serialize a content object to a text representation.

For the purposes of this document, we have defined a simple item that
just carries an integer payload attribute::

  >>> class Item(object):
  ...   def __init__(self, payload):
  ...     self.payload = payload
  >>> item = Item(payload=1)
  >>> item.payload
  1

We will use an ISerializer adapter to serialize it to a file. Let's
define the adapter::

  >>> from z3c.vcsync.interfaces import ISerializer
  >>> class ItemSerializer(grok.Adapter):
  ...     grok.provides(ISerializer)
  ...     grok.context(Item)
  ...     def serialize(self, f):
  ...         f.write(str(self.context.payload))
  ...         f.write('\n')
  ...     def name(self):
  ...         return self.context.__name__ + '.test'

Let's test our adapter::

  >>> from StringIO import StringIO
  >>> f= StringIO()
  >>> ItemSerializer(item).serialize(f)
  >>> f.getvalue()
  '1\n'

Let's register the adapter::

  >>> grok.grok_component('ItemSerializer', ItemSerializer)
  True

We can now use the adapter::

  >>> f = StringIO()
  >>> ISerializer(item).serialize(f)
  >>> f.getvalue()
  '1\n'

Export persistent state to version control system checkout
----------------------------------------------------------

As part of the synchronization procedure we need the ability to export
persistent python objects to the version control checkout directory in
the form of files and directories. 
 
Content is represented by an ``IState``. This supports two methods:

* ``objects(dt)``: any object that has been modified since dt. Returning
  'too many' objects (objects that weren't modified) is safe, though less
  efficient as they will then be re-exported. 

  Typically in your application this would be implemented as the
  result of a catalog search.

* ``removed(dt)``: any path that has had an object removed from it
  since dt.  It is safe to return paths that have been removed and
  have since been replaced by a different object with the same
  name. It is also safe to return 'too many' paths, though less
  efficient as the objects in these paths may be re-exported
  unnecessarily. 

  Typically in your application you would maintain a list of removed
  objects by hooking into IObjectRemovedEvent and recording the paths
  of all objects that were removed. After an export it is safe to
  purge this list.

Let's imagine we have this object structure consisting of a container
with some items and sub-containers in it::

  >>> data = Container()
  >>> data.__name__ = 'root'
  >>> data['foo'] = Item(payload=1)
  >>> data['bar'] = Item(payload=2)
  >>> data['sub'] = Container()
  >>> data['sub']['qux'] = Item(payload=3)

This object structure has some test payload data::

  >>> data['foo'].payload
  1
  >>> data['sub']['qux'].payload
  3

We have a checkout in testpath on the filesystem::

  >>> testpath = create_test_dir()
  >>> checkout = TestCheckout(testpath)

We also have a test state representing the object data::

  >>> state = TestState(data)

The test state will always return a list of all objects. We pass in
``None`` for the datetime here, as the TestState ignores this
information anyway::

  >>> sorted([obj.__name__ for obj in state.objects(None)])
  ['bar', 'foo', 'qux', 'root', 'sub']

Now let's synchronize. For this, we need a synchronizer initialized
with the checkout and the state::
  
  >>> from z3c.vcsync import Synchronizer
  >>> s = Synchronizer(checkout, state)

We now save the state into that checkout. We are passing ``None`` for
the dt for the time being::

  >>> s.save(None)

The filesystem should now contain the right objects. Everything is
always saved in a directory called ``root``:
 
  >>> root = testpath.join('root')
  >>> root.check(dir=True)
  True

This root directory should contain the right objects::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['bar.test', 'foo.test', 'sub']

We expect the right contents in ``bar.test`` and ``foo.test``::

  >>> root.join('bar.test').read()
  '2\n'
  >>> root.join('foo.test').read()
  '1\n'

``sub`` is a container so should be represented as a directory::

  >>> sub_path = root.join('sub')
  >>> sub_path.check(dir=True)
  True

  >>> sorted([entry.basename for entry in sub_path.listdir()])
  ['qux.test']

  >>> sub_path.join('qux.test').read()
  '3\n'

Modifying an existing checkout
------------------------------

Now let's assume that the version control checkout is that as
generated by step 1a). We will now change some data in the ZODB again.

Let's add ``hoi``::
  
  >>> data['hoi'] = Item(payload=4)

And let's delete ``bar``::

  >>> del data['bar']

Since we are removing something, we need inform the state about it. We
do this manually here, though in a real application typically you
would subscribe to the ``IObjectRemovedEvent``.

  >>> removed_paths = ['/root/bar']
  >>> state.removed_paths = removed_paths

The added object always will return with ``objects``, but in your
application you may also need to let the state know.
 
Let's save the object structure again to the same checkout::
 
  >>> s.save(None)

We expect the ``hoi.test`` file to be added::

  >>> root.join('hoi.test').read()
  '4\n'

We also expect the ``bar.test`` file to be removed::

  >>> root.join('bar.test').check()
  False

Modifying an existing checkout, some edge cases
-----------------------------------------------

The ZODB has changed again.  Item 'hoi' has changed from an item into
a container::

  >>> del data['hoi']
  >>> data['hoi'] = Container()

Let's create a new removed list. The item 'hoi' was removed before it
was removed with a new container with the same name, so we have to
remember this::

  >>> removed_paths = ['/root/hoi']
  >>> state.removed_paths = removed_paths

We put some things into the new container::

  >>> data['hoi']['something'] = Item(payload=15)

We export again into the existing checkout (which still has 'hoi' as a
file)::

  >>> s.save(None)

Let's check the filesystem state::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi', 'sub']

We expect ``hoi`` to contain ``something.test``::

  >>> hoi_path = root.join('hoi')
  >>> something_path = hoi_path.join('something.test')
  >>> something_path.read()
  '15\n'

Let's now change the ZODB again and change the ``hoi`` container back
into a file::

  >>> del data['hoi']
  >>> data['hoi'] = Item(payload=16)
  >>> s.save(None)

This means we need to mark the path to the container to be removed::

  >>> removed_paths = ['/root/hoi']
  >>> state.removed_paths = removed_paths

We expect to see a ``hoi.test`` but no ``hoi`` directory anymore::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi.test', 'sub']

Note: creating a container with the name ``hoi.test`` (using the
``.test`` postfix) will lead to trouble now, as we already have a file
``hoi.test``. ``svn`` doesn't allow a single-step replace of a file
with a directory - as expressed earlier, an ``svn up`` would need to
be issued first, but this would be too early in the process. Solving
this problem is quite involved. Instead, we require the application to
avoid creating any directories with a postfix in use by items. The
following should be forbidden::

  data['hoi.test'] = Container()

multiple object types
---------------------

We will now introduce a second object type::

  >>> class OtherItem(object):
  ...   def __init__(self, payload):
  ...     self.payload = payload

We will need an ``ISerializer`` adapter for ``OtherItem`` too::

  >>> class OtherItemSerializer(grok.Adapter):
  ...     grok.provides(ISerializer)
  ...     grok.context(OtherItem)
  ...     def serialize(self, f):
  ...         f.write(str(self.context.payload))
  ...         f.write('\n')
  ...     def name(self):
  ...         return self.context.__name__ + '.other'
  >>> grok.grok_component('OtherItemSerializer', OtherItemSerializer)
  True

Note that the extension we serialize to is ``.other``.

Let's now change the ``hoi`` object into an ``OtherItem``. First we remove
the original ``hoi``::

  >>> del data['hoi']

We need to mark this removal in our ``removed_paths`` list::

  >>> state.removed_paths = ['/root/hoi']

We then introduce the new ``hoi``::

  >>> data['hoi'] = OtherItem(23)

Let's serialize::

  >>> s.save(None)

We expect to see a ``hoi.other`` item now::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi.other', 'sub']

Let's change the object back again::

  >>> del data['hoi']
  >>> state.removed_paths = ['/root/hoi']
  >>> data['hoi'] = Item(payload=16)
  >>> s.save(None)

We expect to see a ``hoi.test`` item again::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi.test', 'sub']

loading a checkout state into python objects
--------------------------------------------

Let's load the currentfilesystem layout into python objects. Factories
are registered as utilities for the different things we can encounter
on the filesystem. Let's look at items first. A factory is registered
for the ``.test`` extension::

  >>> from z3c.vcsync.interfaces import IVcFactory
  >>> class ItemFactory(grok.GlobalUtility):
  ...   grok.provides(IVcFactory)
  ...   grok.name('.test')
  ...   def __call__(self, path):
  ...       payload = int(path.read())
  ...       return Item(payload)
  >>> grok.grok_component('ItemFactory', ItemFactory)
  True

Now for containers. They are registered for an empty extension::

  >>> class ContainerFactory(grok.GlobalUtility):
  ...   grok.provides(IVcFactory)
  ...   def __call__(self, path):
  ...       container = Container()
  ...       return container
  >>> grok.grok_component('ContainerFactory', ContainerFactory)
  True

We need to maintain a list of everything modified or added, and a list
of everything deleted by the update operation. Normally this
information is extracted from the version control system, but for the
purposes of this test we maintain it manually. In this case,
everything is added so appears in the files list::

  >>> checkout._files = [root.join('foo.test'), root.join('hoi.test'),
  ...   root.join('sub'), root.join('sub', 'qux.test')]

Nothing was removed::

  >>> checkout._removed = []

Let's load up the contents from the filesystem now, into a new container::

  >>> container2 = Container()
  >>> container2.__name__ = 'root'

In order to load into a different container, we need to set up a new
synchronizer with a new state::

  >>> s = Synchronizer(checkout, TestState(container2))

We can now do the loading::

  >>> s.load(None)

We expect the proper objects to be in the new container::

  >>> sorted(container2.keys())
  ['foo', 'hoi', 'sub']

We check whether the items contains the right information::

  >>> isinstance(container2['foo'], Item)
  True
  >>> container2['foo'].payload
  1
  >>> isinstance(container2['hoi'], Item)
  True
  >>> container2['hoi'].payload
  16
  >>> isinstance(container2['sub'], Container)
  True
  >>> sorted(container2['sub'].keys())
  ['qux']
  >>> container2['sub']['qux'].payload
  3

version control changes a file
------------------------------

Now we synchronize our checkout by synchronizing the checkout with the
central coordinating server (or shared branch in case of a distributed
version control system). We do a ``checkout.up()`` that causes the
text in a file to be modified.

The special checkout class we use for example purposes will call
``update_function`` during an update. This function should then
simulate what might happen during a version control system ``update``
operation. Let's define one here that modifies text in a file::

  >>> hoi_path = root.join('hoi.test')
  >>> def update_function():
  ...    hoi_path.write('200\n')
  >>> checkout.update_function = update_function

Now let's do an update::

  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = [hoi_path]
  >>> checkout._removed = []

We will reload the checkout into Python objects::

  >>> s.load(None)
 
We expect the ``hoi`` object to be modified::

  >>> container2['hoi'].payload
  200

version control adds a file
---------------------------

We update our checkout again and cause a file to be added::

  >>> hallo = root.join('hallo.test').ensure()
  >>> def update_function():
  ...   hallo.write('300\n')
  >>> checkout.update_function = update_function

  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = [hallo]
  >>> checkout._removed = []

We will reload the checkout into Python objects again::

  >>> s.load(None)
 
We expect there to be a new object ``hallo``::

  >>> 'hallo' in container2.keys()
  True

version control removes a file
------------------------------

We update our checkout and cause a file to be removed::

  >>> def update_function():
  ...   root.join('hallo.test').remove()
  >>> checkout.update_function = update_function

  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = []
  >>> checkout._removed = [hallo]

We will reload the checkout into Python objects::
  
  >>> s.load(None)

We expect the object ``hallo`` to be gone again::

  >>> 'hallo' in container2.keys()
  False

version control adds a directory
--------------------------------

We update our checkout and cause a directory (with a file inside) to be
added::

  >>> newdir_path = root.join('newdir')
  >>> def update_function():
  ...   newdir_path.ensure(dir=True)
  ...   newfile_path = newdir_path.join('newfile.test').ensure()
  ...   newfile_path.write('400\n')
  >>> checkout.update_function = update_function
  
  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = [newdir_path, newdir_path.join('newfile.test')]
  >>> checkout._removed = []

Reloading this will cause a new container to exist::

  >>> s.load(None)
  >>> 'newdir' in container2.keys()
  True
  >>> isinstance(container2['newdir'], Container)
  True
  >>> container2['newdir']['newfile'].payload
  400

version control removes a directory
-----------------------------------

We update our checkout once again and cause a directory to be removed::

  >>> def update_function():
  ...   newdir_path.remove()
  >>> checkout.update_function = update_function

  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = []
  >>> checkout._removed = [newdir_path, newdir_path.join('newfile.test')]

And reload the data::

  >>> s.load(None)

Reloading this will cause the new container to be gone again::

  >>> 'newdir' in container2.keys()
  False

version control changes a file into a directory
-----------------------------------------------

Some sequence of actions by other users has caused a name that previously
referred to a file to now refer to a directory::

  >>> hoi_path2 = root.join('hoi')
  >>> def update_function():
  ...   hoi_path.remove()
  ...   hoi_path2.ensure(dir=True)
  ...   some_path = hoi_path2.join('some.test').ensure(file=True)
  ...   some_path.write('1000\n')
  >>> checkout.update_function = update_function

We maintain the lists of things changed::

  >>> checkout._files = [hoi_path2, hoi_path2.join('some.test')]
  >>> checkout._removed = [hoi_path]

  >>> checkout.up()

Reloading this will cause a new container to be there instead of the file::

  >>> s.load(None)
  >>> isinstance(container2['hoi'], Container)
  True
  >>> container2['hoi']['some'].payload
  1000

version control changes a directory into a file
-----------------------------------------------

Some sequence of actions by other users has caused a name that
previously referred to a directory to now refer to a file::

  >>> def update_function():
  ...   hoi_path2.remove()
  ...   hoi_path = root.join('hoi.test').ensure()
  ...   hoi_path.write('2000\n')
  >>> checkout.update_function = update_function

  >>> checkout.up()

We maintain the lists of things changed::

  >>> checkout._files = [hoi_path]
  >>> checkout._removed = [hoi_path2.join('some.test'), hoi_path2]

Reloading this will cause a new item to be there instead of the
container::

  >>> s.load(None)
  >>> isinstance(container2['hoi'], Item)
  True
  >>> container2['hoi'].payload
  2000

Complete synchronization
------------------------

Let's now exercise the ``sync`` method directly. First we'll modify
the payload of the ``hoi`` item::

  >>> container2['hoi'].payload = 3000
 
Next, we willl add a new ``alpha`` file to the checkout when we do an
``up()``, so again we simulate the actions of our version control system::

  >>> alpha_path = root.join('alpha.test').ensure()
  >>> def update_function():
  ...   alpha_path.write('4000\n')
  >>> checkout.update_function = update_function

We maintain the lists of things changed::

  >>> checkout._files = [alpha_path]
  >>> checkout._removed = []

Now we'll synchronize with the memory structure::

  >>> s.sync(None)

We expect the checkout to reflect the changed state of the ``hoi`` object::

  >>> root.join('hoi.test').read()
  '3000\n'

We also expect the database to reflect the creation of the new
``alpha`` object::

  >>> container2['alpha'].payload
  4000

Exporting
---------

Besides version control synchronization, the same infrastructure
can also be used for an export and import procedure.

Here we export the state to a target directory::

  >>> from z3c.vcsync import export_state
  >>> target = create_test_dir()
  >>> export_state(TestState(container2), target)

Let's inspect the state of container2 first::

  >>> sorted(container2.keys())
  ['alpha', 'foo', 'hoi', 'sub']
  >>> sorted(container2['sub'].keys())
  ['qux']
  >>> container2['alpha'].payload
  4000
  >>> container2['foo'].payload
  1
  >>> container2['hoi'].payload
  3000
  >>> container2['sub']['qux'].payload
  3

We can inspect the target directory and see the data is there::

  >>> sorted([p.basename for p in target.listdir()])
  ['alpha.test', 'foo.test', 'hoi.test', 'sub']
  >>> target.join('alpha.test').read()
  '4000\n'
  >>> target.join('foo.test').read()
  '1\n'
  >>> target.join('hoi.test').read()
  '3000\n'
  >>> sub = target.join('sub')
  >>> sorted([p.basename for p in sub.listdir()])
  ['qux.test']
  >>> sub.join('qux.test').read()
  '3\n'

Importing
---------

Now we import the state on the filesystem into a fresh container::

  >>> container3 = Container()
  >>> container3.__name__ = 'root'

  >>> from z3c.vcsync import import_state
  >>> import_state(TestState(container3), target)

We expect the structure to be the same as what we exported::

  >>> sorted(container3.keys())
  ['alpha', 'foo', 'hoi', 'sub']
  >>> sorted(container3['sub'].keys())
  ['qux']
  >>> container3['alpha'].payload
  4000
  >>> container3['foo'].payload
  1
  >>> container3['hoi'].payload
  3000
  >>> container3['sub']['qux'].payload
  3

Note that importing into a container with existing content isn't supported yet.
