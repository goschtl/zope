from zope.lifecycleevent import ObjectModifiedEvent
from zope import interface
import interfaces

class FileTypeModifiedEvent(ObjectModifiedEvent):
    interface.implements(interfaces.IFileTypeModifiedEvent)

