==========
Mars Macro
==========

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration information in
Python code. Martian can then grok the system and do the appropriate
configuration registrations.

.. _Grok: http://grok.zope.org/

Mars Viewlet
------------

z3c packages bring significant clarity and a pattern for forms, view and
templates.

This package uses martian to configure z3c.macro based macros.

Example Code
------------

::

 class Navigation(mars.macro.MacroFactory):
     """Name defaults to factory.__name__: 'navigation'"""
     grok.template('templates/navigation.pt') # required
     grok.context(zope.interface.Interface) # required if no module context 

The following tal statement will look up the defined macro and insert its
template.::

 <div metal:use-macro="macro:navigation" />

Directives specific to this package
-----------------------------------

* mars.macro.macro(name):
  The name of the macro to be used. This allows us to reference 
  the named  macro defined with metal:define-macro if we use a 
  different IMacroDirective name.

* mars.macro.view(class_or_interface):
  The view for which the macro should be used',
  Default: IBrowserView

* mars.macro.content_type(name):
  The content type identifies the type of data.
  Default: text/html


Relevant grok directives
------------------------

* grok.layer(class_or_interface):
  The layer for which the template should be available.
  This directive can be used at module level
  Default: zope.publisher.browser.interfaces.IDefaultBrowserLayer

* grok.template(path):
  This is used different to IGrokDirectives.template. It looks up the file
  containing the page template using the path relative to the current module, if
  not found it tries `path` as an absolute path, if not found GrokError is
  raised. The file should end in extensions ``.pt`` or ``.html``.
  **Required**

* grok.name(name):
  The macro name which this macro is registered for. The macro name can be the
  same defined in metal:define-macro but does not have to be the same. If no
  macro attribute is given the name is used as the name defined in
  metal:define-macro. If you need to register a macro under a different name as
  the defined one, you can use the macro attribute which have to reference the
  metal.define-macro name. The TALES expression calls macros by this name and
  returns the macro within the same name or with the name defined in the macro
  attribute.
  Default: or **Required**?

* grok.context(class_or_interface):
  The context for which the macro should be used. Usually should be
  defined.
  Default: zope.interface.Interface

Tests
-----

See test directory.


