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
  >>> new_c = accessVersion(repository, c)
  >>> new_c.refers_to == new_a
  False
  
This demonstrates that the reference to a is not correctly preserved. To
achieve this goal we overwrite some methods :

  >>> class RefertialVersionControl(Repository) : 
  ...   # an implementation that preprocesses the object states
  ...
  ...   def applyVersionControl(self, object, message) :
  ...       obj = self.preprocess(object)
  ...       super(RefertialVersionControl, self).applyVersionControl(obj, message)
  ...
  ...   def getVersionOfResource(self, history_id, branch) :
  ...       obj = super(RefertialVersionControl, self).getVersionOfResource(history_id, branch)
  ...       return self.postprocess(obj)
  ...
  ...   def preprocess(self, obj) :
  ...       # We replace python references by unique ids
  ...       
  
  >>> repository2 = buildRepository(RefertialVersionControl)
  >>> repository2.applyVersionControl(sample)
  >>> repository2.applyVersionControl(a)
  >>> repository2.applyVersionControl(b)
  >>> repository2.applyVersionControl(c)
  
  

  >>> new_a = accessVersion(repository2, a)
  >>> new_c = accessVersion(repository2, c)
  >>> new_c.refers_to == new_a
  True
  





Extensions: We want to define a repository that works as a black box and returns
only a ticket which guarantees that we get a valid copy back if we use this ticket.

class IRepository(Interface) :

    def register(self, obj) :
        """ Returns an ITicket. """
        
    def retrieve(self, ticket) :
        """ Returns an object or throws an ObjectNotFound 
            or ObjectPermanentylDeleted exception.
        """
    
We want to use versioning with object other than standard zope objects that use
only the standard containment structure meachanism.



