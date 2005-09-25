from zope.interface import implements
from Products.Five.browser import BrowserView
from zope.app import zapi

from Products.Five.utilities.interfaces import IMarkerUtility

class MarkerView(BrowserView):
    
    def __init__(self, context, view):
        BrowserView.__init__(self, context, view)
        self.utility = zapi.getUtility(IMarkerUtility)

    def getAvailableInterfaceNames(self):
        return self.utility.getAvailableInterfaceNames(self.context) 

    def getDirectlyProvidedNames(self):
        return self.utility.getDirectlyProvidedNames(self.context) 

    def getProvidedNames(self):
        return self.utility.getProvidedNames(self.context) 
