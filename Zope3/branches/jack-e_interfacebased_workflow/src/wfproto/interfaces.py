from zope import interface
from zope.app.event.interfaces import IObjectEvent


class IMyProcess(interface.Interface):
    """ just my process. """

    __processdefinition_name__ = interface.Attribute('temporary helper to find pd')


class IMyStateINITIAL(IMyProcess):
    """ the INITIAL state. """

class IMyStateA(IMyProcess): 
    """ the A state. """

class IMyStateB(IMyProcess):
    """ the B state. """

class IMyStateC(IMyProcess):
    """ the C state. """






class IUserEvent(IObjectEvent):
    """ an informal UserEvent Interface. """


    formData = interface.Attribute('form data')
    method   = interface.Attribute('submit method')

    
