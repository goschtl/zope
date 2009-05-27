Reuse zope.publisher-based components with bobo
***********************************************

The ``bozo.reuse`` package provides support for using
``zope.publisher`` based components with `bobo
<http://bobo.digicool.com>`_.  It provides:

- a request implementation that supports both ``zope.publisher`` and
  `WebOb <http://pythonpaste.org/webob/>`_ interfaces,

- a subclass of the bobo `WSGI <http://wsgi.org>`_ application that
  uses the request implementation,

- a development server based in the bobo development server, and

- bobo resources for using existing resources and views designed to
  work with ``zope.publisher``.


To learn more, see


Changes
*******

0.1 (yyyy-mm-dd)
================

Initial release
