from zope.interface import implements
from Products.Five.browser import BrowserView
from zope.app import zapi

from Products.Five.utilities.interfaces import IMarkerUtility

class MarkerView(BrowserView):
    
    def __init__(self, context, view):
        BrowserView.__init__(self, context, view)
        self.utility = zapi.getUtility(IMarkerUtility)

    def getAvailableInterfaceNames(self):
        
    
