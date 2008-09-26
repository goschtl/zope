Overview
========

This package implements a template compiler for dynamic HTML
documents. In particular, it supports the XSS rule language which is
used to associate elements with dynamic content.

XSS rule language
-----------------

The XSS rule language uses a CSS-compliant syntax to let you match HTML
elements using CSS selectors and set up dynamic content
definitions.

To associate a template with a rule file, use the <link> tag:

  <link rel="xss" type="text/xss" src="rules.xss" />

XSS files contain rules like the following:

  html > head > title {
    name: document-heading;
    structure: true;
    attributes: document-attributes;
  }

This rule will associate the <title> tag with the dynamic content
identifier "document-heading", escape the inserted content and apply
the dynamic attributes bound to the "document-attributes" identifier.

See the file ``template.txt`` within the package for documentation on
how to render templates and provide dynamic content and attributes.


Resource rebase functionality
-----------------------------

If a resource location adapter is available (see
``chameleon.html.interfaces.IResourceLocation``), references resources
(e.g. images, stylesheets, javascripts) will be "rebased" to the URL
returned by the component.

