Version Control Synchronization
===============================

This package contains code that helps with handling synchronization of
persistent content with a version control system. 

This can be useful in software that needs to be able to work
offline. The web application runs on a user's laptop that may be away
from an internet connection. When connected again, the user syncs with
a version control server, receiving updates that may have been made by
others, and committing their own changes.

Another advantage is that the version control system always contains a
history of how content developed over time. The version-control based
content can also be used for other purposes independent of the
application.

While this package has been written with other version control systems
in mind, it has only been developed to work with SVN so far. Examples
below are all given with SVN.

The synchronization sequence is as follows:
 
1) save persistent state (IState) to svn checkout (ICheckout) on the
   same machine as the Zope application.

2) ``svn up``. Subversion merges in changed made by others users that
   were checked into the svn server.

3) Any svn conflicts are automatically resolved.

4) reload changes in svn checkout into persistent Python objects

5) ``svn commit``.

This is all happening in a single step. It can happen over and over
again in a reasonably safe manner, as after the synchronization has
concluded, the state of the persistent objects and that of the local
SVN checkout will always be in sync.

During synchronisation, the system tries to take care only to
synchronize those objects and files that have changed. That is, in
step 1) only applies those objects that have been modified, added or
removed will have an effect on the checkout. In step 4) only those
files that have been changed, added or removed on the filesystem due
to the ``up`` action will change the persistent object state.

State
-----
 
Content to synchronize is represented by an object that provides
``IState``. The following methods need to be implemented:

* ``get_revision_nr()``: return the last revision number that the
   application was synchronized with. The state typically stores this
   the application object.

* ``set_revision_nr(nr)``: store the last revision number that the
  application was synchronized with.

* ``objects(revision_nr)``: any object that has been modified (or
  added) since the synchronization for ``revision_nr``. Returning 'too
  many' objects (objects that weren't modified) is safe, though less
  efficient as they will then be re-exported.

  Typically in your application this would be implemented by doing
  a catalog search, so that they can be looked up quickly.

* ``removed(revision_nr)``: any path that has had an object removed
  from it since revision_nr.  It is safe to return paths that have
  been removed and have since been replaced by a different object with
  the same name. It is also safe to return 'too many' paths, though
  less efficient as the objects in these paths may be re-exported
  unnecessarily.

  Typically in your application you would maintain a list of removed
  objects by hooking into ``IObjectMovedEvent`` and
  ``IObjectRemovedEvent`` and recording the paths of all objects that
  were moved or removed. After an export it is safe to purge this
  list.

In this example, we will use a simpler, less efficient, implementation
that goes through a content to find changes. It tracks the
revision number as a special attribute of the root object::

  >>> from zope.interface import implements
  >>> from z3c.vcsync.interfaces import IState
  >>> class TestState(object):
  ...     implements(IState)
  ...     def __init__(self, root):
  ...         self.root = root
  ...     def set_revision_nr(self, nr):
  ...         self.root.nr = nr
  ...     def get_revision_nr(self):
  ...         try:
  ...             return self.root.nr
  ...         except AttributeError:
  ...             return 0
  ...     def removed(self, revision_nr):
  ...         return []
  ...     def objects(self, revision_nr):
  ...         for container in self._containers(revision_nr):
  ...             for value in container.values():
  ...                 if isinstance(value, Container):
  ...                     continue
  ...                 if value.revision_nr >= revision_nr:
  ...                     yield value
  ...     def _containers(self, revision_nr):
  ...         return self._containers_helper(self.root)
  ...     def _containers_helper(self, container):
  ...         yield container
  ...         for obj in container.values():
  ...             if not isinstance(obj, Container):
  ...                 continue
  ...             for sub_container in self._containers_helper(obj):
  ...                 yield sub_container


The content
-----------

Now that we have something that can synchronize a tree of content in
containers, let's actually build ourselves a tree of content.

An item contains some payload data, and maintains the SVN revision
after which it was changed. In a real application you would typically
maintain the revision number of objects by using an annotation and
listening to ``IObjectModifiedEvent``, but we will use a property
here::

  >>> class Item(object):
  ...   def __init__(self, payload):
  ...     self.payload = payload
  ...   def _get_payload(self):
  ...     return self._payload
  ...   def _set_payload(self, value):
  ...     self._payload = value
  ...     self.revision_nr = get_revision_nr()
  ...   payload = property(_get_payload, _set_payload)

This code needs a global ``get_revision_nr`` function available to get access
to the revision number of last synchronization. For now we'll just define
this to return 0, but we will change this later::

  >>> def get_revision_nr():
  ...    return 0

Besides the ``Item`` class, we also have a ``Container`` class, set up
before this test started. It is a class that implements enough of the
dictionary API and implements the ``IContainer`` interface. A normal
Zope 3 folder or Grok container will also work. Let's now set up the
tree::

  >>> data = Container()
  >>> data.__name__ = 'root'
  >>> data['foo'] = Item(payload=1)
  >>> data['bar'] = Item(payload=2)
  >>> data['sub'] = Container()
  >>> data['sub']['qux'] = Item(payload=3)

As part of the synchronization procedure we need the ability to export
persistent python objects to the version control checkout directory in
the form of files and directories.

Now that we have an implementation of ``IState`` that works for our
state, let's create our ``state`` object::

  >>> state = TestState(data)

Reading from and writing to the filesystem
------------------------------------------

To integrate with the synchronization machinery, we need a way to dump
a Python object to the filesystem (to an SVN working copy), and to
parse it back to an object again.

Let's grok this package first, as it provides some of the required
infrastructure::

  >>> import grok.testing
  >>> grok.testing.grok('z3c.vcsync')
  
We need to provide a serializer for the Item class that takes an item
and writes it to the filesystem to a file with a particular extension
(``.test``)::

  >>> import grok
  >>> from z3c.vcsync.interfaces import ISerializer
  >>> class ItemSerializer(grok.Adapter):
  ...     grok.provides(ISerializer)
  ...     grok.context(Item)
  ...     def serialize(self, f):
  ...         f.write(str(self.context.payload))
  ...         f.write('\n')
  ...     def name(self):
  ...         return self.context.__name__ + '.test'

We also need to provide a parser to load an object from the filesystem
back into Python, overwriting the previously existing object::

  >>> from z3c.vcsync.interfaces import IParser
  >>> class ItemParser(grok.GlobalUtility):
  ...   grok.provides(IParser)
  ...   grok.name('.test')
  ...   def __call__(self, object, path):
  ...      object.payload = int(path.read())

Sometimes there is no previously existing object in the Python tree,
and we need to add it. To do this we implement a factory (where we use
the parser for the real work)::

  >>> from z3c.vcsync.interfaces import IFactory
  >>> from zope import component
  >>> class ItemFactory(grok.GlobalUtility):
  ...   grok.provides(IFactory)
  ...   grok.name('.test')
  ...   def __call__(self, path):
  ...       parser = component.getUtility(IParser, '.test')
  ...       item = Item(None) # dummy payload
  ...       parser(item, path)
  ...       return item

Both parser and factory are registered per extension, in this case
``.test``. This is the name of the utility.

We register these components::

  >>> grok.testing.grok_component('ItemSerializer', ItemSerializer)
  True
  >>> grok.testing.grok_component('ItemParser', ItemParser)
  True
  >>> grok.testing.grok_component('ItemFactory', ItemFactory)
  True

We also need a parser and factory for containers, registered for the
empty extension (thus no special utility name). These can be very
simple::

  >>> class ContainerParser(grok.GlobalUtility):
  ...     grok.provides(IParser)
  ...     def __call__(self, object, path):
  ...         pass

  >>> class ContainerFactory(grok.GlobalUtility):
  ...     grok.provides(IFactory)
  ...     def __call__(self, path):
  ...         return Container()

  >>> grok.testing.grok_component('ContainerParser', ContainerParser)
  True
  >>> grok.testing.grok_component('ContainerFactory', ContainerFactory)
  True

Setting up the SVN repository
-----------------------------

Now we need an SVN repository to synchronize with. We create a test
SVN repository now and create a svn path to a checkout::

  >>> repo, wc = svn_repo_wc()

We can now initialize the ``SvnCheckout`` object with the SVN path to
the checkout we just created::

  >>> from z3c.vcsync.svn import SvnCheckout
  >>> checkout = SvnCheckout(wc)

Constructing the synchronizer
-----------------------------

Now that we have the checkout and the state, we can set up a synchronizer::

  >>> from z3c.vcsync import Synchronizer
  >>> s = Synchronizer(checkout, state)

Let's make ``s`` the current synchronizer as well. We need this in
this example to get back to the last revision number::

  >>> current_synchronizer = s

It's now time to set up our ``get_revision_nr`` function a bit better,
making use of the information in the current synchronizer. In actual
applications we'd probably get the revision number directly from the
content, and there would be no need to get back to the synchronizer
(it doesn't need to be persistent but can be constructed on demand)::

  >>> def get_revision_nr():
  ...    return current_synchronizer.state.get_revision_nr()

Synchronization
---------------

We'll synchronize for the first time now::

  >>> info = s.sync("synchronize")

We will now examine the SVN checkout to see whether the
synchronization was successful.

To do this we'll introduce some helper functions that help us present
the paths in a more readable form, relative to the base of the
checkout::

  >>> def pretty_path(path):
  ...     return path.relto(wc)
  >>> def pretty_paths(paths):
  ...     return sorted([pretty_path(path) for path in paths])

We see that the Python object structure of containers and items has
been translated to the same structure of directories and ``.test``
files on the filesystem::

  >>> pretty_paths(wc.listdir())
  ['root']
  >>> pretty_paths(wc.join('root').listdir())
  ['root/bar.test', 'root/foo.test', 'root/sub']
  >>> pretty_paths(wc.join('root').join('sub').listdir())
  ['root/sub/qux.test']

The ``.test`` files have the payload data we expect::
  
  >>> print wc.join('root').join('foo.test').read()
  1
  >>> print wc.join('root').join('bar.test').read()
  2
  >>> print wc.join('root').join('sub').join('qux.test').read()
  3

Synchronization back into objects
---------------------------------

Let's now try the reverse: we will change the SVN content from another
checkout, and synchronize the changes back into the object tree.

We have a second, empty tree that we will load objects into::

  >>> last_revision_nr = 0
  >>> data2 = Container()
  >>> data2.__name__ = 'root'
  >>> state2 = TestState(data2)

We make another checkout of the repository::

  >>> import py
  >>> wc2 = py.test.ensuretemp('wc2')
  >>> wc2 = py.path.svnwc(wc2)
  >>> wc2.checkout(repo)
  >>> checkout2 = SvnCheckout(wc2)

Let's make a synchronizer for this new checkout and state::

  >>> s2 = Synchronizer(checkout2, state2)

This is now the current synchronizer (so that our ``get_revision_nr``
works properly)::

  >>> current_synchronizer = s2

Now we'll synchronize::

  >>> info = s2.sync("synchronize")

The state of objects in the tree must now mirror that of the original state::

  >>> sorted(data2.keys())    
  ['bar', 'foo', 'root', 'sub']

Now we will change some of these objects, and synchronize again::

  >>> data2['bar'].payload = 20
  >>> data2['sub']['qux'].payload = 30
  >>> info2 = s2.sync("synchronize")

We can now synchronize the original tree again::

  >>> current_synchronizer = s
  >>> info = s.sync("synchronize")

We should see the changes reflected into the original tree::

  >>> data['bar'].payload
  20
  >>> data['sub']['qux'].payload
  30

Conflicts
---------

Let's now generate a conflict: we change the same object in both trees
at the same time::

  >>> data['bar'].payload = 200
  >>> current_synchronizer = s2
  >>> data2['bar'].payload = 250

Let's synchronize the second tree first::

  >>> info = s2.sync("synchronize")

Now we'll synchronize the first tree::

  >>> current_synchronizer = s
  >>> info = s.sync("synchronize")

The conflict will have been resolved in favor of the first tree, as
this synchronized last::

  >>> data['bar'].payload
  200

When we synchronize from the second tree again, we will see the
resolved value appear as well::

  >>> current_synchronizer = s
  >>> info = s2.sync("synchronize")
  >>> data2['bar'].payload
  200

Conflicts in subdirectories should also be resolved properly::

  >>> data['sub']['qux'].payload = 35 
  >>> current_synchronizer = s2
  >>> data2['sub']['qux'].payload = 36
  >>> info = s2.sync("Synchronize")
  >>> current_synchronizer = s
  >>> info = s.sync("Synchronize")
  >>> data['sub']['qux'].payload
  35
  >>> current_synchronizer = s2
  >>> info = s2.sync("Synchronize")
  >>> data2['sub']['qux'].payload
  35
