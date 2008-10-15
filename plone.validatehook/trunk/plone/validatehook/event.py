from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from plone.validatehook.interfaces import IPostValidationEvent

class PostValidationEvent(ObjectEvent):
    """An event which is fired after the Zope publisher has completed
    traversal and validated a user."""

    implements(IPostValidationEvent)

    def __init__(self, context, request, user):
        super(PostValidationEvent, self).__init__(context)
        self.request=request
        self.user=user

