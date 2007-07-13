=============
Mars Template
=============

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

The mars.template package provides the means of creating and configuring
``templates`` for an application using Zope3.

These templates use presentation patterns used by other z3c packages.

z3c packages bring significant clarity and a pattern for forms, view and
templates.

Example Code
------------

::

    class View(grok.View):

        def render(self):
            template = zope.component.getMultiAdapter(
                (self, self.request), IPageTemplate)
            return template(self)

    class ViewTemplate(mars.template.TemplateFactory):
        grok.template('templates/macro.pt')
        grok.context(View)
        mars.template.macro('mymacro')

Directives specific to this package
-----------------------------------

* mars.template.macro(name):
  The macro to be used.  This allows us to define different macros in on template.
  The template designer can now create whole site, the ViewTemplate can then
  extract the macros for single viewlets or views.  If no macro is given the whole
  template is used for rendering.
  Default: empty

* mars.template.content_type(name):
  The content type identifies the type of data.
  Default: text/html

Also the mars.layer directive may be used
-----------------------------------------

* mars.layer.layer(class_or_interface):
  The layer for which the template should be available.
  This directive can be used at module level
  Default: zope.publisher.browser.interfaces.IDefaultBrowserLayer

Relevant grok directives
------------------------

* grok.template(path):
  This is used different to IGrokDirectives.template. It looks up the file
  containing the page template using the path relative to the current module, if
  not found it tries `path` as an absolute path, if not found GrokError is
  raised. The file should end in extensions ``.pt`` or ``.html``.
  **Required**

* grok.name(name):
  If defined the template will be registered as a `named adapter`.
  Default: empty string

* grok.context(class_or_interface):
  The view for which the template should be available. Usually should be
  defined.
  Default: module context

* grok.provides(interface):
  Explicitly specify with which interface a component will be looked up.
  Default: zope.pagetemplate.interfaces.IPageTemplate for TemplateFactory
           z3c.template.interfaces.ILayoutTemplate for LayoutFactory

