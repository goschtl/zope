from zope.interface import implements
from zope.component import adapts
from zope.introspector.interfaces import IRegistrySearch
from zope.component.interfaces import IAdapterRegistration,IHandlerRegistration, IUtilityRegistration

class AdapterSearch(object):
    implements(IRegistrySearch)
    adapts(IAdapterRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False):
        
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
                if string in getattr(each, '__name__'):
                    return True
        return False
    
    def getInterfaces(self):
        interfaces = []
        for each in list(self.registration.required) + [self.registration.provided]:
            module = getattr(each, '__module__')
            name = getattr(each, '__name__')
            if module:
                name = '%s.%s' % (module,name)
            interfaces.append(name)
        return interfaces
    
    def getObject(self):
        return self.registration
    
        
class HandlerSearch(object):
    implements(IRegistrySearch)
    adapts(IHandlerRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False):
        
        if string in self.registration.name:
            return True
        elif string in getattr(self.registration.factory, '__name__',''):
            return True
#        elif string in self.registration.info:
#            return True
        else:
            for each in self.registration.required:
                if string in getattr(each, '__name__'):
                    return True
        return False

    def getInterfaces(self):
        interfaces = []
        for each in list(self.registration.required) + [self.registration.factory]:
            module = getattr(each, '__module__')
            name = getattr(each, '__name__')
            if module:
                name = '%s.%s' % (module,name)
            interfaces.append(name)
        return interfaces
    
    def getObject(self):
        return self.registration
    

        
class UtilitySearch(object):
    implements(IRegistrySearch)
    adapts(IUtilityRegistration)

    def __init__(self, registration):
        self.registration = registration
        
    def searchRegistration(self, string, caseSensitive = False):
        
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
    
