from zope import schema
from zope.interface import Interface, Attribute
from zope.location.interfaces import ILocation


class IMovableLocation(ILocation):

    """a located object that can change its __name__ attribute by
    itself"""

    __name__ = schema.TextLine(
        title=u"Name",
        description=u"Traverse the parent with this name to get the object.",
        required=False,
        default=None)

