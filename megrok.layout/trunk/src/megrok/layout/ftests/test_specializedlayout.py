"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> getRootFolder()["one"] = One()
  >>> getRootFolder()["two"] = Two()
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False 
  
  >>> browser.open("http://localhost/++skin++askin/one/@@myview") 
  >>> print browser.contents
  <div> Layout A for context One </div>

  >>> browser.open("http://localhost/++skin++askin/two/@@myview") 
  >>> print browser.contents
  <div> Layout A for context Two </div>

  >>> browser.open("http://localhost/++skin++bskin/one/@@myview") 
  >>> print browser.contents
  <div> Layout B for context One </div>

  >>> browser.open("http://localhost/++skin++bskin/two/@@myview") 
  >>> print browser.contents
  <div> Layout B for context Two </div>
"""

import grokcore.view as grok
from grokcore.view import layer, skin

from zope import interface
from megrok.layout import Layout, Page 

from grokcore.view import IDefaultBrowserLayer

class IALayer(IDefaultBrowserLayer):
    pass


class IBLayer(IALayer):
    pass


class ASkin(IALayer):
    skin('askin')


class BSkin(IBLayer):
    skin('bskin')


class One(grok.Context):
    pass


class Two(One):
    pass


class AOneLayout(Layout):
    grok.context(One)
    grok.layer(IALayer)

    def render(self):
	return "<div> Layout A for context One </div>"

class ATwoLayout(Layout):
    grok.context(Two)
    grok.layer(IALayer)

    def render(self):
	return "<div> Layout A for context Two </div>"

class BOneLayout(Layout):
    grok.context(One)
    grok.layer(IBLayer)

    def render(self):
	return "<div> Layout B for context One </div>"

class BTwoLayout(Layout):
    grok.context(Two)
    grok.layer(IBLayer)

    def render(self):
	return "<div> Layout B for context Two </div>"


class MyView(Page):
    grok.context(interface.Interface)
    grok.layer(IALayer)

    def render(self):
        return "MyView on IALayouer"


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite  
