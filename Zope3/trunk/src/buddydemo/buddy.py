import persistent
import zope.interface
from buddydemo.interfaces import IBuddy
from buddydemo.interfaces import IPostalLookup, IPostalInfo
from buddydemo.interfaces import IBuddyContained
from zope.app import zapi

class Buddy(persistent.Persistent):
    """Buddy information

    >>> bud = Buddy('Bob', 'Smith', 'bob@smith.org',
    ...             '513 Princess Ann Street', '22401')
    >>> bud.first, bud.last, bud.email
    ('Bob', 'Smith', 'bob@smith.org')
    >>> bud.address, bud.postal_code
    ('513 Princess Ann Street', '22401')

    Any data not passed to the class are initialized to
    empty strings:

    >>> bud = Buddy()
    >>> bud.first, bud.last, bud.email
    ('', '', '')
    >>> bud.address, bud.postal_code
    ('', '')
    """

    zope.interface.implements(IBuddy, IBuddyContained)

    __parent__ = __name__ = None

    def __init__(self, first='', last='', email='',
                 address='', pc=''):
        self.first, self.last = first, last
        self.email = email
        self.address, self.postal_code = address, pc

    def name(self):
        """Get the full name of a buddy

        >>> bud = Buddy('Bob', 'Smith')
        >>> bud.name()
        'Bob Smith'
        """
        return "%s %s" % (self.first, self.last)

from zope.app.container.btree import BTreeContainer
from buddydemo.interfaces import IBuddyFolder

class BuddyFolder(BTreeContainer):
    zope.interface.implements(IBuddyFolder)




class BuddyCityState:
    """Provide city and state information for a buddy

    The adapter needs a postal-lookup utility.  For the
    sake of the example, we'll install one, but first,
    we have to set up the component architecture:

      >>> from zope.app.tests import placelesssetup, ztapi
      >>> placelesssetup.setUp()

    and then we can provide the utility:

      >>> from stubpostal import Lookup
      >>> ztapi.provideUtility(IPostalLookup, Lookup())

    Now, we can try our adapter.  If we have no postal
    code, we get no data:

      >>> bob = Buddy('Bob')
      >>> info = BuddyCityState(bob)
      >>> info.city, info.state
      ('', '')

    But if we use a known postal code:

      >>> bob = Buddy('Bob', '', '', '', '22401')
      >>> info = BuddyCityState(bob)
      >>> info.city, info.state
      ('Fredericksburg', 'Virginia')

    Finally, we'll put things back the way we found them:

      >>> placelesssetup.tearDown()

    """

    zope.interface.implements(IPostalInfo)

    __used_for__ = IBuddy

    def __init__(self, buddy):
        lookup = zapi.getUtility(buddy, IPostalLookup)
        info = lookup.lookup(buddy.postal_code)
        if info is None:
            self.city, self.state = '', ''
        else:
            self.city, self.state = info.city, info.state
        
