z3c.resourceinclude
-------------------

This package provides functionality to define web-resources for
inclusion in HTML documents.

Registering resources
---------------------

Let's set up a browser resource.

   >>> from z3c.resourceinclude.testing import MockResourceFactory

   >>> from zope import component
   >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
   >>> from zope.component.interfaces import IResource

Let's register a couple of resources.

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/plain'),
   ...     (IDefaultBrowserLayer,), IResource, name='1')

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/plain'),
   ...     (IDefaultBrowserLayer,), IResource, name='2')

We'll now instantiate a resource manager and register it as an adapter
on the default browser layer.

   >>> from z3c.resourceinclude.manager import ResourceManager
   >>> from z3c.resourceinclude.interfaces import IResourceManager

   >>> manager = ResourceManager()
   >>> component.provideAdapter(
   ...     manager, (IDefaultBrowserLayer,), IResourceManager, name='A')

Let's register the first resource for this layer by adding it to the
manager we just registered.

   >>> manager.add('1')

Now we'll introduce another layer and register the second resource for
it.

   >>> class ISpecificLayer(IDefaultBrowserLayer):
   ...     """A specific layer."""

   >>> manager = ResourceManager()
   >>> component.provideAdapter(
   ...     manager, (ISpecificLayer,), IResourceManager, name='B')

   >>> manager.add('2')

Collecting resources
--------------------

A resource collector is responsible for gathering resources that apply
to the current browser request.

   >>> from z3c.resourceinclude.collector import ResourceCollector
   >>> from zope.publisher.browser import TestRequest

   >>> request = TestRequest()
   >>> collector = ResourceCollector(request)

Let's ask the collector to gather resources available for this
request.

   >>> collector.collect()
   (<MockResource type="text/plain">,)

Let's confirm that if we provide the specific layer on the request,
that we'll get the other resource as well.

   >>> from zope import interface
   >>> interface.alsoProvides(request, ISpecificLayer)

   >>> collector.collect()
   (<MockResource type="text/plain">,
    <MockResource type="text/plain">)

Resources are only included once.

   >>> manager.add('1')

   >>> collector.collect()
   (<MockResource type="text/plain">,
    <MockResource type="text/plain">)

Resources are sorted by their content-type.

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/x-web-markup'),
   ...     (IDefaultBrowserLayer,), IResource, name='3')

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/plain'),
   ...     (IDefaultBrowserLayer,), IResource, name='4')

   >>> manager.add('3')
   >>> manager.add('4')

   >>> collector.collect()
   (<MockResource type="text/plain">,
    <MockResource type="text/plain">,
    <MockResource type="text/plain">,
    <MockResource type="text/x-web-markup">)

Including resources in an HTML document
---------------------------------------

Let's register a few browser resources:

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/css'),
   ...     (IDefaultBrowserLayer,), IResource, name='base.css')

   >>> component.provideAdapter(
   ...     MockResourceFactory('application/x-javascript'),
   ...     (IDefaultBrowserLayer,), IResource, name='base.js')

   >>> component.provideAdapter(
   ...     MockResourceFactory('text/kss'),
   ...     (IDefaultBrowserLayer,), IResource, name='base.kss')

   >>> manager.add('base.css')
   >>> manager.add('base.js')
   >>> manager.add('base.kss')

Let's register the resource collector as a component.

   >>> component.provideAdapter(ResourceCollector)

We can now render the resource includes.

   >>> from z3c.resourceinclude.provider import ResourceIncludeProvider
   >>> provider = ResourceIncludeProvider(None, request, None)

   >>> provider.update()
   >>> print provider.render()
   <script src="http://nohost/site/@@/mock" type="text/javascript">
   </script>
   <style media="all" type="text/css">
       <!-- @import url("http://nohost/site/@@/mock"); -->
   </style>
   <link href="http://nohost/site/@@/mock" rel="kinetic-stylesheet" type="text/kss" />
