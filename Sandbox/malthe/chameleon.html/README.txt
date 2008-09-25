Overview
========

This package implements a template compiler for dynamic HTML
documents. In particular, it supports the dynamic element language XSS
which is used to set up dynamic content.

XSS language
------------

The XSS language uses a CSS-compliant syntax to let you match HTML
elements using CSS selectors and set up dynamic content
definitions.

For example:

  html > head > title {
    name: document-heading;
    structure: true;
    attributes: document-attributes;
  }


