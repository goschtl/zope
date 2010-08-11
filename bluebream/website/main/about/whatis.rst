.. _whatis:

What is BlueBream ?
===================

**BlueBream** -- formerly known as **Zope 3** -- is a web framework written
in the Python programming language.

A few features distinguish BlueBream from other Python web frameworks.

- BlueBream is built on top of the `Zope Tool Kit` (ZTK), which has many
  years of experience proving it meets the demanding requirements for
  stable, scalable software.

- BlueBream uses the powerful and familiar `Buildout` system written in
  Python.

- BlueBream employs the Zope Object Database (`ZODB`), a transactional
  object database providing extremely powerful and easy to use persistence.

- BlueBream registers components with Zope Component Markup Language
  (`ZCML`), an XML based configuration language, providing limitless
  flexibility.

- BlueBream features the `Zope Component Architecture` (ZCA) which
  implements `Separation of concerns` to create highly cohesive reusable
  components (zope.component_).

- BlueBream implements Python Web Server Gateway Interface `WSGI` using
  `Paste`, `PasteScript`, and `PasteDeploy`.

- BlueBream includes a number of well tested components to implement common
  activities.  A few are of these are:

  - zope.publisher_ publishes Python objects on the web, emphasizing `WSGI`
    compatibility

  - zope.security_ provides a generic mechanism for pluggable security
    policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing
    frameworks

  - zope.pagetemplate_ is an XHTML-compliant language for devloping
    templates

  - zope.schema_ is a schema engine

  - zope.formlib_ is a tool for automatically generating forms

BlueBream is free/open source software, owned by the `Zope Foundation`.
Bluebream is licensed under the `Zope Public License` (BSD like, GPL
compatible license).

.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib
