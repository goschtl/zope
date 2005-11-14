import zope.interface
from buddydemo.interfaces import IPostalInfo, IPostalLookup

class Info:
    """Postal information

    >>> info = Info('Cleveland', 'Ohio')
    >>> info.city, info.state
    ('Cleveland', 'Ohio')
    """

    zope.interface.implements(IPostalInfo)

    def __init__(self, city, state):
        self.city, self.state = city, state

class Lookup:

    zope.interface.implements(IPostalLookup)
    
    _data = {
        '22401': ('Fredericksburg', 'Virginia'),
        '44870': ('Sandusky', 'Ohio'),
        '90051': ('Los Angeles', 'California'),
        }

    def lookup(self, postal_code):
        """Lookup city and state information

        If a known postal code is used, we get data:

          >>> lookup = Lookup()
          >>> info = lookup.lookup('22401')
          >>> info.city, info.state
          ('Fredericksburg', 'Virginia')

        But get nothing if an unknown code is given:

          >>> lookup.lookup('11111')
        """
        data = self._data.get(postal_code)
        if data:
            return Info(*data)
