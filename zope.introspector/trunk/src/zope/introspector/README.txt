zope.introspector
*****************

An introspector for Zope.

:Test-Layer: nonunit

The `zope.introspector` package provides an extensible framework
for retrieving 'data' on 'entities'. It makes use of
grokcore.component for registration of adapters and utilities.

'Entity' in that respect means everything, that is descriptable by a
name in Python or everything, that can be passed to a method. In other
words: if you can pass something to a callable, then the introspector
should be able to give you some information about it.

'Data' in that respect means a container containing a set of data,
describing the given entity. The container might contain primitive
values (like numbers or strings) as well as more complex objects,
callables etc.

In plain words: Given a certain object you get a dataset describing
it.

Support for modification of objects (for instance for debugging
purposes) is still not implemented. This package also does not include
viewing components to display the results.


Inspecting Objects
===================

Because many objects have many different aspects that can be examined,
we provide a set of 'examiners', each one responsible for a certain
aspect.

Currently, the following introspectors are available

* ``ObjectInfo`` and relatives

  Gives you information about simple and built-in types like strings,
  classes, packages and functions. See `objectinfo.txt` to learn more
  about that.

* ``UtilityInfo`` and relatives

  Gives you information about the utilities that are available for a
  certain objects. See `utilityinfo.txt` to learn more about that.


Code objects
------------

Code objects are such, that provide information about packages,
classes and other pieces of code. We can retrieve informations about
packages::

  >>> import grokcore.component as grok
  >>> grok.grok('zope.introspector')
  >>> 


Writing your own introspector
=============================

Writing an introspector means providing a component (the ``Info``
component), that delivers information about certain kinds of objects
and another component (the ``DescriptionProvider`` component), that
decides for an arbitrary object, whether it can be decribed by your
new ``Info`` component.

Step 1: Writing an ``Info`` component
-------------------------------------

An Info component can be a simple object. We define a class, whose
instances should be described afterwards::

  >>> class Mammoth(object):
  ...   def __init__(self, name='Fred'):
  ...     self.name=name

An accompanied ``Info`` component now could look like this::

  >>> class MammothInfo(object):
  ...   def __init__(self, obj):
  ...     self.obj = obj
  ...   def getName(self):
  ...     return self.obj.name

Apparently this class gives us interesting informations about
mammoths::

  >>> fred = Mammoth()
  >>> fred.name
  'Fred'

The trick now is to make this ``Info`` available in the framework when
a ``Mammoth`` object should be described. This is currently not the
case. We generally look up infos for objects using an utility
providing ``IObjectDescriptionProvider`` interface::

  >>> from zope.component import getUtility
  >>> from zope.introspector.interfaces import IObjectDescriptionProvider
  >>> info_provider = getUtility(IObjectDescriptionProvider)

When we ask this provider for infos about fred, we will get one of the
default ``Info`` components::
  
  >>> info_provider.getDescription(fred)
  <zope.introspector.objectinfo.ObjectInfo object at 0x...>

Instead of this ``ObjectInfo`` we want to get our new ``MammothInfo``
returned. To let this happen, we first have to register it by writing
a ``DescriptionProvider``.


Step 2: Writing an ``DescriptionProvider``
------------------------------------------

``DescriptionProviders`` are built by inheriting from
``zope.introspector.DescriptionProvider``. They provide a
``canHandle()`` and a ``getDescription()`` method::

  >>> from zope.introspector import DescriptionProvider

  >>> class MammothDescriptionProvider(DescriptionProvider):
  ...   def canHandle(self, obj, *args, **kw):
  ...     if isinstance(obj, Mammoth):
  ...       return True
  ...     return False
  ...   def getDescription(self, obj, *args, **kw):
  ...     return MammothInfo(obj)

If we ask this class whether it can handle a ``Mammoth`` instance, it
will agree::

  >>> mdp = MammothDescriptionProvider()
  >>> mdp.canHandle(fred)
  True

For other objects it should fail::

  >>> mdp.canHandle(object())
  False

We can also get a description::

  >>> mdp.getDescription(fred)
  <MammothInfo object at 0x...>

This is all very well, but how can the framework know, that we have a
ready-to-use description provider for mammoths? The
``zope.introspector`` package uses grokkers from the ``martian``
package to find description providers on startup. Before grokking a
module with a description provider, the latter will be unknown to the
framework::

  >>> info_provider.getDescription(fred)
  <zope.introspector.objectinfo.ObjectInfo object at 0x...>

This means, that we have to grok all modules and classes, that contain
description providers::

  >>> import grokcore.component as grok
  >>> grok.testing.grok('zope.introspector')
  >>> grok.testing.grok_component('MammothDescriptionProvider',
  ...                             MammothDescriptionProvider)
  True

If we now repeat our request to the global info provider, we get the
descriptor we want::

  >>> info_provider.getDescription(fred)
  <MammothInfo object at 0x...>


We remove the MammothInfo handler to clean up the registry::

  >>> import zope.introspector.descriptionprovider as zid
  >>> zid.descriptor_registry =  [x for x in zid.descriptor_registry
  ...     if not x['handler'] is MammothDescriptionProvider]

