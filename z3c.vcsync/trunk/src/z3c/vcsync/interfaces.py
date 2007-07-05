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
    
    def sync(dt, message=''):
        """Synchronize persistent Python state with version control system.

        dt - date since when to look for state changes
        message - message to commit any version control changes.
        """

    def save(dt):
        """Save state to filesystem location of checkout.

        dt - timestamp after which to look for state changes.
        """

    def load(dt):
        """Load the filesystem information into persistent state.

        dt - timestamp after which to look for filesystem changes.
        """
    
class ICheckout(Interface):
    """A version control system checkout.
    """        
    path = Attribute('Path to checkout root')

    def up():
        """Update the checkout with the state of the version control system.
        """

    def resolve():
        """Resolve all conflicts that may be in the checkout.
        """

    def commit(message):
        """Commit checkout to version control system.
        """

    def files(dt):
        """Files added/modified in state since dt.

        Returns paths to files that were added/modified since dt.
        """

    def removed(dt):
        """Files removed in state since dt.

        Returns filesystem (py) paths to files that were removed.
        """

class IState(Interface):
    """Information about Python object state.
    """
    root = Attribute('The root container')

    def objects(dt):
        """Objects modified/added in state since dt.

        Ideally, only those objects that have been modified or added
        since dt should be returned. Returning more objects (as long
        as they exist) is safe, however, though less efficient.
        """

    def removed(dt):
        """Paths removed since dt.

        The path is a path from the state root object to the actual
        object that was removed. It is therefore not the same as the
        physically locatable path.

        Ideally, only those paths that have been removed since dt
        should be returned. It is safe to return paths that were added
        again later, so it is safe to return paths of objects returned
        by the 'objects' method.
        """

