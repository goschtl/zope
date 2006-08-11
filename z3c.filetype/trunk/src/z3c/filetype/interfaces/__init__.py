from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope import interface

class IFileTypeModifiedEvent(IObjectModifiedEvent):

    """This event is fired when the filetypes change on an object"""


class ITypeableFile(interface.Interface):

    """A file object that is typeable"""

    data = interface.Attribute('Data of the file')
    
    
