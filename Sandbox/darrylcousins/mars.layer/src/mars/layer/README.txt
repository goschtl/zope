==========
Mars Layer
==========

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

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

