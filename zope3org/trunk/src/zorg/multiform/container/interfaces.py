from zope.app.location.interfaces import ILocation
from zope import schema
from zope.interface import Interface, Attribute

class IMovableLocation(ILocation):

    """a located object that can change its __name__ attribute by
    itself"""

    __name__ = schema.TextLine(
        title=u"The name within the parent",
        description=u"Traverse the parent with this name to get the object.",
        required=False,
        default=None)

