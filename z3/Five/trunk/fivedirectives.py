from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens

class IImplementsDirective(Interface):
    """State that a class implements something.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

    interface = Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=GlobalObject()
        )

class IViewableDirective(Interface):
    """State that a class can be viewed.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

