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
used backend generates its own versions."""


   
class IVersionableData(Interface) :
    """ An interface that implements a versioning policy for
        a content type and a storage that knows how to version the
        content data.
    """
           
 
class ITicket(Interface) :
    """ A marker interface for access information for versioned data.
    
        A must provide sufficient information to get back these data.  
        A ticket is created when some versionable data have been accepted 
        and successfully stored in the repository.
    
        XXX: Special case IDelayedTicket for asynchronous storages needed?
      
    """

class IHistoryStorage(Interface) :
    """ Minimal interface for a pluggable storage that stores a new version
    of an object into an object history.
    """

    def register(obj) :
        """ Puts some object under version control. Returns an ITicket
        to the first version.
        """
    
    def write(obj) :
        """ Saves a new version in the repository and returns an ITicket.
        
        Raises a VersionControlError if something went wrong.
        """
    
    def read(ticket) :
        """ Reads a version from the repository that is specified by the ticket.
        
        Raises a VersionPermanentlyDeleted exception if the repository
        allowed to delete the specified version.
        
        VersionNotAvailable error if something went wrong 
        """
       
   
class IPythonReferenceStorage :
    """ Marker interface for a storage that is able to preserve 
        python references and thus is able to accept originals.
    
        A minimal implementation would only ensure that versioned originals
        are referenced and thus protected against sweep out in ZODB
        packs.
    """


   
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


# XXX describe Event types here


