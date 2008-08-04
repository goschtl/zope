HTML layout engine
==================

This package implements a page rendering model based on a static HTML
document that is made dynamic from the outside by mapping content
provider definitions to locations in the HTML document tree. This is
called a "layout".

The component architecture is utilized to provide extension points
that allow wide application. Two-phase rendering is supported using
the ``zope.contentprovider`` rendering scheme (update/render).

Static resources, as referenced by the HTML document (images,
stylesheets and javascript files) are included carbon copy and
published as browser resources (see ``zope.app.publisher.browser``).

Benefits:

* No template language required
* Support for two-phase rendering
* Integrates with creative workflow
* Flexible extension points

