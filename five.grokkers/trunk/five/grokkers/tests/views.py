"""Testing five.grokkers Views.

  >>> from OFS.SimpleItem import SimpleItem
  >>> item = SimpleItem()
  >>> item.id = 'item'

Setup a fake request:

  >>> from zope.publisher.browser import TestRequest
  >>> item.REQUEST = TestRequest()

We should now be able to find the view:

  >>> view = item.unrestrictedTraverse('@@theview')
  >>> view()
  'item'

"""
from five.grokkers import grok
from OFS.interfaces import ISimpleItem

class SimpleItemView(grok.View):
    grok.context(ISimpleItem)
    grok.name('theview')
        
    def __call__(self):
        return self.context.getId()
        