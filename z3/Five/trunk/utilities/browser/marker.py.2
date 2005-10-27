from zope.app import zapi
from zope.interface import implements, Interface
from zope.app.component.interface import getInterface

from zope.app.apidoc.viewmodule.browser import ViewsDetails as _ViewsDetails
from Products.Five.browser import BrowserView 
from Products.Five.utilities.interfaces import IMarkerUtility
from zope.component import getView, ComponentLookupError

class ViewsDetails(_ViewsDetails, BrowserView):
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
        self.processForm()

        self.name = ''
        if request:
            path = request.environ['PATH_INFO'].split('/')
            self.name = path[-1]

        self.context_url = self.context.absolute_url()

    def add(self):
        return self.request.get('add', ())

    def name(self):
        return self.name
    
    def _getLinkToInterfaceDetailsView(self, interfaceName):
        return (self.context_url + 
            '/views-details.html?iface=%s&type=zope.publisher.interfaces.browser.IBrowserRequest' % interfaceName)

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

    def processForm(self):
        # this could return errors
        ifaces = self.request.get('add', ()), self.request.get('remove', ())
        add, remove = [self.utility.dottedToInterfaces(self.context, seq) for seq in ifaces]
        self.utility.update(self.context, add=add, remove=remove)


