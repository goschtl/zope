Overview
--------

z3c.discriminator provides a formalism for marking adapter specifications as
discriminators in the sense that they will be used only for adapter lookup,
not instantiation.

Using z3c.discriminator
-----------------------

To mark one or more interfaces as discriminators in a ``provideAdapter`` call,
simply wrap your interface with the ``discriminator`` method:

  >>> from z3c.discriminator import discriminator
  >>> provideAdapter(MyAdapter, (IFoo, discriminator(IBar)))

To do the same in a Zope configuration file, prefix your dotted path with a
dash like so:

  <adapter for="IFoo -IBar" factory="some.package.YourFactory" />
  
Note that any interface in the declaration can be made a discriminator; they
need not come in any particular order.

In your factory definition, simply require only the arguments that correspond
to non-discriminator specifications, e.g.

  class GetsOnlyFoo(object):
      def __init__(self, foo):
          ...

   -or-

   def gets_only_bar(bar):
       ...

	  
