Versioning
==========


We start by testing some of the existing infrastructure from zope.app.versioncontrol
and try to apply the existing versioning to sample data. We take a simple
folder tree with the following structure :

  sample
    |--> a <--|
    |--> b    |
         |--> c
     

  >>> import zope.app.versioncontrol.interfaces
  >>> from zope.interface import directlyProvides
  >>> from zope.app.versioncontrol.repository import declare_versioned
  >>> from versioning.tests.repository_setup import registerAdapter
  >>> from zope.app.folder import Folder, rootFolder
  >>> from zope.app.tests.setup import setUpTraversal
  >>> from zope.app.traversing.interfaces import IPhysicallyLocatable
  >>> from ZODB.tests import util
  >>> from zope.app.versioncontrol.interfaces import IVersioned
  >>> registerAdapter()
  >>> setUpTraversal()
  >>> class TestFolder(Folder) :
  ...   zope.interface.implements(IPhysicallyLocatable)
  ...   def getPath(self) :
  ...       return ""
  
  >>> sample = TestFolder()
  >>> directlyProvides(sample, zope.app.traversing.interfaces.IContainmentRoot)
  >>> a = sample["a"] = TestFolder()
  >>> b = sample["b"] = TestFolder()
  >>> c = b["c"] = TestFolder()
  >>> for x in (sample, a, b, c) :
  ...     directlyProvides(x, zope.app.versioncontrol.interfaces.IVersionable)
  
The interesting test case is the reference that uses references outside
the hierarchical ones, which should be naturally handled in Zope3:

  >>> c.refers_to = a
  >>> a == c.refers_to
  True

In order to show some limitations of the current implementation we use a
prebuild version control repository :

  >>> from versioning.tests.repository_setup import buildRepository, buildDatabaseRoot
  >>> db_root = buildDatabaseRoot()
  >>> db_root["sample"] = sample 
  >>> repository = buildRepository()
  
The current policy forces us to remove __parent__ and __name__. We'll do that
by specializing the standard adapter that removes nothing:

  >>> from zope.app.versioncontrol.nonversioned import StandardNonVersionedDataAdapter
  >>> class NonVersionedAdapter(StandardNonVersionedDataAdapter) :
  ...     attrs = ("__name__", "__parent__")   # remove __name__ and __parent from versioning
  
  
  >>> from zope.app.tests import ztapi
  >>> ztapi.provideAdapter(zope.app.versioncontrol.interfaces.IVersionable,
  ...                       zope.app.versioncontrol.interfaces.INonVersionedData,
  ...                       NonVersionedAdapter)
  >>> zope.app.versioncontrol.interfaces.INonVersionedData(a) is not None
  True

Now we can put our example data under version control:

  >>> repository.applyVersionControl(sample)
  >>> repository.applyVersionControl(a)
  >>> repository.applyVersionControl(b)
  >>> repository.applyVersionControl(c)
  >>> util.commit()
  >>> [IVersioned.providedBy(x) for x in (sample, a, b, c)]
  [True, True, True, True]
    

The implementation in zope.app.versioncontrol breaks any database identity references
because a pickle version is used that ignores all references that point
outside the sub tree. In the example above this means, that the version of c loses
its reference to a because c is not contained in a. (See 
 zope.app.versioncontrol.version.cloneByPickle)

  >>> def accessVersion(repository, obj) :
  ...   info = repository.getVersionInfo(obj)
  ...   return repository.getVersionOfResource(info.history_id, 'mainline')
  >>> new_a = accessVersion(repository, a)
  >>> new_b = accessVersion(repository, b)
  >>> new_c = accessVersion(repository, c)

Now the reference from b to c is invalid ...
  
  >>> new_b["c"] == new_c
  False
  
as well as the reference from c to a :
  
  >>> new_c.refers_to == new_a
  False

  
This demonstrates that the reference to a is not preserved, which is the major
motivation for a new implementation.




Alternative implementation
--------------------------

We want to use versioning with objects other than standard zope objects that use
only the standard containment structure meachanism. In the same time some parts
of the versioning system should be pluggable, e.g. the storage for the object histories,
the locking mechanism etc.

We start with the basic building blocks, a storage that holds version histories
of several objects. Note that this implementation does not collide with the
implementation in zope.app.versioncontrol. This versioning scheme does not attach any
information to the versioned objects and keeps the necessary bookeeping information 
encapsulated in the storage of object histories.

    >>> from versioning.storage import SimpleHistoryStorage
    >>> from versioning.policies import VersionableAspectsAdapter
    >>> histories = SimpleHistoryStorage()
    >>> histories.register(a)
    '\x00\x00\x00\x00\x00\x00\x00\x04'
    >>> histories.register(b)
    '\x00\x00\x00\x00\x00\x00\x00\x05'
    >>> util.commit()
    >>> len(histories.values())
    2
    >>> [x for x in histories.keys()]
    [u'\x00\x00\x00\x00\x00\x00\x00\x04', u'\x00\x00\x00\x00\x00\x00\x00\x05']
    >>> adapter = VersionableAspectsAdapter(a, histories)
    >>> adapter.writeAspects()
    '001'
    
    
    
    



    






