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
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'++icon++'

  >>> browser.open('http://localhost/++icon++i-dont-exist')
  Traceback (most recent call last):
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'i-dont-exist'

  >>> browser.open('http://localhost/++icon++tests/emblem-photos')
  >>> browser.contents
  '\x89PNG...'

  >>> browser.open('http://localhost/++icon++tests/i-dont-exist')
  Traceback (most recent call last):
  NotFound: Object: <megrok.icon.tests.TestIcons object at ...>,
  name: u'i-dont-exist'


Defining an icon for a component
================================

Setting a proper site for the browser tests
-------------------------------------------

  >>> from zope.site.hooks import setSite
  >>> root = getRootFolder()
  >>> setSite(root)

Using the ``icon`` directive
----------------------------

  >>> from megrok.icon import icon, get_component_icon_url

  >>> class MyContent(object):
  ...   icon(name="emblem-web", registry=TestIcons)

  >>> get_component_icon_url(MyContent, request)
  'http://127.0.0.1/++icon++tests/emblem-web'

  >>> inst = MyContent()
  >>> get_component_icon_url(inst, request)
  'http://127.0.0.1/++icon++tests/emblem-web'

  >>> class AnotherContent(object):
  ...   icon(name="none", registry=object)
  Traceback (most recent call last):
  ValueError: The specified registry is not a valid IIconRegistry.

  >>> class YetAnotherContent(object):
  ...   icon(name="an-icon", registry=TestIcons)

  >>> print get_component_icon_url(YetAnotherContent, request)
  None


Implicity registration
----------------------

  >>> class ContentIcons(IconRegistry):
  ...   name('content-icons')

  >>> class MyDocument(object):
  ...   icon(name="some-icon", registry=ContentIcons,
  ...        path="tests/more/an_icon.png")  

  >>> from megrok.icon import ICONS_BASES
  >>> ICONS_BASES
  {<class 'megrok.icon.tests.ContentIcons'>: [('some-icon', '/home/trollfot/work/sandbox/megrok.icon/trunk/src/megrok/icon/tests/../tests/more/an_icon.png')]}

  >>> grok_component('content-icons', ContentIcons)
  True

  >>> ICONS_BASES
  {}

  >>> icon_url = get_component_icon_url(MyDocument, request)
  >>> icon_url
  'http://127.0.0.1/++icon++content-icons/some-icon'

  >>> browser.open(icon_url)
  >>> browser.contents
  '\x89PNG...'
