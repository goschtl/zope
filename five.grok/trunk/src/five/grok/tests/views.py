"""Testing five.grok Views.

  >>> from OFS.SimpleItem import SimpleItem
  >>> item = SimpleItem()
  >>> item.id = 'item'

Setup a fake request:

  >>> from zope.publisher.browser import TestRequest
  >>> item.REQUEST = TestRequest()

We should now be able to find the view:

  >>> view = item.unrestrictedTraverse('@@aview')
  >>> view()
  'item'

"""
from five import grok
from OFS.interfaces import ISimpleItem

class SimpleItemView(grok.View):
    grok.context(ISimpleItem)
    grok.name('aview')
    grok.require('zope2.ViewManagementScreens')
        
    def __call__(self):
        return self.context.getId()
