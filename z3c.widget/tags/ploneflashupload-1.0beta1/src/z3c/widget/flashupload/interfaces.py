from zope import interface
try:
    from zope.component.interfaces import ObjectEvent, IObjectEvent
except ImportError:
    # Legacy Zope 3.2 support
    from zope.app.event.objectevent import ObjectEvent
    from zope.app.event.interfaces import IObjectEvent

class IUploadFileView(interface.Interface):

    """a file upload view"""

class IFlashUploadForm(interface.Interface):

    """Form containing the swf for upload movie"""
    
class IFlashUploadedEvent(IObjectEvent):
    """ Event gets fired when flash uploaded an item """
    
class FlashUploadedEvent(ObjectEvent):
    interface.implements(IFlashUploadedEvent)
    
 
