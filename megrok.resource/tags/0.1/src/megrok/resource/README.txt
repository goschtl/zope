===============
megrok.resource
===============

`megrok.resource` is a package destined to integrate `hurry.resource`
and `z3c.hashedresource` into Grok applications. 

Setup
=====

Let's import and init the necessary work environment.

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False 


Library
=======

A Library is a component meant to expose a folder containing
resources::

  >>> from megrok import resource

  >>> class SomeCSS(resource.Library):
  ...    resource.path('ftests/css')

  >>> grok.testing.grok_component('somecss', SomeCSS)
  True

Once grokked, the library provides the ILibrary interface and gets an
accessible name::

  >>> from megrok.resource import ILibrary
  >>> ILibrary.providedBy(SomeCSS)
  True

  >>> SomeCSS.name
  'somecss'

At this point, it should be accessible via the component architecture
as a named adapter::

  >>> from zope.component import getAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> library = getAdapter(TestRequest(), name='somecss')
  >>> library
  <grokcore.view.components.DirectoryResource object at ...>


Resources
=========

Simple resources
----------------

Resources can be declared as part of their library, with their
dependencies.

  >>> css_a = resource.ResourceInclusion(SomeCSS, 'a.css')
  >>> css_b = resource.ResourceInclusion(SomeCSS, 'b.css')

Grouping resources
------------------

Sometimes, resources need to be grouped logically. They can be
declared in a group inclusion:

  >>> css_group = resource.GroupInclusion([css_a, css_b])
  >>> css_group.inclusions()
  [<ResourceInclusion 'a.css' in library 'somecss'>,
   <ResourceInclusion 'b.css' in library 'somecss'>]


Including resources in components
=================================

When rendering a web page we want to be able to include the resources
where we need them. 

There are several ways to include them. It can be done automatically
upon traversal on any IResourcesIncluder component, or manually specified.


Traversal inclusion
-------------------

For this example, we'll create a view and use the automatic inclusion,
using the `include` directive::

  >>> from grokcore import view
  >>> from zope.interface import Interface

  >>> class MyView(view.View):
  ...   grok.context(Interface)
  ...   resource.include(css_a)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('MyView', MyView)
  True

If we try to render the view, we notice that the HTML header is
empty. The resources are not included.

  >>> browser.open('http://localhost/@@myview')
  >>> print browser.contents
  <html><head></head></html>

For the resources to be automatically included during the traversal,
we need to inform the publishing machinery that our component (the
view), is a IResourcesIncluder::

  >>> from zope.interface import classImplements
  >>> classImplements(MyView, resource.IResourcesIncluder)

Now, when we render the view, the resources should be automatically
added to the HTML result::

  >>> browser.open('http://localhost/@@myview')
  >>> print browser.contents
  <html><head>
      <link... href="http://localhost/@@/++noop++.../somecss/a.css" />
  </head></html>

The `include` directive can be stacked, if several resources are to be
included::

  >>> class AnotherView(MyView):
  ...   resource.include(css_a)
  ...   resource.include(css_b)

  >>> grok.testing.grok_component('AnotherView', AnotherView)
  True

  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link... href="http://localhost/@@/++noop++.../somecss/a.css" />
    <link... href="http://localhost/@@/++noop++.../somecss/b.css" />
  </head></html>


Include validation
------------------

The `include` directive will raise an error if the provided value is
not a valid inclusion object::

  >>> sneaky = object()

  >>> class FailingView(view.View):
  ...   grok.context(Interface)
  ...   resource.include(sneaky)
  ...
  ...   def render(self):
  ...	  return u""
  Traceback (most recent call last):
  ...
  ValueError: You can only include IInclusions components.


Remote inclusion
-----------------

Until now, we've seen that the resource inclusion could be made using
the `include` directive. However, it can be very useful to be able to
set inclusion on classes we don't "own". This "remote" inclusion is
done using the `component_includes` function.

We first register a view that includes no resources::

  >>> class DummyView(view.View):
  ...   grok.context(Interface)
  ...
  ...   def render(self):
  ...	  return u"<html><head></head></html>"

  >>> grok.testing.grok_component('dummy', DummyView)
  True

The view class doesn't implement the needed interface::

  >>> resource.IResourcesIncluder.implementedBy(DummyView)
  False

Now, we can use the remove inclusion function, to enable resources::

  >>> resource.component_includes(DummyView, css_group)
  >>> resource.IResourcesIncluder.implementedBy(DummyView)
  True
  >>> resource.include.bind().get(DummyView)
  [<hurry.resource.core.GroupInclusion object at ...>]

This function can be used either on a class or an instance::

  >>> class UselessView(view.View):
  ...   grok.context(Interface)
  ...
  ...   def render(self): return u""

  >>> grok.testing.grok_component('useless', UselessView)
  True

  >>> from zope.component import getMultiAdapter
  >>> useless = getMultiAdapter(
  ...             (object(), TestRequest()), name="uselessview")
  >>> useless
  <megrok.resource.ftests.UselessView object at ...>

  >>> resource.component_includes(useless, css_group)
  >>> resource.IResourcesIncluder.providedBy(useless)
  True
  >>> resource.include.bind().get(useless)
  (<hurry.resource.core.GroupInclusion object at ...>,)


Cache and hash
==============

You probably noticed the "++noop++" traverser, in the resource
URL. This is used to provide a hash and therefore, a unique URL. It
can be very useful to work with caches and avoid outdated resources to
be served.

However, it can happen that this behavior (by default) is unwanted. To
disable the use of the hashed URL, we can use the `use_hash` directive
and set its value to False. This can be done either in the class
definition or by using the directive `set` method::

  >>> from megrok.resource import use_hash
  >>> use_hash.set(SomeCSS, False)
  
  >>> browser.open('http://localhost/@@anotherview')
  >>> print browser.contents
  <html><head>
    <link... href="http://localhost/@@/somecss/a.css" />
    <link... href="http://localhost/@@/somecss/b.css" />
  </head></html>
