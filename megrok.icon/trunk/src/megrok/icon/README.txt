===========
megrok.icon
===========

  >>> from megrok.icon import IconRegistry, IIconRegistry
  >>> from grokcore.view import path, name 

  >>> class TestIcons(IconRegistry):
  ...   name('tests')
  ...   path('tests/icons')


  >>> grok_component('icons', TestIcons)
  True

  >>> from zope.component import getUtility
  >>> registry = getUtility(IIconRegistry, name='tests')

  >>> print registry.get('emblem-photos')
  <megrok.icon.registry.Icon object at ...>

  >>> print registry.get('not-here')
  None

  >>> resource = registry.resource('emblem-photos')
  >>> print resource
  <zope.browserresource.file.FileResourceFactory object at ...>

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(REQUEST_METHOD='GET')
  >>> icon = resource(request)
  >>> print icon
  <zope.browserresource.file.FileResource object at ...>

  >>> view, ignore = icon.browserDefault(request)
  >>> view()
  '\x89PNG...'

  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False 

  >>> browser.open('http://localhost/++icon++tests/emblem-photos')
  >>> browser.contents
  '\x89PNG...'

  >>> browser.open('http://localhost/++icon++tests/i-dont-exist')
  Traceback (most recent call last):
  ...
  NotFound: Object: <megrok.icon.tests.TestIcons object at ...>,
  name: u'i-dont-exist'
