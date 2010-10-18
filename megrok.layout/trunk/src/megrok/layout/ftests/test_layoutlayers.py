"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> getRootFolder()["a"] = A()
  >>> getRootFolder()["b"] = B()
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open("http://localhost/++skin++mydefaultskin/a/@@myview")
  >>> print browser.contents
  <div> A Layout </div>

  >>> browser.open("http://localhost/++skin++myskin/a/@@myview")
  >>> print browser.contents
  <div> A2 Layout </div>

  >>> browser.open("http://localhost/++skin++myskin/b/@@myviewb")
  >>> print browser.contents
  <div> B Layout </div>
"""

import grokcore.component as grok
from grokcore.view import layer, skin

from zope import interface
from megrok.layout import Layout, Page, CodePage

from grokcore.view import IDefaultBrowserLayer

class IMyDefaultLayer(IDefaultBrowserLayer):
    pass


class MyDefaultSkin(IMyDefaultLayer):
    skin('mydefaultskin')


layer(IMyDefaultLayer)



class MySkinLayer(IDefaultBrowserLayer):
    pass


class MySkin(MySkinLayer):
    skin('myskin')


class A(grok.Context):
    pass


class B(grok.Context):
    pass


class ALayout(Layout):
    grok.context(A)

    def render(self):
	return "<div> A Layout </div>"


class A2Layout(Layout):
    grok.context(A)
    layer(MySkinLayer)

    def render(self):
	return "<div> A2 Layout </div>"


class BLayout(Layout):
    grok.context(B)
    layer(MySkinLayer)

    def render(self):
	return "<div> B Layout </div>"


class MyView(CodePage):
    grok.context(interface.Interface)

    def render(self):
        return "MYVIEW"


class MyViewB(CodePage):
    grok.context(interface.Interface)
    layer(MySkinLayer)

    def render(self):
        return "MYVIEW"


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite
