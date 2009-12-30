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

  >>> browser.open('http://localhost/++icon++')
  Traceback (most recent call last):
  ...
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'++icon++'

  >>> browser.open('http://localhost/++icon++i-dont-exist')
  Traceback (most recent call last):
  ...
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'i-dont-exist'

  >>> browser.open('http://localhost/++icon++tests/emblem-photos')
  >>> browser.contents
  '\x89PNG...'

  >>> browser.open('http://localhost/++icon++tests/i-dont-exist')
  Traceback (most recent call last):
  ...
  NotFound: Object: <megrok.icon.tests.TestIcons object at ...>,
  name: u'i-dont-exist'

  >>> from megrok.icon import icon, get_component_icon_url

  >>> class MyContent(object):
  ...   icon(name="emblem-web", registry="tests")

  >>> from zope.site.hooks import setSite
  >>> root = getRootFolder()
  >>> setSite(root)

  >>> get_component_icon_url(MyContent, request)
  'http://127.0.0.1/++icon++tests/emblem-web'

  >>> inst = MyContent()
  >>> get_component_icon_url(inst, request)
  'http://127.0.0.1/++icon++tests/emblem-web'

  >>> class AnotherContent(object):
  ...   icon(name="none", registry="tests")

  >>> print get_component_icon_url(AnotherContent, request)
  None

  >>> class YetAnotherContent(object):
  ...   icon(name="an-icon", registry="buzz")

  >>> print get_component_icon_url(YetAnotherContent, request)
  None


