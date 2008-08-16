##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Collect infos about global and local registries and their content.
"""

from zope.interface import implements
from zope.introspector.interfaces import IRegistryInfo, IRegistrySearch
from zope.component import globalregistry, getSiteManager
from zope.interface.adapter import AdapterRegistry
from zope.component.registry import (AdapterRegistration, 
                                     HandlerRegistration,
                                     UtilityRegistration)
import grokcore.component as grok


class RegistryInfoUtility(grok.GlobalUtility):
    """ Give information about the component registry.
        Implements the IRegistryInfo interface. 
    """
    implements(IRegistryInfo)
    context = None

    def getAllRegistrations(self, registry='base'):
        """ See zope.introspector.interfaces for documentation.
        """
        adapters = self.getAllAdapters(registry)
        handlers = self.getAllHandlers(registry)
        utils = self.getAllUtilities(registry)
        subsriptionAdapters = self.getAllSubscriptionAdapters(registry)
        return adapters + handlers + utils + subsriptionAdapters

    def getAllUtilities(self, registry=None, context=None):
        contxt = context or self.context
        smlist = [getSiteManager(context)]
        seen = []
        result = []
        while smlist:
            sm = smlist.pop()
            if sm in seen:
                continue
            seen.append(sm)
            smlist += list(sm.__bases__)
            for u in sm.registeredUtilities():
                if registry and not (registry == u.registry.__name__):
                    continue
                result.append(u)
        return result

    def getAllAdapters(self, registry='base'):
        """ See zope.introspector.interfaces for documentation.
        """
        def f(item):
            return registry is getattr(item.registry, '__name__')
        
        return filter(f, globalregistry.base.registeredAdapters())
    
    def getAllHandlers(self, registry='base'):
        """ See zope.introspector.interfaces for documentation.
        """
        def f(item):
            return registry is getattr(item.registry, '__name__')
        
        return filter(f, globalregistry.base.registeredHandlers())

    
    def getAllSubscriptionAdapters(self, registry='base'):
        """ See zope.introspector.interfaces for documentation.
        """
        def f(item):
            return registry is getattr(item.registry, '__name__')
        
        return filter(f, globalregistry.base.registeredSubscriptionAdapters())
    
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
        
        if searchString == '*':
            interfaces = searchInterfaces
        else:
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
