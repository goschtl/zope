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
  
as well as the reference from c to a is defunct :
  
  >>> new_c.refers_to == new_a
  False
  
A closer look reveals that

  >>> new_c         # doctest: +ELLIPSIS
  <zope.app.versioncontrol.README.TestFolder object at ...>

  
This demonstrates that the reference to a is not correctly preserved. To
achieve this goal we overwrite the copy process with our own:

    
  >>> def cloneByPickle(obj, repository, ignore_list=()):
  ...     """Makes a copy of a ZODB object, loading ghosts as needed.
  ...      
  ...     Ignores specified objects along the way, replacing them with None
  ...     in the copy.
  ...     """
  ...     ignore_dict = {}
  ...     for o in ignore_list:
  ...         ignore_dict[id(o)] = o
  ...     ids = {"ignored": object()}
  ...     
  ...     def persistent_id(ob):
  ...         if ignore_dict.has_key(id(ob)):
  ...             return 'ignored'
  ...         if IVersionable.providedBy(object) :
  ...             if IVersioned.providedBy(object) :
  ...                myid = repository.getExistingTicket(object)
  ...             else :
  ...                myid = repository.getNewTicket(object)
  ...            
  ...             ids[myid] = ob
  ...             return myid
  ...         if getattr(ob, '_p_changed', 0) is None:
  ...             ob._p_changed = 0
  ...         return None
  ...     
  ...     stream = StringIO()
  ...     p = Pickler(stream, 1)
  ...     p.persistent_id = persistent_id
  ...     p.dump(obj)
  ...     stream.seek(0)
  ...     u = Unpickler(stream)
  ...     u.persistent_load = ids.get
  ...     return u.load()

  >>> VERSION_INFO_KEY = "gaga.at.isarsprint"
  >>> from zope.app.versioncontrol.repository import Repository
  >>> from zope.app.uniqueid import UniqueIdUtility
  >>> class RefertialVersionControl(Repository) : 
  ...   # an implementation that preprocesses the object states
  ...
  ...   tickets = UniqueIdUtility()
  ...
  ...   def getExistingTicket(self, object) :
  ...       IAnnotations(object)[VERSION_INFO_KEY]
  ...
  ...   def getNewTicket(self, object) :
  ...       id = self.tickets.register(object)
  ...       IAnnotations(object)[VERSION_INFO_KEY] = id
  ...       return id
  ...
  ...   def applyVersionControl(self, object, message=None) :
  ...       obj = self.preprocess(object)
  ...       super(RefertialVersionControl, self).applyVersionControl(obj, message)
  ...
  ...   def getVersionOfResource(self, history_id, branch) :
  ...       obj = super(RefertialVersionControl, self).getVersionOfResource(history_id, branch)
  ...       return self.postprocess(obj)
  ...
  ...   def preprocess(self, obj) :
  ...       # We replace python references by unique ids
  ...       return obj.cloneByPickle()
  ...
  ...   def postprocess(self, obj) :
  ...       return obj   
  
  >>> def declare_unversioned(object):
  ...   # remove object from version controll
  ...   ifaces = zope.interface.directlyProvidedBy(object)
  ...   ifaces -= IVersioned
  ...   zope.interface.directlyProvides(object, *ifaces)
    
  >>> declare_unversioned(sample)
  >>> declare_unversioned(a)
  >>> declare_unversioned(b)
  >>> declare_unversioned(c)
  >>> repository2 = buildRepository(RefertialVersionControl, interaction=False)
  >>> repository2.applyVersionControl(sample)
  >>> repository2.applyVersionControl(a)
  >>> repository2.applyVersionControl(b)
  >>> repository2.applyVersionControl(c)
  
 
  >>> new_a = accessVersion(repository2, a)
  >>> new_b = accessVersion(repository2, b)
  >>> new_c = accessVersion(repository2, c)
  
  Now the reference from b to c is intact:
  >>> new_b["c"] == new_c
  False
  >>> new_c.refers_to == new_a
  False
  





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



