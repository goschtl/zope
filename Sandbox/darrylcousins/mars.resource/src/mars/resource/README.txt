=============
Mars Resource
=============

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration information in
Python code. Martian can then grok the system and do the appropriate
configuration registrations.

.. _Grok: http://grok.zope.org/

Mars Resource
-------------

This package uses martian to configure resources and resource directories.

Example Code
------------

::

 # define a file resource
 class Style(mars.resource.ResourceFactory):
     grok.name('site.css')
     mars.resource.file('resources/site.css')

 # define an image resource
 class Logo(mars.resource.ResourceFactory):
     grok.name('logo.jpg')
     mars.resource.file('resources/logo.jpg')

 # define a resource directory, takes name from factory.__name__
 class Resources(mars.resource.ResourceDirectoryFactory):
     mars.resource.directory('resources')

Directives specific to this package
-----------------------------------

* mars.resource.file(name):
  Path to the resource
  **Required** one only of image or file for Resource

* mars.resource.image(name):
  Path to the resource
  **Required** one only of image or file for Resource

* mars.resource.directory(name):
  Path to the resource directory
  **Required** for ResourceDirectory

Also the mars.layer directive may be used
-----------------------------------------

* mars.layer.layer(class_or_interface):
  The layer for which the template should be available.
  Default: zope.publisher.browser.interfaces.IDefaultBrowserLayer

Relevant grok directives
------------------------

* grok.name(name):
  Name by which resource or resource directory is located
  **Required**

[And possibly grok.require??]

Tests
-----

See test directory.


