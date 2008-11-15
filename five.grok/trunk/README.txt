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

- Zope 3 Component (Adapter, Utility, Subscribers),

- Permissions,

- Views and Viewlets,

- Skins and resources directories,

- Page Templates (using the Zope 2 Page Templates),

- Formlib forms.

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

``five.grok`` have some dependencies on Zope 3 eggs. With Zope 2, you
can fake those dependencies in buildout by using the option
``fake-zope-eggs = true`` of ``plone.recipe.zope2instance``. However,
``five.grok`` requires ``zope.component`` 3.4 at least. You can
exclude that egg by mentioning ``zope.component`` in the option
``skip-fake-eggs`` in the same buildout section.


More information
----------------

You can refer to the Grok website: http://grok.zope.org/, and the Grok
documentation: http://grok.zope.org/documentation/.

You can check the doctest included in sources as well.
