import grok
from zope import interface

from zope.introspector.interfaces import IObjectInfo

class Inspect(grok.View):
    grok.context(interface.Interface)
    
    _objectinfo = None
    
    def getObjectInfo(self):
        if self._objectinfo is None:
            self._objectinfo = IObjectInfo(self.context)
        return self._objectinfo

    def getTypeName(self):
        type = self.getObjectInfo().getType()
        return type.__module__ + '.' + type.__name__
        
    def getTypeInspectURL(self):
        return ""
