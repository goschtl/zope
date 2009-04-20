import grok
from zope import interface

from zope.introspector.interfaces import IObjectInfo
from zope.introspector.viewinfo import ViewInfo
from grokui.introspector.util import dotted_name_url

class Inspect(grok.View):
    grok.context(interface.Interface)
    
    _objectinfo = None
    
    def getObjectInfo(self):
        if self._objectinfo is None:
            self._objectinfo = IObjectInfo(self.context)
        return self._objectinfo

    def getTypeName(self):
        mod = getattr(self.context, '__module__', '')
        name = getattr(self.context, '__name__', '')
        if name:
            mod += '.' + name
        return mod

    def getTypeInspectURL(self):
        return dotted_name_url(self.getTypeName())

    def getViews(self):
        info = ViewInfo(self.context)
        return sorted(list(info.getAllViews()))
