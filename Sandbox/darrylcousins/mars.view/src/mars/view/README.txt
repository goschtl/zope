=========
Mars View
=========

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

.. _Grok: http://grok.zope.org/

Mars Template
------------

z3c packages bring significant clarity and a pattern for forms, view and
templates.

This package uses martian to configure views. The views here defined are
TemplateView and LayoutView, both use adapter lookup to locate the template to
be used (but can class attributes `template` for TemplateView and LayoutView and `layout` for
LayoutView will be used before adapter lookup).

TemplateView provides only a `render` method which returns the rendered
template.

LayoutView has a `__call__` method that returns the rendered layout template in
addition to a `render` method inherited from TemplateView which returns the
rendered template.

PageletView provides both a ``render`` method and a ``__call__`` method.

FormView is useful with z3c.form (see mars.formdemo for examples).

Example Code
------------

The following registers a view for Context named view. It has a
`render` method that renders the template defined by ViewTemplate::

 class Context(grok.Model):
     pass

 class View(mars.view.TemplateView):
     pass

 class ViewTemplate(mars.template.TemplateFactory):
     grok.template('templates/template.pt')
     grok.context(View)

The following snippet registers a view for Context named view. It has a
`__call__` method that renders the template defined by ViewLayout in addition to a
`render` method that renders the template defined by ViewTemplate::

 class Context(grok.Model):
     pass

 class View(mars.view.LayoutView):
     pass

 class ViewLayout(mars.template.LayoutFactory):
     grok.template('templates/template.pt')
     grok.context(View)

 class ViewSnippet(mars.template.TemplateFactory):
     grok.template('templates/snippet.pt')
     grok.context(View)

Directives specific to this package
-----------------------------------

* mars.view.layout(name):
  If defined the layout for LayoutView will be looked up as a `named adapter`.
  Should only be defined if the layout template has been registered as a named
  adapter.
  Default: ''


The mars.layer directive may be used
-----------------------------------------

* mars.layer.layer(class_or_interface):
  The layer for which the template should be available.
  Default: zope.publisher.browser.interfaces.IDefaultBrowserLayer

Relevant grok directives
------------------------

* grok.name(name):
  Name of the view, available in url as object/@@viewname.
  Default: factory.__name__.lower()

* grok.context(class_or_interface):
  The view for which the template should be available. Usually should be
  defined.
  Default: module context

* grok.template(name):
  If defined the template will be looked up as a `named adapter`. Should only be
  defined if the template has been registered as a named adapter.
  Default: ''

* grok.require(permission):
  Protect the view class with ``permission``.
  ``permission`` must already be defined, e.g. using
  grok.define_permission.
  Default: []

* grok.provides(class_or_interface):
  Interface the class is looked up as, probably wouldn't be used.
  Default: zope.interface.Interface

Tests
-----

See test directory.


