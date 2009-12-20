===============
megrok.resource
===============

`megrok.resource` is a package destined to integrate `hurry.resource`
and `z3c.hashedresource` into Grok applications.

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False 


Library
=======

Resources are generally files you 

  >>> from megrok import resource

  >>> class SomeCSS(resource.Library):
  ...    resource.path('ftests/css')

  >>> grok.testing.grok_component('somecss', SomeCSS)
  True

  >>> from megrok.resource import ILibrary
  >>> ILibrary.providedBy(SomeCSS)
  True

  >>> SomeCSS.name
  'somecss'

  >>> from zope.component import getAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> library = getAdapter(TestRequest(), name='somecss')
  >>> library
  <grokcore.view.components.DirectoryResource object at ...>


Resources
=========

Simple resources
----------------

  >>> css_a = resource.ResourceInclusion(SomeCSS, 'a.css')
  >>> css_b = resource.ResourceInclusion(SomeCSS, 'b.css')

Grouping resources
------------------

  >>> css_group = resource.GroupInclusion([css_a, css_b])
  >>> css_group.inclusions()
  [<ResourceInclusion 'a.css' in library 'somecss'>,
   <ResourceInclusion 'b.css' in library 'somecss'>]


Including resources in components
=================================

Setup
-----

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.site import SiteManagerContainer, LocalSiteManager
  >>> from zope.site.hooks import setSite

  >>> root = getRootFolder()
 

View & Include
--------------

To include a resource 

  >>> from grokcore import view

  >>> class MyView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   resource.include(css_a)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('MyView', MyView)
  True

  >>> browser.open('http://localhost/@@myview')
  >>> print browser.contents
  <html><head>
      <link... href="http://localhost/@@/++noop++.../somecss/a.css" />
  </head></html>

  >>> class AnotherView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   resource.include(css_a)
  ...   resource.include(css_b)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('AnotherView', AnotherView)
  True

  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link... href="http://localhost/@@/++noop++.../somecss/a.css" />
    <link... href="http://localhost/@@/++noop++.../somecss/b.css" />
  </head></html>



Resources inclusion
-------------------

  >>> class ForeignView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('foreign', ForeignView)
  True

  >>> resource.component_includes(ForeignView, css_group)

  >>> browser.open('http://localhost/@@foreignview')
  >>> print browser.contents
  <html><head>
    <link... href="http://localhost/@@/++noop++.../somecss/a.css" />
    <link... href="http://localhost/@@/++noop++.../somecss/b.css" />
  </head></html>

  >>> resource.component_includes(ForeignView)
  >>> browser.open('http://localhost/@@foreignview')
  >>> print browser.contents
  <html><head></head></html>


Include validation
------------------

  >>> toto = object()

  >>> class FailingView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   resource.include(toto)
  ...
  ...   def render(self):
  ...	  return u""
  Traceback (most recent call last):
  ...
  GrokImportError: You can only include IInclusions components.


Cache & hash
============

  >>> from megrok.resource import use_hash
  >>> use_hash.set(SomeCSS, False)
  
  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link... href="http://localhost/@@/somecss/a.css" />
    <link... href="http://localhost/@@/somecss/b.css" />
  </head></html>
