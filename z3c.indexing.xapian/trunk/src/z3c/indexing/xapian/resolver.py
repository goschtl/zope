from zope import interface
from zope import component

import interfaces

from zope.app.intid.interfaces import IIntIdsQuery

class IntIdResolver(object):
    interface.implements(interfaces.IResolver)
    
    protocol = 'intid'

    def getId(self, obj):
        query = component.getUtility(IIntIdsQuery)
        return "%s://%s" % (self.protocol, query.getId(obj))

    def getObject(self, id):
        protocol, intid = id.split('://')
        
        try:
            intid = int(intid)
        except TypeError:
            raise TypeError("Must be an integer id.")
        
        query = component.getUtility(IIntIdsQuery)
        return query.getObject(intid)    
