===============
megrok.resource
===============

After many discussions on the mailinglist, on irc and the sprint in cologne
i started to work on a first prototype of megrok.resource.

megrok.resource is a combination of these packages:

 - hurry.resource
 - hurry.zoperesource
 - grokcore.view.ResourceDirectory
 - z3c.hashedresource


How does it work:
=================

Setup
-----

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.site import SiteManagerContainer 
  >>> from zope.site import LocalSiteManager
  >>> from zope.site.hooks import setSite

  >>> root = getRootFolder()
  >>> root['myapp'] = myapp = SiteManagerContainer()

Our application has to be a Site to access the right url for the inclusions

  >>> root['myapp'].setSiteManager(LocalSiteManager(root['myapp']))
  >>> setSite(root['myapp'])


Inclusions & Library
--------------------

Let's start with a Library. A Library is in the context of megrok.resource
a ResourceDirectory which holds a kind of different ResourceInclusions

  >>> from megrok.resource import Library, ResourceInclusion, include
  >>> import grokcore.view as view 
  >>> import grokcore.component as grok 

  >>> class SomeCSS(Library):
  ...    view.path('ftests/css')
  ...    view.name('somecss')

  >>> grok.testing.grok_component('somecss', SomeCSS)
  True

  >>> from megrok.resource import ILibrary
  >>> ILibrary.providedBy(SomeCSS)
  True

  >>> from zope.component import getAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> library = getAdapter(TestRequest(), name='somecss')
  >>> library
  <grokcore.view.components.DirectoryResource object at ...>


View & Include
--------------

  >>> from zope.testbrowser.testing import Browser
  >>> from zope.component import getMultiAdapter

  >>> browser = Browser()
  >>> browser.handleErrors = False 

  >>> css_a = ResourceInclusion(SomeCSS, 'a.css')
  >>> css_b = ResourceInclusion(SomeCSS, 'b.css')

To include a resource we need in the most cases a view.

  >>> class MyView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   include(css_a)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('MyView', MyView)
  True

  >>> browser.open('http://localhost/@@myview')
  >>> print browser.contents
  <html><head>
      <link rel="stylesheet" type="text/css" href="http://localhost/@@/++noop++.../somecss/a.css" />
  </head></html>

  >>> class AnotherView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   include(css_a)
  ...   include(css_b)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('AnotherView', AnotherView)
  True

  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link rel="stylesheet" type="text/css" href="http://localhost/@@/++noop++.../somecss/a.css" />
    <link rel="stylesheet" type="text/css" href="http://localhost/@@/++noop++.../somecss/b.css" />
  </head></html>


No hash:

  >>> from megrok.resource import use_hash
  >>> use_hash.set(SomeCSS, False)
  
  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link rel="stylesheet" type="text/css" href="http://localhost/@@/somecss/a.css" />
    <link rel="stylesheet" type="text/css" href="http://localhost/@@/somecss/b.css" />
  </head></html>


Failing validation:

  >>> toto = object()

  >>> class FailingView(view.View):
  ...   grok.context(SiteManagerContainer)
  ...   include(toto)
  ...
  ...   def render(self):
  ...	  return u""
  Traceback (most recent call last):
  ...
  GrokImportError: You can only include IInclusions components.
