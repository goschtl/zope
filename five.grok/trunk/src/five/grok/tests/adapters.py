"""Testing that grokcore adapters work under Zope2

  >>> from OFS.SimpleItem import SimpleItem
  >>> item = SimpleItem()
  >>> item.id = 'item'
  >>> IId(item).id()
  'item'

"""
from zope.interface import Interface
from five import grok
from OFS.interfaces import ISimpleItem

class IId(Interface):
    
    def id():
        """Returns the ID of the object"""

class SimpleItemIdAdapter(grok.Adapter):
    grok.provides(IId)
    grok.context(ISimpleItem)
    
    def id(self):
        return self.context.getId()