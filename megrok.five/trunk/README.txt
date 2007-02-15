Introduction
============

``megrok.five`` provides integration of grok_ into Zope 2.  Grok_ is a
library that makes it much easier to write Zope 3 web applications, in
particular writing and hooking up Zope 3-style components.  Thanks to
the Five_ project, it's already possible to write software using Zope
3-style components in Zope 2, so why shouldn't it be possible to do it
the grok_ way in Zope 2?  This is what ``megrok.five`` is about.

Features
========

``megrok.five`` supports all the major grok_ features:

* adapters, utilities, annotations (they're generic to both Zope 2 and 3)

* views (``grok.View``) with Page Templates

* forms (``grok.EditForm``, ``grok.AddForm``)

Writing a grok_ application on Zope 2 should therefore not be any
different than on Zope 3.  In fact, your grok_ applications should
work right away on Zope 2, with one exception: you'll have to use the
``Model`` and ``Container`` base classes from ``megrok.five``.  Those
are Zope 2-enabled versions of their grok equivalents.  In particular:

* ``megrok.five.Model`` is not only a persistent objects (like
  grok.Model is), but it's also a Zope 2 "SimpleItem", allowing your
  models to properly exist in a Zope 2 environment.

* ``megrok.five.Container`` is a Zope 2 "ObjectManager" but also
  implements the ``IContainer`` interface from Zope 3, which is
  essentially the dictionary API.  The following table compares the
  old ObjectManager API with the ``IContainer`` API:

  ================================  ========================
  (Old) ObjectManager spelling      IContainer spelling
  ================================  ========================
  folder.objectIds()                folder.keys()
  folder.objectValues()             folder.values()
  folder.objectItems()              folder.items()
  getattr(folder, name)             folder[name], folder.get(name, default)
  folder._setObject(name, obj)      folder[name] = obj
  folder.manage_delObjects([name])  del folder[name]
  folder.hasObject(name)            name in folder
  for name in folder.objectIds():   for name in folder:
  ================================  ========================

  Note that this implies that ``megrok.five.Containers`` may not have
  subobjects called ``keys``, ``values``, ``items``, etc. because Zope
  2 uses attribute access to traverse to subobjects.

  .. TODO perhaps provide a custom traverser for megrok.five.Container
  .. that deals with this issue?

.. _grok: http://cheeseshop.python.org/pypi/grok
.. _Five: http://codespeak.net/z3/five/

Installation
============

You need to install both the grok_ and ``megrok.five`` packages
somewhere in your ``PYTHONPATH``, e.g. in your instance's
``lib/python`` directory.  Note that they both depend on
``setuptools`` (which will be pulled in automatically if you decide to
do the installation via eggs).

You will then have to load ``grok``'s and ``megrok.five``'s
configuration (in that order!).  To do that, append the following two
lines to your instance's ``etc/site.zcml``::

  <include package="grok" file="meta.zcml" />
  <include package="megrok.five" />

*After* those lines you can add additional include statements to load
your application package's, e.g.::

  <include package="my.grok.app" />

if your package already contains a ``configure.zcml`` file, or
directly grok the package with the followign statement::

  <grok package="my.grok.app" xmlns="http://namespaces.zope.org/grok" />

If you're using "ZCML slugs" in ``etc/package-includes`` instead of
statements in ``etc/site.zcml`` , make sure the slugs are named
correctly so that first grok's meta configuration is loaded, then
``megrok.five`` and *then* your packages.

Developers
==========

If you'd like to get a development checkout of ``megrok.five``, get it
like so::

  $ svn co svn://svn.zope.org/repos/main/megrok.five/trunk megrok.five

This is a `zc.buildout`_-enabled sandbox, which means you can turn
this checkout into a completely functional Zope 2 setup with the
following commands::

  $ python2.4 bootstrap/bootstrap.py
  ... a bit of output here

  $ bin/buildout
  ... lots of output here, might take a moment

After that you can start Zope with::

  $ bin/instance fg

Log into the ZMI (user: ``admin``, password: ``admin``) and you'll
find a new type to add in the ZMI Add menu from the ``TodoList`` demo
application.

.. _zc.buildout: http://cheeseshop.python.org/pypi/zc.buildout
