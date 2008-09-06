"""
Testing the plugging in of a template language

  >>> grok.testing.grok(__name__)

  >>> cave = Cave()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope import component

  # And the template directory template:
  >>> view = component.getMultiAdapter((cave, request), name='kakadu')
  >>> print view()
  <html><body>Kakadu is in Australia</body></html>

  # We should be able to extend the namespace in the view and
  >>> view = component.getMultiAdapter((cave, request), name='sierra')
  >>> print view()
  <html><body>Sierra de San Fransisco is in Mexico</body></html>

"""
import grokcore.view as grok, os

# Dummy template language:
class MyTemplate(object):

    def __init__(self, text):
        self._text = text

    def render(self, **kw):
        # Silliest template language ever:
        return self._text % kw

class MyPageTemplate(grok.components.GrokTemplate):

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

class MyPageTemplateFactory(grok.GlobalUtility):

    grok.implements(grok.interfaces.ITemplateFileFactory)
    grok.name('mtl')

    def __call__(self, filename, _prefix=None):
        return MyPageTemplate(filename=filename, _prefix=_prefix)

class Cave(grok.Context):
    pass

class Kakadu(grok.View):
    grok.template('kakadu')

class Sierra(grok.View):
    grok.template('sierra')

    def namespace(self):
        return {'cave': 'Sierra de San Fransisco',
                'country': 'Mexico'}
