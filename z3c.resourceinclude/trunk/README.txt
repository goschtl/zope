Overview
--------

A package that provides functionality to register resources for
inclusion in HTML documents:

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

To actually include resources, a content provider is provided, see
``z3c/resourceinclude/provide.py``.


Ordering
--------

Resources will be included in the order they're registered for
inclusion; within an include-definition, order is respected only for
resources of similar kind.
