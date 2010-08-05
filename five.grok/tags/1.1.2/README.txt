five.grok
=========

.. contents::

Introduction
------------

`five.grok` is a development layer for Zope 2, based on Grok framework
concepts.

The development techniques are similar to the ones used with Grok
framework.

It is based on `grokcore` namespace packages that were factored out of Grok
framework.

Implemented features
--------------------

Coming from Grok, the following components are available to Zope 2
developers:

- Zope 3 Component (Adapter, Global utilities, Subscribers),

- Permissions,

- Views and Viewlets,

- Skins and resources directories,

- Page Templates (using the Zope 2 Page Templates),

- Formlib forms,

- Local sites and local utilities,

- Annotations.

All those components are available with exactly the same syntax than
in grok. You just have to do::

  from five import grok

Instead of::

  import grok

Installation
------------

After adding the dependency to ``five.grok`` in your project, you have
to load the following ZCML::

  <include package="five.grok" />

Note
~~~~

And for this release we recommend to pin down the following version in
your buildout::

  grokcore.annotation = 1.2
  grokcore.component = 1.8
  grokcore.formlib = 1.5
  grokcore.security = 1.4
  grokcore.site = 1.2
  grokcore.view = 1.12.2
  grokcore.viewlet = 1.4.1
  five.localsitemanager = 2.0.3
  martian = 0.11.2

Zope 2.12 is required. If you wish to use a previous version of Zope
2, look at the version 1.0 of five.grok.


More information
----------------

You can refer to the Grok website: http://grok.zope.org/, and the Grok
documentation: http://grok.zope.org/documentation/.

You can check the doctest included in sources as well.
