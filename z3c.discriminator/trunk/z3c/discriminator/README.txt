z3c.discriminator
=================

This package provides a formalism for designating adapter arguments as
discriminators in the sense that they will be used only for adapter lookup,
not instantiation.

  >>> from zope import interface

First a set of interfaces and their implementations.
  
  >>> class IFoo(interface.Interface):
  ...   pass

  >>> class IBar(interface.Interface):
  ...   pass

  >>> class Foo(object):
  ...   interface.implements(IFoo)

  >>> class Bar(object):
  ...   interface.implements(IBar)

Let's say we want to register an adapter for IFoo that also discriminates
on IBar.

  >>> def give_me_foo(foo):
  ...   return foo

We can use the ``discriminator`` method the decorate the interface as a
discriminator. To register the adapter we use a custom ``provideAdapter``
method that is basically a wrapper around the actual implementation from
``zope.component``.

  >>> from z3c.discriminator import discriminator
  >>> from z3c.discriminator import provideAdapter

  >>> provideAdapter(give_me_foo, (IFoo, discriminator(IBar)), IFoo)

Let's look up the adapter with the proper arguments.

  >>> foo = Foo()
  >>> bar = Bar()

  >>> from zope import component
  >>> component.getMultiAdapter((foo, bar), IFoo)
  <Foo object at ...>

Extended adapter directive
--------------------------

The discriminator extension is also available from ZCML. The convention
is that if a dotted interface specification is prefaced by a minus
sign, it's interpreted as a discriminator, e.g.

  for="-some.package.ISomeInterface"
  
The ``clearZCML`` method sets up the extended adapter directive.

  >>> from z3c.discriminator.tests import clearZCML
  >>> clearZCML()

Let's register an adapter for IBar that also discriminates on IFoo.

  >>> def give_me_bar(bar):
  ...   return bar

We need to patch our definitions onto the tests module to target
them from the configuration string.
  
  >>> import z3c.discriminator.tests
  >>> z3c.discriminator.tests.IBar = IBar
  >>> z3c.discriminator.tests.IFoo = IFoo
  >>> z3c.discriminator.tests.give_me_bar = give_me_bar

  >>> from cStringIO import StringIO
  >>> from zope.configuration import xmlconfig

  >>> xmlconfig.xmlconfig(StringIO("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ... <adapter for="-z3c.discriminator.tests.IFoo
  ...               z3c.discriminator.tests.IBar"
  ...          provides="z3c.discriminator.tests.IBar"
  ...          factory="z3c.discriminator.tests.give_me_bar" />
  ... </configure>
  ... """))
  
  >>> component.getMultiAdapter((foo, bar), IBar)
  <Bar object at ...>
