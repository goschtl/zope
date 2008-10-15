from zope.interface import Attribute
from zope.component.interfaces import IObjectEvent

class IPostValidationEvent(IObjectEvent):
    """An event which is sent after the ZPublisher request has completed
    traversel and validated the user.
    """

    user = Attribute("The authenticated user")
    request = Attribute("The current request")

