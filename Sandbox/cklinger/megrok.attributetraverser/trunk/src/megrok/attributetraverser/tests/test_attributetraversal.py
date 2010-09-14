"""
Let's setup some basic infrastructure for running the tests.

  >>> from grokcore.component import testing
  >>> testing.grok(__name__)

  >>> root = getRootFolder() 
  >>> root['app'] = app = MyApp()
  >>> root['app']
  <megrok.attributetraverser.tests.test_attributetraversal.MyApp object at ...>

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

Now we can call the appview with the testbrowser.
As result we receive the normal output of grok.View

  >>> browser.open('http://127.0.0.1/app/appview')
  >>> print browser.contents
  HELLO

Next, we try to access a method on this view, which is
not marked as traversable.

  >>> browser.handleErrors = True 
  >>> browser.open('http://127.0.0.1/app/appview/@@untraversable_method')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 404: Not Found

This method is traversable this means we should get the expected
result

  >>> browser.open('http://127.0.0.1/app/appview/@@traversable_method')
  >>> print browser.contents
  I'm traversable!

This test shows that query_strings work with traversable methods

  >>> browser.open('http://127.0.0.1/app/appview/@@with_querystring?name=Christian')
  >>> print browser.contents
  Hello Christian


  >>> browser.open('http://127.0.0.1/app/appview/@@json_response')
  >>> browser.headers.get('content-type')
  'application/json'

  >>> simplejson.loads(browser.contents)
  {'name': 'json'}
"""


import grok
import simplejson


class MyApp(grok.Context):
    pass


class Appview(grok.View):
    grok.context(MyApp)
    grok.traversable('traversable_method')
    grok.traversable('with_querystring')
    grok.traversable('json_response')

    def render(self):
        return "HELLO"

    def untraversable_method(self):
        return "I'm not traversable!"

    def traversable_method(self):
        return "I'm traversable!"

    def with_querystring(self, name):
        return "Hello " + name

    def json_response(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        data = {'name': 'json'}
        return simplejson.dumps(data)

def test_suite():
    import unittest
    from megrok.attributetraverser import tests
    from zope.testing import doctest

    layer = tests.AttributeTraverserLayer(tests.test_attributetraversal)
    suite = unittest.TestSuite()
    mytest = doctest.DocTestSuite(
        extraglobs={"getRootFolder": layer.getRootFolder},
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    mytest.layer = layer
    suite.addTest(mytest)
    return suite
