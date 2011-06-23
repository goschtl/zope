"""
=====================
Test Content Provider
=====================

This doctest will test the various grok content provider registrations. Grok
viewlets offer the same flexibility as zope3, allowing you to register viewlets
for a particular view, context, layer, and permission.

Set up a content object in the application root::

  >>> root = getRootFolder()
  >>> root['wilma'] = CaveWoman()
  >>> root['fred'] = CaveMan()

Traverse to the view on the model object. We get the viewlets
registered for the default layer, with the anybody permission::

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/wilma/@@caveview")
  >>> print browser.contents
  Soup pot

"""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import grokcore.view as grok

class CaveWoman(grok.Context):
    pass

class CaveMan(grok.Context):
    pass

class CaveView(grok.View):
    grok.context(Interface)

class FireView(grok.View):
    grok.context(Interface)
    grok.template('caveview')

class Pot(grok.ContentProvider):
    grok.context(Interface)

    def render(self):
        return u"Soup pot"

class GoldPot(grok.ContentProvider):
    grok.name('pot')
    grok.context(Interface)
    grok.require('bone.gold')
    grok.view(FireView)

    def render(self):
        return u"Gold Soup Pot"

class IBoneLayer(IDefaultBrowserLayer):
    grok.skin('boneskin')

class LayeredPot(grok.ContentProvider):
    grok.name('pot')
    grok.context(Interface)
    grok.layer(IBoneLayer)

    def render(self):
        return u"Layered pot"
