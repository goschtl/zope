from zope.interface import implements
from zope.introspector.interfaces import IRegistryInfo, IRegistrySearch
from zope.component import globalregistry
from zope.interface.adapter import AdapterRegistry
from zope.component.registry import (AdapterRegistration, HandlerRegistration,
                                     UtilityRegistration)
import grokcore.component as grok


class RegistryInfoUtility(grok.GlobalUtility):
    """ Give information about the component registry.
        Implements the IRegistryInfo interface. 
    """
    implements(IRegistryInfo)
    
    def getAllRegistrations(self):
        """ See zope.introspector.interfaces for documentation.
        """
        adapters = self.getAllAdapters()
        handlers = self.getAllHandlers()
        utils = self.getAllUtilities()
        subsriptionAdapters = self.getAllSubscriptionAdapters()
        return adapters + handlers + utils + subsriptionAdapters
        
    def getAllUtilities(self):
        """ See zope.introspector.interfaces for documentation.
        """
        return [x for x in globalregistry.base.registeredUtilities()]
        
    def getAllAdapters(self):
        """ See zope.introspector.interfaces for documentation.
        """
        return [x for x in globalregistry.base.registeredAdapters()]
    
    def getAllHandlers(self):
        """ See zope.introspector.interfaces for documentation.
        """
        return [x for x in globalregistry.base.registeredHandlers()]
    
    def getAllSubscriptionAdapters(self):
        """ See zope.introspector.interfaces for documentation.
        """
        return [x for x in
                globalregistry.base.registeredSubscriptionAdapters()]
    
    def getRegistrationsForInterface(self, searchString='', types=['all']):
        """ See zope.introspector.interfaces for documentation.
        """
        interfaces = []
        searchInterfaces = []
        
        if 'all' in types:
            searchInterfaces = self.getAllRegistrations()
        if 'adapters' in types:
            searchInterfaces.extend(self.getAllAdapters())
        if 'utilities' in types:
            searchInterfaces.extend(self.getAllUtilities())
        if 'handlers' in types:
            searchInterfaces.extend(self.getAllHandlers())
        if 'subscriptionAdapters' in types:
            searchInterfaces.extend(self.getAllSubscriptionAdapters())
        
        #Search using adapters
        for eachRegistration in searchInterfaces:
            if IRegistrySearch(eachRegistration).searchRegistration(
                searchString):
                interfaces.append(eachRegistration)                    
        return interfaces
    
    def getAllInterfaces(self):
        """ See zope.introspector.interfaces for documentation.
        """
        registrations = {}

        for eachRegistration in self.getAllRegistrations():
            reg = IRegistrySearch(eachRegistration)
            interfacePaths = reg.getInterfaces()
            import pprint; 
            #pprint.pprint(interfacePaths)

            for eachInterface in interfacePaths:
                registrations = self._dicter(registrations,
                                             eachInterface.split('.'),
                                             reg.getObject())

        return registrations
    
    def _dicter(self, dictionary, modPath, item):
        
        key = modPath[0]

        if key in dictionary:
            # has key enter that dictionary and continue looking for the end
            if len(modPath) == 1:
                dictionary[key].append(item)
            else:
                self._dicter(dictionary[key], modPath[1:], item)
        else:
            # No key found,
            # create a dictionary and add.
            dictionary[key] = self._createDict(modPath[1:], item)
    
        return dictionary
    
    def _createDict(self, path, item):
        if not path:
            return [item]
        return {path[0]:self._createDict(path[1:], item)}
