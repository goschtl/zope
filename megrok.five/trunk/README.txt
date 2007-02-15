megrok.five
===========

``megrok.five`` provides integration of the grok_ library into Zope 2.
Currently it supports:

* adapters, utilities, annotations (they're generic to both Zope 2 and 3)

* views (``grok.View``) with Page Templates

* forms (``grok.EditForm``, ``grok.AddForm``)

It also supplies two new base classes, ``Model`` and ``Container``,
which are Zope 2-enabled versions of their grok equivalents.  In
particular:

* ``megrok.five.Model`` is not only a persistent objects (like
  grok.Model is), but it's also a Zope 2 "SimpleItem", allowing it to
  properly exist in a Zope 2 environment.

* ``megrok.five.Container`` is a Zope 2 "ObjectManager" but also
  implements the ``IContainer`` interface from Zope 3, which is
  essentially the dictionary API.  The following table compares the
  old ObjectManager API with the ``IContainer`` API:

  ================================  =======================
  (Old) ObjectManager spelling      IContainer spelling
  ================================  ========================
  folder.objectIds()                folder.keys()
  folder.objectValues()             folder.values()
  folder.objectItems()              folder.items()
  getattr(folder, name)             folder[name], folder.get(name, default)
  folder._setObject(name, obj)      folder[name] = obj
  folder.manage_delObjects([name])  del folder[name]
  folder.hasObject(name)            name in folder
  for name in folder.objectIds():   for name in folder
  ================================  ========================

  Note that this implies that ``megrok.five.Containers`` may not have
  subobjects called ``keys``, ``values``, ``items``, etc. because Zope
  2 uses attribute access to traverse to subobjects.

  .. TODO perhaps provide a custom traverser for megrok.five.Container
  .. that deals with this issue?

.. _grok: http://cheeseshop.python.org/pypi/grok
