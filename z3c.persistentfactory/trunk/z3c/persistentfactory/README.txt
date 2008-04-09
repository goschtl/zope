;-*-Doctest-*-

=====================
z3c.persistentfactory
=====================

The ZCA and the ZODB are a good combination where components require
persistent state.  ZCA factories or handlers typically retrieve any
persistent state required from the persistent objects being adapted.
If the persistent state required is not specific to the objects being
adapted, a common solution is to register a persistent utility which
is then looked up in the factory or handler.  The persistent utility
approach requires, however, that the one appropriate utility is looked
up which requires support in the ZCA registrations either in the
interface provided or the utility name.

In some cases, however, it is more consistent with the object oriented
semantics of Python and the ZCA to think of the factory or handler as
an instance method of a persistent object.  With this approach the
non-context specific persistent state can be accessed on self.

Instance Method Event Handler
=============================

One example where this may be useful is where some non-context
persistent state is tightly coupled to some event handlers in such a
way where instance methods are better semantics.

The Baz class uses the decorator in the python code.  Note that the
factory decorator must come before the declaration decorators so that
it will be run last and will reflect the declarations.

    >>> from z3c.persistentfactory import testing
    >>> baz = testing.Baz()

Register the persistent factory wrapped instance method as a handler.

    >>> from zope import component
    >>> component.provideHandler(factory=baz.factory)
 
The method adapts IFoo, so create an object providing IFoo to be used
as the event.

    >>> component.adaptedBy(baz.factory)
    (<InterfaceClass z3c.persistentfactory.testing.IFoo>,)

    >>> from zope import interface
    >>> foo = testing.Foo()
    >>> interface.alsoProvides(foo, testing.IFoo)

When the event is notified, the method is called with the event as an
argument.

    >>> import zope.event
    >>> zope.event.notify(foo)
    Called <bound method Baz.factory of
    <z3c.persistentfactory.testing.Baz object at ...>>
      args: (<z3c.persistentfactory.testing.Foo object at ...>,)
      kwargs: {}

Instance Method Adapter Factory
===============================

Another example is where an adapter factory needs to look up
persistent state specific to the objects being adapted but where that
state can't be stored on the adapted objects them selves.  The
component storing the shared persistent state can register one of it's
instance methods as the adapter factory which will look up the
necessary persistent state on self.

Register the persistent factory wrapped instance method as an adapter
factory.

    >>> component.provideAdapter(factory=baz.factory)
 
The method implements IBar.

    >>> tuple(interface.implementedBy(baz.factory))
    (<InterfaceClass z3c.persistentfactory.testing.IBar>,)

When the adapter is looked up, the metod is called with the object to
be adapted as an argument.

    >>> result = component.getAdapter(foo, testing.IBar)
    Called <bound method Baz.factory of
    <z3c.persistentfactory.testing.Baz object at ...>>
      args: (<z3c.persistentfactory.testing.Foo object at ...>,)
      kwargs: {}
    >>> result
    (<bound method Baz.factory of
     <z3c.persistentfactory.testing.Baz object at ...>>,
     (<z3c.persistentfactory.testing.Foo object at ...>,), {})
