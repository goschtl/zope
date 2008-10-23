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
from zope.interface import implements
from zope.component import adapts
from zope.introspector.interfaces import IRegistrySearch
from zope.component.interfaces import (IAdapterRegistration,
                                       IHandlerRegistration,
                                       IUtilityRegistration,
                                       ISubscriptionAdapterRegistration)
import grokcore.component as grok

class AdapterSearch(grok.Adapter):
    grok.implements(IRegistrySearch)
    grok.context(IAdapterRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False, registry='base'):
        
        if registry is not getattr(self.registration.registry, '__name__'):
            return False
        
        if string in getattr(self.registration.provided, '__name__', ''):
            return True
        elif string in self.registration.name:
            return True
        elif string in getattr(self.registration.factory, '__name__', ''):
            return True
#        elif string in self.registration.info:
#            return True
        else:
            for each in self.registration.required:
                if string in getattr(each, '__name__', ''):
                    return True
        return False
    
    def getInterfaces(self):
        interfaces = []
        for each in list(
            self.registration.required) + [self.registration.provided]:
            module = getattr(each, '__module__')
            name = getattr(each, '__name__')
            if module:
                name = '%s.%s' % (module,name)
            interfaces.append(name)
        return interfaces
    
    def getObject(self):
        return self.registration

class SubscriptionSearch(AdapterSearch):
    grok.implements(IRegistrySearch)
    grok.context(ISubscriptionAdapterRegistration)
        
class HandlerSearch(grok.Adapter):
    grok.implements(IRegistrySearch)
    grok.context(IHandlerRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False, registry='base'):
        
        if registry is not getattr(self.registration.registry, '__name__'):
            return False
        
        if string in self.registration.name:
            return True
        elif string in getattr(self.registration.factory, '__name__',''):
            return True
#        elif string in self.registration.info:
#            return True
        else:
            for each in self.registration.required:
                if string in getattr(each, '__name__',''):
                    return True
        return False

    def getInterfaces(self):
        interfaces = []
        for each in list(
            self.registration.required) + [self.registration.factory]:
            module = getattr(each, '__module__')
            name = getattr(each, '__name__')
            if module:
                name = '%s.%s' % (module,name)
            interfaces.append(name)
        return interfaces
    
    def getObject(self):
        return self.registration
    

        
class UtilitySearch(grok.Adapter):
    grok.implements(IRegistrySearch)
    grok.context(IUtilityRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False, registry='base'):
        
        if registry is not getattr(self.registration.registry, '__name__'):
            return False
        
        if string in getattr(self.registration.provided, '__name__',''):
            return True
        elif string in self.registration.name:
            return True
#        elif string in self.registration.info:
#            return True
        return False

    def getInterfaces(self):
        interfaces = []
        module = getattr(self.registration.provided, '__module__')
        name = getattr(self.registration.provided, '__name__')
        if module:
            name = '%s.%s' % (module,name)
        interfaces.append(name)
        return interfaces
    
    def getObject(self):
        return self.registration
    
