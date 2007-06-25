from zope.interface import Interface

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

class ICheckout(Interface):
    """A version control system checkout.
    """
    def sync(object, message=''):
        """Synchronize persistent Python state with remove version control.
        """
        
    def save(object):
        """Save root object to filesystem location of checkout.
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

    def add(path):
        """Add a file to the checkout (so it gets committed).
        """

    def delete(path):
        """Delete a file from the checkout (so the delete gets committed).
        """

    def added_by_save():
        """A list of files and directories that have been added by a save.
        """

    def deleted_by_save():
        """A list of files and directories that have been deleted by a save.
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
    
