z3c.discriminator
=================
  
This package provides a formalism for marking adapter specifications as
discriminators in the sense that they will be used only for adapter lookup,
not instantiation.

First a set of interfaces and their implementations.
  
  >>> from zope import interface
  
  >>> class IFoo(interface.Interface):
  ...   pass

  >>> class IBar(interface.Interface):
  ...   pass

  >>> class Foo(object):
  ...   interface.implements(IFoo)

  >>> class Bar(object):
  ...   interface.implements(IBar)
  
  >>> foo = Foo()
  >>> bar = Bar()

Let's say we want to register an adapter for IFoo that also discriminates
on IBar. That is, the adapter itself takes only one argument (providing IFoo).

  >>> def give_me_foo(foo):
  ...   return foo

We can use the ``discriminator`` method the mark the interface as a
discriminator. Let's look at its properties:

  >>> from z3c.discriminator import discriminator
  >>> discriminator(IFoo).providedBy(foo)
  True

To register the adapter we use the standard ``provideAdapter`` method.

  >>> from zope import component
  >>> component.provideAdapter(give_me_foo, (IFoo, discriminator(IBar)), IFoo)

Let's look up the adapter providing both ``foo`` and ``bar``:

  >>> from zope import component
  >>> component.getMultiAdapter((foo, bar), IFoo)
  <Foo object at ...>

Adapter registration using ZCML
-------------------------------

Directives that use ``zope.configuration.fields.GlobalObject`` as the value
type for the global object parameters are automatically equipped to use
discriminators.

The convention is that if a dotted interface specification is prefaced by a dash,
it's interpreted as a discriminator, e.g.

  for="-some.package.ISomeInterface"
  
Let's try with the ``adapter`` directive. We'll register an adapter for IBar that
also discriminates on IFoo.

  >>> def give_me_bar(bar):
  ...   return bar

To make our symbols available from the configuration machine we patch it onto
the tests module.

  >>> import z3c.discriminator.tests
  >>> z3c.discriminator.tests.IBar = IBar
  >>> z3c.discriminator.tests.IFoo = IFoo
  >>> z3c.discriminator.tests.give_me_bar = give_me_bar

We must first load the meta directives from ``zope.component``.
  
  >>> from cStringIO import StringIO
  >>> from zope.configuration import xmlconfig
  >>> xmlconfig.XMLConfig('meta.zcml', component)()

Now we can Register the adapter.
  
  >>> xmlconfig.xmlconfig(StringIO("""
  ... <configure xmlns="http://namespaces.zope.org/zope">
  ... <adapter for="-z3c.discriminator.tests.IFoo
  ...               z3c.discriminator.tests.IBar"
  ...          provides="z3c.discriminator.tests.IBar"
  ...          factory="z3c.discriminator.tests.give_me_bar" />
  ... </configure>
  ... """))

Let's verify the adapter lookup:
  
  >>> component.getMultiAdapter((foo, bar), IBar)
  <Bar object at ...>
