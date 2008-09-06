"""

  >>> grok.testing.grok(__name__)

View with an associated PageTemplate that is referred to using
``grok.template``:

  >>> manfred = Mammoth()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope import component
  >>> view = component.getMultiAdapter((manfred, request), name='painting')
  >>> print view()
  <html><body><h1>GROK PAINT MAMMOTH!</h1></body></html>

``grok.name`` and ``grok.template`` can be combined:

  >>> view = component.getMultiAdapter((manfred, request), name='meal')
  >>> print view()
  <html><body><h1>GROK EAT MAMMOTH!</h1></body></html>

"""
import grokcore.view as grok

grok.templatedir('templates')

class Mammoth(grok.Context):
    pass

class Painting(grok.View):
    grok.template('painting')

class Food(grok.View):
    grok.template('food_template')
    grok.name('meal')
