===========
megrok.icon
===========

Registry
========

Manual registration
-------------------

  >>> from megrok.icon import IconsRegistry, getIconsRegistriesMap
  >>> registries = getIconsRegistriesMap()
  >>> registry = registries.register('tests', IconsRegistry)

Manual population
-----------------

  >>> from megrok.icon import populate_icons_registry
  >>> populate_icons_registry('tests', 'tests/icons')

An error is raised if the registry we try to populate does not exist::

  >>> populate_icons_registry('non-existing', 'tests/icons')
  Traceback (most recent call last):
  ...
  IconsRegistryError: unknown icon registry: 'non-existing'


Manual fetching
---------------

Icon getter
~~~~~~~~~~~

  >>> registry.get('emblem-photos')
  '...tests/icons/emblem-photos.png'

Resource getter
~~~~~~~~~~~~~~~

  >>> print registry.resource('emblem-photos')
  <zope.browserresource.file.FileResourceFactory object at ...>

  
Automated registration and population
-------------------------------------

  >>> from megrok.icon import name, path

  >>> class ContentIcons(IconsRegistry):
  ...   name("common")
  ...   path("tests/more")

  >>> grok_component('content', ContentIcons)
  True

  >>> common_icons = registries.get('common')
  >>> common_icons
  <megrok.icon.tests.ContentIcons object at ...>

  >>> common_icons.get("an_icon")
  '...tests/more/an_icon.png'


Resource
========

Rendering
---------

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(REQUEST_METHOD='GET')

  >>> factory = common_icons.resource("an_icon")
  >>> print factory
  <zope.browserresource.file.FileResourceFactory object at ...>

  >>> resource = factory(request)
  >>> resource
  <zope.browserresource.file.FileResource object at ...>

  >>> view, ignore = resource.browserDefault(request)
  >>> view()
  '\x89PNG...'


Browser access
--------------

  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False 

  >>> browser.open('http://localhost/++icon++common/an_icon')
  >>> browser.contents
  '\x89PNG...'

Errors handling
~~~~~~~~~~~~~~~

  >>> browser.open('http://localhost/++icon++')
  Traceback (most recent call last):
  ...
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'++icon++'

  >>> browser.open('http://localhost/++icon++not-here')
  Traceback (most recent call last):
  ...
  NotFound: Object: <zope.site.folder.Folder object at ...>,
  name: u'not-here'

  >>> browser.open('http://localhost/++icon++common')
  Traceback (most recent call last):
  ...
  NotFound: Object: <megrok.icon.tests.ContentIcons object at ...>,
  name: u'index.html'

  >>> browser.open('http://localhost/++icon++common/unknown')
  Traceback (most recent call last):
  ...
  NotFound: Object: <megrok.icon.tests.ContentIcons object at ...>,
  name: u'unknown'


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
  ...   icon(name="an_icon", registry='common')

  >>> get_component_icon_url(MyContent, request)
  'http://127.0.0.1/++icon++common/an_icon'

  >>> inst = MyContent()
  >>> get_component_icon_url(inst, request)
  'http://127.0.0.1/++icon++common/an_icon'


Registration order
------------------

  >>> class SomeContent(object):
  ...   icon(name="mycontent", registry='my-icons',
  ...        path="tests/icons/emblem-default.png")
  
  >>> iconurl = get_component_icon_url(SomeContent, request)
  >>> print iconurl
  http://127.0.0.1/++icon++my-icons/mycontent

  >>> reg = registries.get('my-icons')
  >>> reg
  <megrok.icon.registry.IconsRegistry object at ...>

  >>> print reg.get('an_icon')
  None

  >>> browser.open(iconurl)
  >>> browser.contents
  '\x89PNG...'

  >>> class SomeIcons(IconsRegistry):
  ...   name("my-icons")
  ...   path("tests/more")

  >>> grok_component('someicons', SomeIcons)
  True

  >>> reg = registries.get('my-icons')
  >>> reg
  <megrok.icon.tests.SomeIcons object at ...>

  >>> reg.get('an_icon')
  '...tests/more/an_icon.png'

  >>> iconurl = get_component_icon_url(SomeContent, request)
  >>> iconurl
  'http://127.0.0.1/++icon++my-icons/mycontent'

  >>> browser.open(iconurl)
  >>> browser.contents
  '\x89PNG...'
