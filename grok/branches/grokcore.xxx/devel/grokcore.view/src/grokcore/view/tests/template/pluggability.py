"""
Testing the plugging in of a template language

  >>> from grokcore.view.tests.test_all import grok
  >>> grok(__name__)

  >>> cave = Cave()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope import component

  # The inline template should work:
  >>> view = component.getMultiAdapter((cave, request), name='sebaayeni')
  >>> print view()
  <html><body>Sebaayeni is in South Africa</body></html>

  # And the inline file template:
  >>> view = component.getMultiAdapter((cave, request), name='lascaux')
  >>> print view()
  <html><body>Lascaux is in France</body></html>

  # And the template directory template:
  >>> view = component.getMultiAdapter((cave, request), name='kakadu')
  >>> print view()
  <html><body>Kakadu is in Australia</body></html>

  # We should be able to extend the namespac in the view and
  >>> view = component.getMultiAdapter((cave, request), name='sierra')
  >>> print view()
  <html><body>Sierra de San Fransisco is in Mexico</body></html>

"""
import os
import grokcore.component
import grokcore.view
from grokcore.view import components

from grokcore.view.tests.components import TestView
from grokcore.view.tests.components import TestModel

# Dummy template language:
class MyTemplate(object):

    def __init__(self, text):
        self._text = text

    def render(self, **kw):
        # Silliest template language ever:
        return self._text % kw

class MyPageTemplate(components.GrokTemplate):

    def setFromString(self, string):
        self._template = MyTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        file = open(os.path.join(_prefix, filename))
        self._template = MyTemplate(file.read())

    def namespace(self, view):
        # I'll override the default namespace here for testing:
        return {'middle_text': 'is in'}

    def render(self, view):
        return self._template.render(**self.getNamespace(view))

class MyPageTemplateFactory(grokcore.component.GlobalUtility):

    grokcore.component.implements(grokcore.view.interfaces.ITemplateFileFactory)
    grokcore.component.name('mtl')

    def __call__(self, filename, _prefix=None):
        return MyPageTemplate(filename=filename, _prefix=_prefix)

class Cave(TestModel):
    pass

class Sebaayeni(TestView):
    pass

sebaayeni = MyPageTemplate('<html><body>Sebaayeni is in South Africa</body></html>')

class Lascaux(TestView):
    pass

lascaux = MyPageTemplate(filename='lascaux.html')

class Kakadu(TestView):
    pass

class Sierra(TestView):

    def namespace(self):
        return {'cave': 'Sierra de San Fransisco',
                'country': 'Mexico'}
