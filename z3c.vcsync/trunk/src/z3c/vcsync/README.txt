Version Control Synchronization
===============================

This package contains code that helps with handling synchronization of
persistent content with a version control system. This can be useful
in software that needs to be able to work offline. The web application
runs on a user's laptop that may be away from an internet
connection. When connected again, the user syncs with a version
control server, receiving updates that may have been made by others,
and committing their own changes.

The synchronization sequence is as follows (example given with SVN as
the version control system):
 
  1) save persistent state to svn checkout on the same machine as the
     Zope application.

  2) ``svn up``. Subversion merges in changed made by others users
     that were checked into the svn server.

  3) Any svn conflicts are automatically resolved.

  4) reload changes in svn checkout into persistent Python objects

  5) ``svn commit``.

This is all happening in a single step. It can happen over and over
again in a reasonably safe manner, as after the synchronization has
concluded, the state of the persistent objects and that of the local
SVN checkout will always be perfectly in sync.

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
 
Content is assumed to consist of two types of objects:

* containers. These are represented as directories on the filesystem.

* items. These are represented as files on the filesystem. The files
  will have an extension to indicate the type of item.

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

The object structure can now be saved into that checkout::

  >>> checkout.save(data)

The filesystem should now contain the right objects.

Everything is always saved in a directory called ``root``:
 
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

We know that no existing files or directories were deleted by this save,
as the checkout was empty before this::

  >>> checkout.deleted_by_save()
  []

We also know that certain files have been added::

  >>> rel_paths(checkout, checkout.added_by_save())
  ['/root', '/root/bar.test', '/root/foo.test', '/root/sub', 
   '/root/sub/qux.test']

Modifying an existing checkout
------------------------------

Now let's assume that the version control checkout is that as
generated by step 1a). We will bring it to its initial state first::

  >>> checkout.clear()

We will now change some data in the ZODB again to test whether we
detect additions and deletions (we need to inform the version control
system about these).

Let's add ``hoi``::
  
  >>> data['hoi'] = Item(payload=4)

And let's delete ``bar``::

  >>> del data['bar']

Let's save the object structure again to the same checkout::
  
  >>> checkout.save(data)

The checkout will now know which files were added and deleted during
the save::

  >>> rel_paths(checkout, checkout.added_by_save())
  ['/root/hoi.test']

We also know which files got deleted::

  >>> rel_paths(checkout, checkout.deleted_by_save())
  ['/root/bar.test']

Modifying an existing checkout, some edge cases
-----------------------------------------------

Let's take our checkout as one fully synched up again::

  >>> checkout.clear()

The ZODB has changed again.  Item 'hoi' has changed from an item into
a container::

  >>> del data['hoi']
  >>> data['hoi'] = Container()

We put some things into the container::

  >>> data['hoi']['something'] = Item(payload=15)

We export again into the existing checkout (which still has 'hoi' as a
file)::

  >>> checkout.save(data)

The file ``hoi.test`` should now be removed::

  >>> rel_paths(checkout, checkout.deleted_by_save())
  ['/root/hoi.test']

And the directory ``hoi`` should now be added::

  >>> rel_paths(checkout, checkout.added_by_save())
  ['/root/hoi', '/root/hoi/something.test']

Let's check the filesystem state::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi', 'sub']

We expect ``hoi`` to contain ``something.test``::

  >>> hoi_path = root.join('hoi')
  >>> something_path = hoi_path.join('something.test')
  >>> something_path.read()
  '15\n'

Let's now consider the checkout synched up entirely again::

  >>> checkout.clear()

Let's now change the ZODB again and change the ``hoi`` container back
into a file::

  >>> del data['hoi']
  >>> data['hoi'] = Item(payload=16)
  >>> checkout.save(data)

The ``hoi`` directory (and everything in it, implicitly) is now
deleted::

  >>> rel_paths(checkout, checkout.deleted_by_save())
  ['/root/hoi']

We have added ``hoi.test``::

  >>> rel_paths(checkout, checkout.added_by_save())
  ['/root/hoi.test']

We expect to see a ``hoi.test`` but no ``hoi`` directory anymore::

  >>> sorted([entry.basename for entry in root.listdir()])
  ['foo.test', 'hoi.test', 'sub']

Let's be synched-up again::

  >>> checkout.clear()

Note: creating a container with the name ``hoi.test`` (using the
``.test`` postfix) will lead to trouble now, as we already have a file
``hoi.test``. ``svn`` doesn't allow a single-step replace of a file
with a directory - as expressed earlier, an ``svn up`` would need to
be issued first, but this would be too early in the process. Solving
this problem is quite involved. Instead, we require the application to
avoid creating any directories with a postfix in use by items. The
following should be forbidden::

  data['hoi.test'] = Container()

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
  ...   def __call__(self, checkout, path):
  ...       payload = int(path.read())
  ...       return Item(payload)
  >>> grok.grok_component('ItemFactory', ItemFactory)
  True

Now for containers. They are registered for an empty extension. They
are also required to use VcLoad to load their contents::

  >>> from z3c.vcsync.interfaces import IVcLoad
  >>> class ContainerFactory(grok.GlobalUtility):
  ...   grok.provides(IVcFactory)
  ...   def __call__(self, checkout, path):
  ...       container = Container()
  ...       IVcLoad(container).load(checkout, path)
  ...       return container
  >>> grok.grok_component('ContainerFactory', ContainerFactory)
  True

We have registered enough. Let's load up the contents from the
filesystem now::

  >>> container2 = Container()
  >>> container2.__name__ = 'root'
  >>> checkout.load(container2)
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

  >>> checkout.up()

We will reload the checkout into Python objects::

  >>> checkout.load(container2)
 
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

We will reload the checkout into Python objects again::

  >>> checkout.load(container2)
 
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

We will reload the checkout into Python objects::

  >>> checkout.load(container2)

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

Reloading this will cause a new container to exist::

  >>> checkout.load(container2)

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

  >>> checkout.load(container2)

Reloading this will cause the new container to be gone again::

  >>> checkout.load(container2)
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

  >>> checkout.up()

Reloading this will cause a new container to be there instead of the file::

  >>> checkout.load(container2)
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

Reloading this will cause a new item to be there instead of the
container::

  >>> checkout.load(container2)
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

  >>> def update_function():
  ...   alpha_path = root.join('alpha.test').ensure()
  ...   alpha_path.write('4000\n')
  >>> checkout.update_function = update_function

Now we'll synchronize with the memory structure::

  >>> checkout.sync(container2)

We expect the checkout to reflect the changed state of the ``hoi`` object::

  >>> root.join('hoi.test').read()
  '3000\n'

We also expect the database to reflect the creation of the new
``alpha`` object::

  >>> container2['alpha'].payload
  4000



* are the right events being generated

* check save of unicode names
