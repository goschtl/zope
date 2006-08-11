from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope import interface, component
import interfaces
import api

class FileTypeModifiedEvent(ObjectModifiedEvent):
    interface.implements(interfaces.IFileTypeModifiedEvent)


@component.adapter(interfaces.ITypeableFile,IObjectModifiedEvent)
def handleModified(typeableFile, event):
    """handles modification of data"""
    #import pdb;pdb.set_trace()
    if interfaces.IFileTypeModifiedEvent.providedBy(event):
        # do nothing if this is already a filetype modification event
        return
    api.applyInterfaces(typeableFile)
    
