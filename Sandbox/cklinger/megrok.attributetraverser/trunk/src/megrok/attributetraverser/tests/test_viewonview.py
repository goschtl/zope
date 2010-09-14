"""
Let's setup some basic infrastructure for running the tests.

  >>> from grokcore.component import testing
  >>> testing.grok(__name__)

  >>> root = getRootFolder() 
  >>> root['app1'] = app = MyApp()
  >>> root['app1']
  <megrok.attributetraverser.tests.test_viewonview.MyApp object at ...>

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Now we can call the appview with the testbrowser.
As result we receive the normal output of grok.View

  >>> browser.open('http://127.0.0.1/app1/simpleview')
  >>> print browser.contents
  HELLO

  >>> browser.open('http://127.0.0.1/app1/simpleview/@@getfoo')
  >>> print browser.contents
  fooBAR


Testing with the ZCA
--------------------

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = getMultiAdapter((app, request), name=u"simpleview")
  >>> view
  <megrok.attributetraverser.tests.test_viewonview.SimpleView object at ...>
  >>> print view()
  HELLO

  >>> getfoo = getMultiAdapter((view, request), name=u"getfoo")
  >>> getfoo 
  <megrok.attributetraverser.meta.AjaxMethods object at ...>
  >>> print getfoo()
  fooBAR

  >>> getbar = getMultiAdapter((view, request), name=u"getbar")
  >>> getbar
  <megrok.attributetraverser.meta.AjaxMethods object at ...>
  >>> print getbar()
  EGEO

"""


import grok
import simplejson
from megrok.attributetraverser.components import ViewExtension, jsonify


class MyApp(grok.Context):
    bar = "BAR"


class SimpleView(grok.View):
    grok.context(MyApp)
    foo = "foo"

    def render(self):
        return "HELLO"


class AjaxMethods(ViewExtension):
    grok.view(SimpleView)

    def getfoo(self):
        return self.view.foo + self.context.bar 
    
    def getbar(self):
        return "EGEO"


def test_suite():
    import unittest
    from megrok.attributetraverser import tests
    from zope.testing import doctest

    layer = tests.AttributeTraverserLayer(tests.test_viewonview)
    suite = unittest.TestSuite()
    mytest = doctest.DocTestSuite(
        extraglobs={"getRootFolder": layer.getRootFolder},
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    mytest.layer = layer
    suite.addTest(mytest)
    return suite
