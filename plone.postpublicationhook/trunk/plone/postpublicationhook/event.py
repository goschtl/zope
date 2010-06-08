from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from zope.event import notify

from plone.postpublicationhook.interfaces import IAfterPublicationEvent


class AfterPublicationEvent(ObjectEvent):
    implements(IAfterPublicationEvent)

    def __init__(self, context, request):
        super(AfterPublicationEvent, self).__init__(context)
        self.request=request


def redispatch(event):
    """Redispatch IPubBeforeCommit as IAfterPublicationEvent
    """
    request = event.request
    object = request['PUBLISHED']
    notify(AfterPublicationEvent(object, request))
