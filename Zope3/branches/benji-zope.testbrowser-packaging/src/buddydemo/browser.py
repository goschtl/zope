import zope.interface
from buddydemo.interfaces import IBuddy, IPostalInfo
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent

class BuddyInfo:
    """Provide an interface for viewing a Buddy
    """

    zope.interface.implements(IPostalInfo)
    __used_for__ = IBuddy

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        info = IPostalInfo(context)
        self.city, self.state = info.city, info.state

class BuddyRename:
    """Rename a buddy"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self, first, last):
        self.context.first = first
        self.context.last = last
        notify(ObjectModifiedEvent(self.context))
        self.request.response.redirect("rename.html")

        
