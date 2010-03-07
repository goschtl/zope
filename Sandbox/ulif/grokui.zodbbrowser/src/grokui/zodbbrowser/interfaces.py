"""grokui.zodbbrowser interfaces.
"""
from zope import schema
from zope.interface import Interface

class IObjectInfo(Interface):
    """Infos about a ZODB object.
    """
    oid = schema.Int(
        title = u"ZODB object ID of an object",
        required = False,
        )

    name = schema.TextLine(
        title = u"Name of an object or '???'",
        required = True,
        )

    parent = schema.Object(
        schema = Interface,
        title = u"Parent of an object. Can be of arbitrary type.",
        required = False,
        )
    
    def getMembers():
        """Get a list of object infos for all members of an object.
        """

