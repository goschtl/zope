==========
Versioning
==========


In the following we take a simple folder tree with the following structure
as an example :

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
  >>> [x for x in sample.keys()]
  [u'a', u'b']
  
  >>> from versioning.tests.repository_setup import buildRepository, buildDatabaseRoot
  >>> db_root = buildDatabaseRoot()
  >>> db_root["sample"] = sample 
  
In this architecture we can choose between several repositories. We take a
CopyModifyMergeRepository without check in and check out as an example.
 
  >>> from versioning.repository import CopyModifyMergeRepository
  >>> repository = buildRepository(CopyModifyMergeRepository)

Now we can put our example data under version control:

  >>> repository.applyVersionControl(sample)
  >>> repository.applyVersionControl(a)
  >>> repository.applyVersionControl(b)
  >>> repository.applyVersionControl(c)
  >>> util.commit()
  >>> [IVersioned.providedBy(x) for x in (sample, a, b, c)]
  [True, True, True, True]
  >>> [x for x in sample.keys()]
  [u'a', u'b']
  


  >>> def accessVersion(repository, obj) :
  ...   info = repository.getVersionInfo(obj)
  ...   return repository.getVersionOfResource(info.history_id, 'mainline')
  >>> new_a = accessVersion(repository, a)
  >>> new_b = accessVersion(repository, b)
  >>> new_c = accessVersion(repository, c)
  >>> [x for x in sample.keys()]
  [u'a', u'b']
