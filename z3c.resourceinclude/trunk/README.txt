Overview
--------


The package is able to include the following types of resources:

* Cascading stylesheets (.css)
* Kinetic stylesheets (.kss)
* Javascript (.js)


Usage
-----

The package operates with browser resources, registered individually
or using the resource directory factory.

A simple example::

   <configure xmlns="http://namespaces.zope.org/zope"
             xmlns:browser="http://namespaces.zope.org/browser">

     <include package="z3c.resourceinclude" file="meta.zcml" />
     <include package="z3c.resourceinclude" />

     <browser:resource name="example.css" file="example.css" />

     <browser:resourceInclude
          layer="zope.publisher.interfaces.browser.IDefaultBrowserLayer"
          include="example.css"
      />

   </configure>


This registration means that whenever the request provides
``IDefaultBrowserLayer`` the resource named 'example.css' will be
included on the page.

To render HTML snippets that include applicable resources, a content
provider is provided, see ``z3c/resourceinclude/provide.py``. You may
also use one of the viewlets::

  <browser:viewlet
     name="resourceinclude"
     class="z3c.resourceinclude.viewlets.CacheOneHourViewlet"
     permission="zope.View" />

A convenience method is provided to require a given resource layer:

   >>> from z3c.resourceinclude import include
   >>> include(IMyLayer)

Ordering
--------

Resources are included in the order they're registered; that is, the
order in which the ZCML-directives are processed.

Stylesheets are included before javascripts as per general
recommendation. Kinetic stylesheets are included last.

Merging
-------

When not in 'devmode', the resource collector will automatically merge
resources, giving them a filename based on the contents (sha
digest). This has the side effect that merged resources are set to
never expire.
