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

class IVcLoad(Interface):
    def load(checkout, path):
        """Load data in checkout's path into context object.
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
    
class IModified(Interface):
    def modified_since(dt):
        """Return True if the object has been modified since dt.
        """

    def update():
        """Update modification datetime.
        """

class IState(Interface):
    """Information about Python object state.
    """
    root = Attribute('The root container')

    def objects(dt):
        """Objects present in state.

        Not all objects have to be returned. At a minimum, only those
        objects that have been modified or added since dt need to
        be returned.
        """

    def removed(dt):
        """Paths removed.

        Any path that has been removed since dt should be returned. This
        path might have been added again later, so it is safe to return
        paths of objects returned by the 'objects' method.
        """

class ICheckout(Interface):
    """A version control system checkout.
    """
    def sync(state, dt, message=''):
        """Synchronize persistent Python state with remove version control.

        dt is date since when to look for state changes.
        """
        
    def save(state, dt):
        """Save state to filesystem location of checkout.
        """

    def load(object):
        """Load filesystem state of checkout into object.
        """
        
    def up():
        """Update the checkout with the state of the version control system.
        """

    def resolve():
        """Resolve all conflicts that may be in the checkout.
        """

    def commit(message):
        """Commit checkout to version control system.
        """

    def added_by_up():
        """A list of those files that have been added after 'up'.
        """

    def deleted_by_up():
        """A list of those files that have been deleted after 'up'.
        """

    def modified_by_up():
        """A list of those files that have been modified after 'up'.
        """
    
