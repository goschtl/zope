"""Testing that grokcore adapters work under Zope2

  >>> from OFS.SimpleItem import SimpleItem
  >>> item = SimpleItem()
  >>> item.id = 'item'
  >>> IId(item).id()
  'item'

"""
from zope.interface import Interface
from zope.component import adapts
from grokcore.component.components import Adapter
from grokcore.component.directive import provides, context
from OFS.interfaces import ISimpleItem

class IId(Interface):
    
    def id():
        """Returns the ID of the object"""

class SimpleItemIdAdapter(Adapter):
    provides(IId)
    context(ISimpleItem)
    
    def id(self):
        return self.context.getId()