from zope.app import zapi
from zope.interface import implements

from zope.app.apidoc.viewmodule import browser
from Products.Five.browser import BrowserView 
from Products.Five.utilities.interfaces import IMarkerUtility
from zope.component import getView, ComponentLookupError

class ViewsDetails(browser.ViewsDetails, BrowserView):
    # BBB: wrap ViewsDetails to work in Z2
    """
    set/nci
    """
    def __init__(self, content, request):
        super(ViewsDetails, self).__init__(content, request)

class EditView(BrowserView):

    def __init__(self, context, request):
        self.utility = zapi.getUtility(IMarkerUtility)
        self.context = context
        self.request = request
        self.context_url = self.context.absolute_url()    
    
    def _getLinkToInterfaceDetailsView(self, interfaceName):
        return (self.context_url + 
            '/view_details?iface=%s&type=zope.publisher.interfaces.browser.IBrowserRequest' % interfaceName)

    def _getNameLinkDicts(self, interfaceNames):
        return [dict(name=name,
                     link=self._getLinkToInterfaceDetailsView(name))
                for name in interfaceNames]

    def getAvailableInterfaceNames(self):
        return self._getNameLinkDicts(
            self.utility.getAvailableInterfaceNames(self.context))

    def getDirectlyProvidedNames(self):
        return self._getNameLinkDicts(
            self.utility.getDirectlyProvidedNames(self.context))

    def getProvidedNames(self):
        return self._getNameLinkDicts(
            self.utility.getProvidedNames(self.context))

