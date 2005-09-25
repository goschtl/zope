from zope.interface import implements
from Products.Five.browser import BrowserView
from zope.app import zapi

from Products.Five.utilities.interfaces import IMarkerUtility

class MarkerView(BrowserView):
    
    def __init__(self, context, view):
        BrowserView.__init__(self, context, view)
        self.utility = zapi.getUtility(IMarkerUtility)
        self.context_url = self.context.absolute_url()

    
    def _getLinkToInterfaceDetailsView(interfaceName):
        return self.context_url + 
            '/view_details?iface=%s&type=zope.publisher.interfaces.browser.IBrowserRequest' % interfaceName

    def _getNameLinkTuples(interfaceNames):
        return [{'name':name,
                 'link':self._getLinkToInterfaceDetailsView(name)}
                for name in interfaceNames]

    def getAvailableInterfaceNames(self):
        return self._getNameLinkTuples(
            self.utility.getAvailableInterfaceNames(self.context))

    def getDirectlyProvidedNames(self):
        return self._getNameLinkTuples(
            self.utility.getDirectlyProvidedNames(self.context))

    def getProvidedNames(self):
        return self._getNameLinkTuples(
            self.utility.getProvidedNames(self.context))

