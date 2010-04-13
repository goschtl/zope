import zope.interface
import zope.traversing.interfaces

from zope.location.location import Location

class TLocation(Location):
    """Simple traversable location used in examples."""

    zope.interface.implements(zope.traversing.interfaces.ITraverser)

    def traverse(self, path, default=None, request=None):
        o = self
        for name in path.split(u'/'):
           o = getattr(o, name)
        return o
