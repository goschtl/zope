==========
Versioning
==========

General Setup Stuff
-------------------

In the following we take a simple folder tree with the following structure
as an example :

  sample
    |--> a <--|
    |--> b    |
         |--> c
     
  >>> import zope.app.versioncontrol.interfaces
  >>> from zope.interface import directlyProvides
  >>> from zope.app.folder import Folder, rootFolder
  >>> from zope.app.tests.setup import setUpTraversal
  >>> from zope.app.traversing.interfaces import IPhysicallyLocatable
  >>> from ZODB.tests import util
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

  >>> from versioning.tests.test_versioncontrol import buildRepository, buildDatabaseRoot
  >>> db_root = buildDatabaseRoot()
 
  
  
CopyModifyMergeRepository Setup Explained
-----------------------------------------

In this architecture we can choose between several repositories. We take a
CopyModifyMergeRepository without check in and check out as an example.

First lets configure the various component needed (what 'configure.zcml' 
usually does for us):

  >>> from zope.app.tests import ztapi
  >>> from zope.app import zapi
  >>> from versioning import interfaces, repository, policies, storage

Configure the 'IHistoryStorage' utility being responsible for the storage 
of the objects histories:

  >>> ztapi.provideUtility(interfaces.IHistoryStorage,
  ...                      storage.SimpleHistoryStorage())
  
  >>> histories_storage = zapi.getUtility(interfaces.IHistoryStorage)
  >>> db_root['storage'] = histories_storage

We also need a 'IVersionableAspects' multi adapter beeing responsible
for the versioning policy (what is versioned and how (not storage)).

  >>> ztapi.provideAdapter((interfaces.IVersionable, 
  ...                       interfaces.IHistoryStorage),
  ...                      interfaces.IVersionableAspects,
  ...                      policies.VersionableAspectsAdapter)

Register a 'ICheckoutAware' adapter to a 'IHistoryStorage' that 
handles the checkout/checkin status for the repository.

  >>> ztapi.provideAdapter(interfaces.ICheckoutAware,
  ...                      interfaces.IHistoryStorage,
  ...                      repository.DummyCheckoutAware)

In this implementation the repository is simply a adapter to a 
'IHistoryStorage'. This ensures that several versioning strategies 
can be used with the same storage:

  >>> ztapi.provideAdapter(interfaces.IHistoryStorage,
  ...                      interfaces.ICopyModifyMergeRepository,
  ...                      repository.CopyModifyMergeRepository)

Now we adapt our history storage to the chosen repository strategy:

  >>> repo = interfaces.ICopyModifyMergeRepository(histories_storage)


CopyModifyMergeRepository Usage Explained
-----------------------------------------

An object that isn't 'IVersionable' can't be put under version control.
Applying version control should raise an exception:

  >>> repo.applyVersionControl(a)
  Traceback (most recent call last):
  RepositoryError: This resource cannot be put under version control.

So let us attach marker interfaces to the object before putting them
under version control:

  >>> from versioning.tests.test_versioncontrol import instanceProvides
  >>> instanceProvides(sample, interfaces.IVersionable)
  >>> instanceProvides(a, interfaces.IVersionable)
  >>> instanceProvides(b, interfaces.IVersionable)
  >>> instanceProvides(c, interfaces.IVersionable)

  >>> sample.text = "text version 1 of sample"
  >>> a.text = "text version 1 of a"
  >>> c.text = "text version 1 of a"

The chosen 'IHistoryStorage' component expects the objects having
a '_p_oid'. 
XXX We know this is an implementation detail. We probably should think
more about this and then talk about this in the interfaces.

 
Now let's put our example data under version control:

  >>> repo.applyVersionControl(sample)
  >>> repo.applyVersionControl(a)
  >>> repo.applyVersionControl(b)
  >>> repo.applyVersionControl(c)
  >>> [interfaces.IVersioned.providedBy(x) for x in (sample, a, b, c)]
  [True, True, True, True]

The example data must be now in checked in state:

  #>>> repo.isCheckedOut(sample)
  False
  
Let's have a look how 'checkout', 'checkin' and 'isCheckedOut' work 
together:

  #>>> #repo.checkout(sample)
  #>>> #repo.isCheckedOut(sample)
  True

The text shall be unchanged:

  >>> sample.text
  'text version 1 of sample'

We have a look if the version history grows with a checkin:

  #>>> len(repo.getVersionHistory(sample))
  1
  >>> repo.checkout(sample)
  >>> repo.text = 'text version 2 of sample'
  >>> repo.checkin(sample)
  #>>> len(repo.getVersionHistory(sample))
  2
  >>> 