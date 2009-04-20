grok.admin.introspector
***********************

Introspect objects and applications.

:Test-Layer: functional

Introduction
============

The grokadmin introspector is built upon ``zope.introspector``. Its
purpose is to deliver in-depth information about applications, objects
and other thing existing in a running Grok environment.

Unlike ``zope.introspector`` this package also provides viewing
components to display all the information retrieved. Furthermore we
have the opportunity to get informed about aspects, which are specific
for Grok and/or Zope 3 like lists of available directives, used
grokkers etc.

The Grok introspector is context-oriented. That means, that it is able
to provide information about objects in specific contexts, so that you
can for example get a list of available views in the context of a
given skin/layer.

Basic Usage
===========

Although the Grok introspector is context-oriented, it also provides
an overview page as a starting point for general explorations of the
whole runtime environment.

Before we can access any pages, we have to initialize the test
browser::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.handleErrors = False

All introspector related content is shown in a special skin called
``inspect``, so that you can enter the following URL to access the
overview page::

  >>> browser.open('http://localhost/++inspect++/index.html')
  >>> print browser.contents
  <!DOCTYPE html...
  <h1>The Grok Introspector</h1>
  ...

Note the `++inspect++` marker in the URL.

The overview page provides three main sections to start browsing: 

- the registries

- code

- content

Browsing the registries
=======================

We can browse the registries by clicking on the provided link::

  >>> browser.getLink(
  ...  "Browse the registries (utilitites, adapters, etc.)").click()
  >>> print browser.contents
  <!DOCTYPE html...
  <h1>Registries</h1>
  ...

We get back to introspector home page::

  >>> browser.open('http://localhost/++inspect++/index.html')


Browsing code (classes, packages, etc.)
=======================================

The code browser assists in giving us an overview over the available
code basis. The overview page is where we can start::

  >>> browser.getLink(
  ... "Browse classes, packages and other filesystem based information"
  ... ).click()
  >>> print browser.contents
  <!DOCTYPE html...
  <h1>Code</h1>
  ...

The overview page provides already some starting points to explore the
whole code basis. We can go to the ``zope`` package::

  >>> zope_link = browser.getLink('Browse the zope package')
  >>> zope_link.click()
  
  >> print browser.contents
  <!DOCTYPE html...
  Package: <span>...zope...</span>
  ...

The system detected from the URL, that we wanted to get information
about the ``zope`` package. The link we clicked looks like this::

  >>> zope_link
  <Link ... url='http://localhost/++inspect++/+code/zope'>

This link is translated by the system to the dotted name `zope`, which
means to display the object, whose dotted name is 'zope'.

See `code.txt` to learn more about the code browser.

We get back to introspector home page::

  >>> browser.open('http://localhost/++inspect++/index.html')


Browsing content (ZODB items, etc.)
===================================

The content browser assists in giving us an overview over the
available content items. The overview page is where we can start::

  >>> browser.getLink(
  ... "Browse the content"
  ... ).click()
  >>> print browser.contents
  <html>
  ...
  <h1>...Content Introspector</h1>
  ...

From here we can start browsing the ZODB::

  >>> link = browser.getLink("ZODB root")
  >>> link.click()

All content introspection is done by simply watching an item via the
`inspect` view. So, to examine the ZODB root, we enter::

  >>> link.url
  'http://localhost/@@inspect'

To learn more about the content introspector, see `content.txt`.

We get back to introspector home page::

  >>> browser.open('http://localhost/++inspect++/index.html')
