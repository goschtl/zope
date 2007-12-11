from zope.interface import Interface, Attribute

class IVcDump(Interface):
    def save(checkout, path):
        """Save context object to path in checkout.

        checkout - an ICheckout object
        path - a py.path object referring to directory to save in.

        This might result in the creation of a new file or directory under
        the path, or alternatively to the modification of an existing file
        or directory.

        Returns the path just created.
        """

class ISerializer(Interface):
    def serialize(f):
        """Serialize object to file object.
        """

class IParser(Interface):
    def parse(f):
        """Parse object and load it into new object, returning it.
        """

    def parse_into(f):
        """Parse object and replace current object's content with it.
        """

class IVcFactory(Interface):
    def __call__():
        """Create new instance of object.
        """

class ISynchronizer(Interface):
    """Synchronizer between state and version control.
    """
    checkout = Attribute('Version control system checkout')
    state = Attribute('Persistent state')
    
    def sync(revision_nr, message=''):
        """Synchronize persistent Python state with version control system.

        revision_nr - Revision number since when we want to synchronize.
             Revision number are assumed to increment over time as new
             revisions are made (through synchronisation). It is
             possible to identify changes to both the checkout as well
             as the ZODB by this revision number.  Normally a version
             control system such as SVN controls these.
        message - message to commit any version control changes.

        Returns a ISynchronizationInfo object with a report of the
        synchronization, including the new revision number after 
        synchronization.
        """
        
    def save(revision_nr):
        """Save state to filesystem location of checkout.

        revision_nr - revision_nr since when there have been state changes.
        """

    def load(revision_nr):
        """Load the filesystem information into persistent state.

        revision_nr - revision_nr after which to look for filesystem changes.
        """
    
class ICheckout(Interface):
    """A version control system checkout.
    """        
    path = Attribute('Path to checkout root')

    def up():
        """Update the checkout with the state of the version control system.
        """

    def revision_nr():
        """Current revision number of the checkout.
        """
        
    def resolve():
        """Resolve all conflicts that may be in the checkout.
        """

    def commit(message):
        """Commit checkout to version control system.
        """

    def files(revision_nr):
        """Files added/modified in state since revision_nr.

        Returns paths to files that were added/modified since revision_nr.
        """

    def removed(revision_nr):
        """Files removed in state since revision_nr.

        Returns filesystem (py) paths to files that were removed.
        """

class IState(Interface):
    """Information about Python object state.
    """
    root = Attribute('The root container')

    def objects(revision_nr):
        """Objects modified/added in state since revision_nr.

        Ideally, only those objects that have been modified or added
        since the synchronisation marked by revision_nr should be
        returned. Returning more objects (as long as they exist) is
        safe, however, though less efficient.
        """

    def removed(revision_nr):
        """Paths removed since revision_nr.

        The path is a path from the state root object to the actual
        object that was removed. It is therefore not the same as the
        physically locatable path. These paths always use the forward
        slash as the seperator, and thus are not subject to os.path.sep
        like filesystem paths are.

        Ideally, only those paths that have been removed since the
        synchronisation marked by revision_nr should be returned. It
        is safe to return paths that were added again later, so it is
        safe to return paths of objects returned by the 'objects'
        method.
        """

class ISynchronizationInfo(Interface):
    """Information on what happened during a synchronization.
    """

    revision_nr = Attribute("""
    The revision number of the version control system that
    we have synchronized with.
    """)
    
    def objects_removed():
        """Paths of objects removed in synchronization.

        The paths are state internal paths.
        """
        
    def objects_changed():
        """Paths of objects added or changed in synchronization.

        The paths are state internal paths.
        """

    def files_removed():
        """Paths of files removed in synchronization.

        The paths are filesystem paths (py.path objects)
        """

    def files_changed():
        """The paths of files added or changed in synchronization.

        The paths are filesystem paths (py.path objects)
        """
