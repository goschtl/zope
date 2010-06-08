from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute


class IAfterPublicationEvent(IObjectEvent):
    """An event which is fired after publication, but before the transaction is
    commited."""

    request = Attribute("The request")
