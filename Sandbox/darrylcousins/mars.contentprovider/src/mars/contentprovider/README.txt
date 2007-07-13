====================
Mars ContentProvider
====================

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration information in
Python code. Martian can then grok the system and do the appropriate
configuration registrations.

.. _Grok: http://grok.zope.org/

Mars ContentProvider
--------------------

Martian is a library that allows the embedding of configuration
information in Python code. Martian can then grok the system and
do the appropriate configuration registrations.

The mars.contentprovider package provides the means of creating and configuring
``contentproviders`` for an application using Zope3.

Example Code
------------

::
 import mars.view
 import mars.template
 import mars.contentprovider

 class Index(mars.view.LayoutView):
     pass

 class IndexLayout(mars.template.LayoutFactory):
     grok.template('index.pt')
     grok.context(Index)

 class Title(mars.contentprovider.ContentProvider):

     def render(self):
         return self.context.title

Template for index may be::

 <tal:block tal:content="structure provider:title" />

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
  defined if a template has been registered as a named adapter.
  Default: ''

* grok.provides(class_or_interface):
  Interface the class is looked up as, probably wouldn't be used.
  Default: zope.interface.Interface

Tests
-----

See test directory.


