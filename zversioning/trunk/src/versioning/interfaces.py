"""  Whether the versioning scheme uses the existing ZODB or some
other versioning system like CVS or Subversion as a subsystem
should be configurable.  How the repository stores the data, 
whether it is able to version metadata or only content, 
whether it uses revision numbers for commits
(like Subversion) or document specific version numbers (like CVS)
may thus vary.        
               
Therefore we use a ticket mechanism, which means that
the versioning repository takes any versionable data (not necessarily
the original object), stores them whereever it likes and gives
back arbitrary access information (a path, a global unique id) which
is sufficient to guarantee that the provided versionable data
can be retrieved.

It's the responsibility of the clients to bookkeep this access information 
or tickets. The inner structure of these tickets cannot be
determined in advance. We therefore propose only a marker interface
for this.
    
To abstract from the access is simple, more difficult
is the question, what happens if the used repository allows 
to generate new version independently from Zope.
For instance, if someone uses Subversion
as a backend for versioning, numerous other clients can access 
the versioned contents and commit changes, if they are allowed.

The important distinction here is that some repositories
are passive and only wait for versions that were created in Zope.
Other versioning system may create their own versions of objects
which must be recognized and be read into Zope. In this case
there must be a mechanism that informs the involved Zope
objects about new versions. We propose to use the Zope event system 
to allow versionable objects to subscribe to new versions if the
used backend generates its own versions.
"""

class IRepository(Interface):
    """A version repository providing core functionality.
    
    IRepository is a kind of abstract component as the most important
    functionality of storing versions of object is not implemented
    here.
    
    See other repository interfaces defining different access strategies.

    As long you have at least one object from your versioned
    object cloud you can reach every object from it (at least the 
    versioned aspects). XXX After having deleted the last object 
    the IHistoryStorage component has to be asked for a bootstrap
    object.
    """
    
    def applyVersionControl(obj):
        """Put the an object under version control.
            
        This method has to be call prior using any other repository
        related methods.
        """
    
    def revertToVersion(obj, selector):
        """Reverts the object to the selected version.
        
        XXX Do we need to say something about branches?
        """
        

class ICopyModifyMergeRepository(IRepository):
    """Top level API for a copy-modify-merge (subversion like) repository.
    """
    
    def saveAsVersion(obj):
        """Save the current state of the object for later retreival.
        """

class ICheckoutCheckinRepository(IRepository):
    """Top level API for a checkout-modify-checkin (XXX DeltaV like) repository.
    
    These kind of repositories administrate an "object is in use" 
    information which may be suitable in some environments.
    
    It my be seen as kind of soft locks.
    """

    def checkout(obj):
        """Marks the object as checked out (being in use somehow).
        """
    
    def checkin(obj):
        """Check in the current state of an object.
        
        Raises an RepositoryError if the object is not versionable.
        XXX Other exceptions (for repository problems)?
        """


class IHardlockUnlockRepository(ICheckoutCheckinRepository):
    """Top level API for a lock-modify-unlock repository.
    
    These kind of repositories also manage a lock state to avoid
    editing collisions.
    
    XXX This interface may be unstable as we didn't think a lot about 
    it.
    """


class IIntrospectableRepository(Interface):
    """Additional methods providing more information versioned objects.
    """

    def getVersion(obj, selector): # XXX Naming: getCopyOfVersion
        """Returns the selected version of an object. 
        
        This method does not overwrite 'obj' (like revertToVersion
        does). Instead it returns the version as new object.
        """

    def getVersionIds(self, obj)
        """Returns references to all versions of the passed object.
        
        XXX Naming: Should we name that 'listVersions' just returning
        references to the objects?
        """


class ICheckoutAware(Interfaces):
    """Marking objects as checked in or checked out.
    
    XXX Naming conventions? Aren't IBlahAware interfaces usually marker 
    interfaces?
    XXX IUsageTrackingAware?, IInUseMarkingAware, ISoftLockingAware
    """
    
    def markAsCheckedIn(obj):
        """Marks the object as being checked in.
        """
        
    def markAsCheckedOut(obj):
        """Marks the object as being checked out.
        """

   
class IVersionableAspects(Interface) :
    """ An interface that implements a versioning policy for
        a content type and a storage that knows how to version the
        content data.
        
        XXX VersionableData vermittelt zwischen den Daten und der Storage, 
        was gespeichert werden soll
        
        XXX Explain that this is a multidapter?
    """

    def updateAspects(selector):
        """Updates a certain aspect on the original object.
        
        XXX exceptions?
        XXX Should reading only certain parts of an aspect be possible?
        """
    
    def writeAspects():
        """Write an aspect from the original object.
        """
 
class ITicket(Interface) :
    """ A marker interface for access information for versioned data.
    
        A must provide sufficient information to get back these data.  
        A ticket is created when some versionable data have been accepted 
        and successfully stored in the repository.
    
        XXX: Special case IDelayedTicket for asynchronous storages needed?
      
    """


# XXX 
class IHistoryStorage(Interface) : # IHistories
    """ Minimal interface for a pluggable storage that stores a new version
    of an object into an object history.
    
    XXX Important note: IHistoryStorage components must be transaction aware.
    A CVSHistoryStorage component for example has to ensure to handle 
    transactions.
    
    IHistoryStorage components store IVersionableAspects of objects.
    """

    def createVersionHistory(obj) :
        """ Puts some object under version control. Returns an IHistory.
        
        XXX YAGNI?
        """
    
    def getObject
    
    def getVersion(history, selector):
        """
        """
   
class IPythonReferenceStorage :
    """ Marker interface for a storage that is able to preserve 
        python references and thus is able to accept originals.
    
        A minimal implementation would only ensure that versioned originals
        are referenced and thus protected against sweep out in ZODB
        packs.
    """

class IVersionable(persistent.interfaces.IPersistent):
    """Version control is allowed for objects that provide this."""

class IDeletableStorage(IStorage) :
    """ Most versioning systems do not allow to throw away versioned
    data, but there might be use cases were simple file repositories
    or other storage solutions can sweep out old versions. """

    def delete(obj, ticket) :
        """ Forces the repository to remove the version described by the ticket.
        
            Raises a VersionUndeletable error if the repository does not
            allow deletions or something other went wrong.
        """

   
class IMultiClientStorage(Interface) : 
    """ if the repository allows several ways to
    create versions and not only reacts to Zope calls.
    """

    def triggerEvents(ticket=None) :
        """ Induce the repository to activate events, 
        i.e. descriptions of changes that allow the application 
        to decide whether the zope database must be updated or not.
        
        If ticket is specified only the changes of the 
        referenced object should be described.
        
        If ticket is None all changes should be described.   
        """


class IVersionable(persistent.interfaces.IPersistent,
                   zope.app.annotation.interfaces.IAnnotatable):
    """Version control is allowed for objects that provide this."""

class INonVersionable(zope.interface.Interface):
    """Version control is not allowed for objects that provide this.
    
    XXX Do we need that? Is this YAGNI?
    """

class IVersioned(IVersionable):
    """Version control is in effect for this object."""


# XXX describe Event types here


