import grokcore.component as grok
from zope import component
from zope.interface import Interface
from zope.introspector.interfaces import IInfos, IInfo

class Infos(grok.Adapter):
    grok.context(Interface)
    grok.provides(IInfos)

    def infos(self):
        return component.getAdapters((self.context,), IInfo)

