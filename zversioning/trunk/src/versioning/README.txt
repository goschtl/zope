==========
Versioning
==========

Versioning means different things to different people and there is no common optimal 
solution for all the problems that are related to the history of evolving data.
Therefore we want to provide a flexible framework that is pluggable in its
most important parts and reduces the problem of different versioning schemes
to a few reusable patterns. These patterns as we conceive them are implemented 
in versioning.repository.

The main API is defined in versioning.interfaces.IVersionControl.

The pattern common to all implementation variants is roughly as follows:

    1.  Versioning can only be applied to a set of objects
        if the objects have been registered and have been accepted
        by the versioning system (or more precisely the version history storage).
        
    2.  Creating a version means that the original object is copied into
        a storage that defines the evolving history of this object by means
        of a succession of replicated data.
            
        What excactly is meant by a copy is a matter of the use case and not
        prescribed by the framework. Some storages may be able to store metadata,
        others only content data, sometimes one wants complete replicas, sometimes
        only some important aspects of an object etc.
        
        A few simple examples can be found in policies.py. The implementation of 
        more complex variants is left as an exercise to the reader.
        
    3.  Reverting to a version means that the saved state of an object is somehow
        reconstructed in the present context. For some contexts a substitution
        of the original with a saved copy is sufficient, sometimes references
        to the original objects must remain intact. These different variants
        are also defined in policies.py
        
Within this overall pattern the following components are pluggable :

    1.  IHistoriesStorage. This is the main persistent storage that is used
        to ensure that the changing versions can be accessed later on. 
        We use the abstract term ticket to describe the fact that different
        storages use quite different reference schemes, e.g. global unique ids,
        paths and revision numbers, python pointers, the _p_oid in the ZODB etc.
        to retrieve and access parts of the history of an object.
        
    2.  IVersionableAspects. 
    
   
    3.  INameChooser.
    
    
    4.  ICheckoutAware.
    
    XXX
    
    5.  IMergeStrategies 
    
    
    
        
    
         

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
  >>> from versioning.tests.test_versioncontrol import buildRepository, buildDatabaseRoot
  >>> db_root = buildDatabaseRoot()

  >>> class TestFolder(Folder) :
  ...   zope.interface.implements(IPhysicallyLocatable)
  ...   def getPath(self) :
  ...       return ""
  >>> sample = TestFolder()
  >>> directlyProvides(sample, zope.app.traversing.interfaces.IContainmentRoot)
  >>> db_root['sample'] = sample

  >>> a = sample["a"] = TestFolder()
  >>> b = sample["b"] = TestFolder()
  >>> c = b["c"] = TestFolder()
  >>> for x in (sample, a, b, c) :
  ...     directlyProvides(x, zope.app.versioncontrol.interfaces.IVersionable)
  >>> [x for x in sample.keys()]
  [u'a', u'b']

The chosen 'IHistoryStorage' component expects the objects having
a '_p_oid'. 
XXX We know this is an implementation detail. We probably should think
more about this and then talk about this in the interfaces.

  >>> util.commit()


Setting up a ICheckoutCheckinRepository
---------------------------------------

In this architecture we can choose between several repositories. We take a
CopyModifyMergeRepository without check in and check out as an example.

First lets configure the various component needed (what 'configure.zcml' 
usually does for us):

  >>> from zope.app.tests import ztapi
  >>> from zope.app import zapi
  >>> import persistent
  >>> from versioning import interfaces, repository, policies, storage

  
Configure a unique id utility. In this case we use the one provided by
zope and enable this utility to adapt all persistent object into
unique references:     

  >>> ztapi.provideUtility(zope.app.uniqueid.interfaces.IUniqueIdUtility,
  ...                           zope.app.uniqueid.UniqueIdUtility())
  >>> ztapi.provideAdapter(persistent.interfaces.IPersistent, 
  ...                           zope.app.uniqueid.interfaces.IReference,
  ...                           zope.app.uniqueid.ReferenceToPersistent)    

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

  >>> ztapi.provideAdapter(interfaces.IHistoryStorage,
  ...                      interfaces.ICheckoutAware,
  ...                      storage.DefaultCheckoutAware)

In this implementation the repository is simply a adapter to a 
'IHistoryStorage'. This ensures that several versioning strategies 
can be used with the same storage:

  >>> ztapi.provideAdapter(interfaces.IHistoryStorage,
  ...                      interfaces.ICopyModifyMergeRepository,
  ...                      repository.CheckoutCheckinRepository)

  >>> ztapi.provideAdapter(None,
  ...                      interfaces.IVersion,
  ...                      storage.Version)


Now we adapt our history storage to the chosen repository strategy:

  >>> repo = interfaces.ICopyModifyMergeRepository(histories_storage)


Useing the ICheckoutCheckinRepository
-------------------------------------

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

Now let's put our example data under version control:

  >>> repo.applyVersionControl(sample)
  >>> repo.applyVersionControl(a)
  >>> repo.applyVersionControl(b)
  >>> repo.applyVersionControl(c)
  >>> [interfaces.IVersioned.providedBy(x) for x in (sample, a, b, c)]
  [True, True, True, True]

The example data must be now in checked in state:

  >>> repo.isCheckedOut(sample)
  False
  
Let's have a look how 'checkout', 'checkin' and 'isCheckedOut' work 
together:

  >>> repo.checkout(sample)
  >>> repo.isCheckedOut(sample)
  True

The text shall be unchanged:

  >>> sample.text
  'text version 1 of sample'

We have a look if the version history grows with a checkin:

  >>> len(repo.listVersions(sample))
  1
  >>> repo.checkout(sample)
  >>> sample.text = 'text version 2 of sample'
  >>> repo.checkin(sample)
  >>> sample.text
  'text version 2 of sample'

  #>>> repo.revertToVersion(sample, u'001')
  #>>> db_root['sample'].text
  'text version 1 of sample'
  #>>> sample.text
  'text version 1 of sample'
  
  >>> len(repo.listVersions(sample))
  2

  >>> [v.label for v in repo.listVersions(sample)]
  [u'001', u'002']

  >>> [v.name for v in repo.listVersions(sample)]
  ['Version 1', 'Version 2']
