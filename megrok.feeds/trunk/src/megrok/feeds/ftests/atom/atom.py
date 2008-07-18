"""
A grok.AtomFeed syndicates sub-objects into an Atom feed.

  >>> c = grok.MammothBox()
  >>> getRootFolder()["c"] = c

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/c/@@atom")
  >>> print browser.contents
  <html>...
  ...Manfred the Mammoth...
  ...Really big...
  ...

"""
import grok
from zope import schema
from zope.interface import Interface, implements
from zope.schema.fieldproperty import FieldProperty

class IMammoth(Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size", default=u"Quite normal")

class MammothBox(grok.OrderedContainer):
    pass

class Mammoth(grok.Model):
    implements(IMammoth)
    
    name = FieldProperty(IMammoth['name'])    
    size = FieldProperty(IMammoth['size'])    

class Atom(grok.AtomFeed):
    grok.context(MammothBox)
