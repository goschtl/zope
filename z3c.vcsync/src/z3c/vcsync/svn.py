import py

from z3c.vcsync.vc import CheckoutBase

class SvnCheckout(CheckoutBase):
    """A checkout for SVN.

    This is a simplistic implementation. Advanced implementations
    might check what has been changed in an SVN update and change the
    load() method to only bother to load changed (or added or removed)
    data. Similarly save() could be adjusted to only save changed
    data.
    
    It is assumed to be initialized with py.path.svnwc
    """
    
    def up(self):
        self.path.update()

    def resolve(self):
        pass

    def commit(self, message):
        self.path.commit(message)
