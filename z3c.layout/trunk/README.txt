HTML layout engine
==================

This package implements a page rendering model where a layout is based
on an existing HTML document and definitions of dynamic regions that
point to elements in the document tree.

A layout is rendered in the context of some object and it's left to
content providers to fill in dynamic data to the regions (see
``zope.contentprovider``).

Images, CSS and JS-resources that are referenced by the HTML document
are included automatically by declaring them as Zope browser
resources.

Benefits:

* No template language required
* Integrates directly with creative workflow
* Provides flexible extension points

Additionally, a set of viewlet managers are included to easily insert
viewlets into common HTML document slots.

