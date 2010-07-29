================
ZODB Mount Point
================

This package provides a very simple implementation of a mount point for an
object in another ZODB connection. If you have multiple connections defined in
your ``zope.conf`` configuration file or multiple databases defined in your
Python code, you can use this package to mount any object from any database at
any location of another database.

Let's start by creating two databases in the typical Zope 3 application layout:

  >>> from ZODB.tests.test_storage import MinimalMemoryStorage
  >>> from ZODB import DB
  >>> from zope.site.folder import rootFolder, Folder
  >>> import transaction

  >>> dbmap = {}

  >>> db1 = DB(MinimalMemoryStorage(), database_name='db1', databases=dbmap)
  >>> conn1 = db1.open()
  >>> conn1.root()['Application'] = rootFolder()

  >>> db2 = DB(MinimalMemoryStorage(), database_name='db2', databases=dbmap)
  >>> conn2 = db2.open()
  >>> conn2.root()['Application'] = rootFolder()

  >>> transaction.commit()

Let's now add a sub-folder to the second database, which will serve as the
object which we wish to mount:

  >>> conn2.root()['Application']['Folder2-1'] = Folder()
  >>> transaction.commit()

We can now create a mount point:

  >>> from z3c.mountpoint import mountpoint
  >>> mountPoint = mountpoint.MountPoint(
  ...     'db2', objectPath=u'/Folder2-1', objectName=u'F2-1')

The first argument to the constructor is the connection name of the database,
the second argument is the path to the mounted object within the mounted DB
and the object name is the name under which the object is mounted.

Now we can add the mount point to the first database:

  >>> conn1.root()['Application']['mp'] = mountPoint
  >>> transaction.commit()

We can now access the mounted object as follows:

  >>> conn1.root()['Application']['mp'].object
  <zope.site.folder.Folder object at ...>

Note that the object name is not yet used; it is for traversal only.


Traversal
---------

So let's have a look at the traversal next. Before being able to traverse, we
need to register the special mount point traverser:

  >>> import zope.component
  >>> zope.component.provideAdapter(mountpoint.MountPointTraverser)

We should now be able to traverse to the mounted object now:

  >>> from zope.publisher.browser import TestRequest
  >>> req = TestRequest()

  >>> from zope.traversing.publicationtraverse import PublicationTraverser
  >>> traverser = PublicationTraverser()
  >>> traverser.traversePath(req, conn1.root()['Application'], 'mp/F2-1')
  <zope.site.folder.Folder object at ...>

When we add a new object remotely, it available via the mount point as well:

  >>> conn2.root()['Application']['Folder2-1']['Folder2-1.1'] = Folder()
  >>> transaction.commit()

  >>> tuple(traverser.traversePath(
  ...    req, conn1.root()['Application'], 'mp/F2-1').keys())
  (u'Folder2-1.1',)

Now, by default the objects refer to their original path:

  >>> f211 = traverser.traversePath(
  ...    req, conn1.root()['Application'], 'mp/F2-1/Folder2-1.1')

  >>> from zope.traversing.browser import absoluteurl
  >>> absoluteurl.absoluteURL(f211, req)
  'http://127.0.0.1/Folder2-1/Folder2-1.1'

This package solves that problem by wrapping all object by a special remote
location proxy and providing a special wrapping traverser for those proxies:

  >>> from z3c.mountpoint import remoteproxy
  >>> zope.component.provideAdapter(remoteproxy.RemoteLocationProxyTraverser)

  >>> f211 = traverser.traversePath(
  ...    req, conn1.root()['Application'], 'mp/F2-1/Folder2-1.1')
  >>> absoluteurl.absoluteURL(f211, req)
  'http://127.0.0.1/mp/F2-1/Folder2-1.1'


Updating the Mount Point
------------------------

Whenever any attribute on the mount point is modified, the mount object is
updated. For example, when the object path is changed, the object is adjusted
as well. This is done with an event subscriber:

  >>> mountPoint.objectPath = u'/Folder2-1/Folder2-1.1'

  >>> modifiedEvent = object()
  >>> mountpoint.updateMountedObject(mountPoint, modifiedEvent)

  >>> f211 == mountPoint.object
  True

