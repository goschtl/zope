============
Mars Viewlet
============

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

This package uses martian to configure viewlets and viewletmanagers.

Example Code
------------

::

 ### the page that we are looking at
 class Index(mars.view.LayoutView):
     pass

 ### the template for index page
 class IndexLayout(mars.template.LayoutFactory):
     grok.template('index.pt') # required
     grok.context(Index) # required

 ### a manager registered for Mammoth and IModuleLayer
 class RightColumn(mars.viewlet.ViewletManager):

     def render(self):
         return u'Right column content'

 ### a second manager registered for Mammoth and IModuleLayer
 class LeftColumn(mars.viewlet.ViewletManager):
     """Joins output of viewlets"""
     pass

 ### viewlets for leftcolumn manager
 class FirstViewlet(mars.viewlet.Viewlet):
     """A simple viewlet"""
     grok.context(Mammoth)
     mars.viewlet.manager(LeftColumn)
     mars.viewlet.view(Index) # not required
     weight = 0

     def render(self):
         return u'<div>First viewlet content</div>'

 ### the second of which uses a template
 class SecondViewlet(mars.viewlet.Viewlet):
     """A viewlet that has its own template"""
     grok.context(Mammoth)
     mars.viewlet.manager(LeftColumn)
     weight = 1


Directives specific to this package
-----------------------------------

* mars.viewlet.manager(class_or_interface):
  The manager for which the viewlet is registered.
  Default: IViewletManager (?)

* mars.viewlet.view(class_or_interface):
  The view for which the viewlet is registered.
  Default: zope.publisher.interfaces.browser.IBrowserView

The mars.layer directive may be used
------------------------------------

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


