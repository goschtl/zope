Zope 3 API Documentation
========================

This Zope 3 product provides a fully dynamic API documentation of Zope 3 and
registered add-on components. The product is very extensible and can be easily
extended by implementing new modules.


Installation
------------

  1. In your 'products.zcml' file make sure that

     (a) the static tree product is registered using::

         <include package="zope.products.statictree"/>

     (b) you register this product using::

         <include package="zope.products.apidoc"/>

  2. Restart Zope 3.

  3. You can now access the documentation via the new namespace "++apidoc++",
     like in::

     http://localhost:8080/++apidoc++/


Developing a Module
-------------------

  1. Implement a class that realizes the 'IDocumentationModule' interface.

  2. Register this class as a utility using something like this::

    <utility
        provides="zope.products.apidoc.interfaces.IDocumentationModule"
        factory=".examplemodule.ExampleModule"
        name="Example" />

  3. Take care of security by allowing at least 'IDocumentationModule':

    <class class=".ExampleModule">
      <allow interface="zope.products.apidoc.interfaces.IDocumentationModule" />
    </class>

  4. Provide a browser view called 'menu.html'.

  5. Provide another view, usually 'index.html', that can show the details for
     the various menu items.

  Note: There are several modules that come with the product. Just look in
  them for some guidance.
