==========
Mars Layer
==========

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

 Martian provides a framework that allows configuration to be expressed
 in declarative Python code. These declarations can often be deduced
 from the structure of the code itself. The idea is to make these
 declarations so minimal and easy to read that even extensive
 configuration does not overly burden the programmers working with the
 code. Configuration actions are executed during a separate phase
 ("grok time"), not at import time, which makes it easier to reason
 about and easier to test.

 The ``martian`` package is a spin-off from the `Grok`_ project, in the
 context of which this codebase was first developed. While Grok uses
 it, the code is completely independent of Grok.

.. _Grok: http://grok.zope.org/

Mars Layer
----------

The mars.layer package provides the means of creating and configuring ``layers``
and ``skins`` for an application using Zope3.

The base layers available are:

* mars.layer.IMinimalLayer
  Uses z3c.layer.IMinimalBrowserLayer

* mars.layer.IPageletLayer
  Uses z3c.layer.IPageletBrowserLayer

* mars.layer.IFormLayer
  Uses z3c.form.IFormLayer, z3c.layer.IPageletBrowserLayer

* mars.layer.IDivFormLayer
  Uses z3c.formui.IDivFormLayer, z3c.form.IFormLayer, z3c.layer.IPageletBrowserLayer

* mars.layer.ITableFormLayer
  Uses z3c.formui.ITableFormLayer, z3c.form.IFormLayer, z3c.layer.IPageletBrowserLayer

Example Code
------------

::

  import mars.layer

  class IMyLayer(mars.layer.IMinimalLayer):
      pass

  class MySkin(mars.layer.Skin):
      mars.layer.layer(IMyLayer)

Skin is available as http://localhost/++skin++myskin

Directives specific to this package
-----------------------------------

* mars.layer.layer(class_or_interface):
  The layer for which the view should be available.
  Default: zope.publisher.browser.interfaces.IBrowserRequest

Relevant grok directives
------------------------

* grok.name(name):
  The name for which the skin is registered.
  Default: factory.__name__.lower()

