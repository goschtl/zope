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
``IState``. A state represents a container object, which should
contain a ``data`` object (a container that contains the actual data
to be synchronized) and a ``found`` object (a container that contains
objects that would otherwise be lost during conflict resolution).

The following methods need to be implemented:

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

  >>> from z3c.vcsync.tests import TestState

The content
-----------

Now that we have something that can synchronize a tree of content in
containers, let's actually build ourselves a tree of content.

An item contains some payload data, and maintains the SVN revision
after which it was changed. In a real application you would typically
maintain the revision number of objects by using an annotation and
listening to ``IObjectModifiedEvent``, but we will use a property
here::

  >>> from z3c.vcsync.tests import Item

This code needs a ``get_revision_nr`` method available to get access
to the revision number of last synchronization. For now we'll just define
this to return 0, but we will change this later::

  >>> def get_revision_nr(self):
  ...    return 0
  >>> Item.get_revision_nr = get_revision_nr

Besides the ``Item`` class, we also have a ``Container`` class::

  >>> from z3c.vcsync.tests import Container

It is a class that implements enough of the dictionary API and
implements the ``IContainer`` interface. A normal Zope 3 folder or
Grok container will also work. 

Let's create a container now::

  >>> root = Container()
  >>> root.__name__ = 'root'

The container has two subcontainers (``data`` and ``found``).

  >>> root['data'] = data = Container()
  >>> root['found'] = Container()
  >>> data['foo'] = Item(payload=1)
  >>> data['bar'] = Item(payload=2)
  >>> data['sub'] = Container()
  >>> data['sub']['qux'] = Item(payload=3)

As part of the synchronization procedure we need the ability to export
persistent python objects to the version control checkout directory in
the form of files and directories.

Now that we have an implementation of ``IState`` that works for our
state, let's create our ``state`` object::

  >>> state = TestState(root)

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

  >>> from z3c.vcsync.tests import ItemSerializer

We also need to provide a parser to load an object from the filesystem
back into Python, overwriting the previously existing object::

  >>> from z3c.vcsync.tests import ItemParser

Sometimes there is no previously existing object in the Python tree,
and we need to add it. To do this we implement a factory (where we use
the parser for the real work)::

  >>> from z3c.vcsync.tests import ItemFactory

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

  >>> from z3c.vcsync.tests import ContainerParser, ContainerFactory
  >>> grok.testing.grok_component('ContainerParser', ContainerParser)
  True
  >>> grok.testing.grok_component('ContainerFactory', ContainerFactory)
  True

Setting up the SVN repository
-----------------------------

Now we need an SVN repository to synchronize with. We create a test
SVN repository now and create a svn path to a checkout::

  >>> from z3c.vcsync.tests import svn_repo_wc
  >>> repo, wc = svn_repo_wc()

We can now initialize the ``SvnCheckout`` object with the SVN path to
the checkout we just created::

  >>> from z3c.vcsync.svn import SvnCheckout
  >>> checkout = SvnCheckout(wc)

The root directory of the working copy will be synchronized with the
root container of the state. The checkout will therefore contain
``data`` and a ``found`` sub-directories.

Constructing the synchronizer
-----------------------------

Now that we have the checkout and the state, we can set up a synchronizer::

  >>> from z3c.vcsync import Synchronizer
  >>> s = Synchronizer(checkout, state)

Let's make ``s`` the current synchronizer as well. We need this in
this example to get back to the last revision number::

  >>> current_synchronizer = s

It's now time to set up our ``get_revision_nr`` method a bit better,
making use of the information in the current synchronizer. In actual
applications we'd probably get the revision number directly from the
content, and there would be no need to get back to the synchronizer
(it doesn't need to be persistent but can be constructed on demand)::

  >>> def get_revision_nr(self):
  ...    return current_synchronizer.state.get_revision_nr()
  >>> Item.get_revision_nr = get_revision_nr

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
  ['data']
  >>> pretty_paths(wc.join('data').listdir())
  ['data/bar.test', 'data/foo.test', 'data/sub']
  >>> pretty_paths(wc.join('data').join('sub').listdir())
  ['data/sub/qux.test']

The ``.test`` files have the payload data we expect::
  
  >>> print wc.join('data').join('foo.test').read()
  1
  >>> print wc.join('data').join('bar.test').read()
  2
  >>> print wc.join('data').join('sub').join('qux.test').read()
  3

Synchronization back into objects
---------------------------------

Let's now try the reverse: we will change the SVN content from another
checkout, and synchronize the changes back into the object tree.

We have a second, empty tree that we will load objects into::

  >>> root2 = Container()
  >>> root2.__name__ = 'root'
  >>> state2 = TestState(root2)

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

  >>> sorted(root2.keys())    
  ['data']

  >>> sorted(root2['data'].keys())
  ['bar', 'foo', 'sub']

Now we will change some of these objects, and synchronize again::

  >>> root2['data']['bar'].payload = 20
  >>> root2['data']['sub']['qux'].payload = 30
  >>> info2 = s2.sync("synchronize")

We can now synchronize the original tree again::

  >>> current_synchronizer = s
  >>> info = s.sync("synchronize")

We should see the changes reflected into the original tree::

  >>> root2['data']['bar'].payload
  20
  >>> root2['data']['sub']['qux'].payload
  30

More information
----------------

To learn more about the APIs you can use and need to implement, see
``interfaces.py``.

To learn about using ``z3c.vcsync`` to import and export content, see
``importexport.txt``.

More low-level information may be gleaned from ``conflicts.txt`` and
``internal.txt``.

