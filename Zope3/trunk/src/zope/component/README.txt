Zope Component Architecture
===========================

This package, together with `zope.interface`, provides facilities for
defining, registering and looking up components.  There are two basic
kinds of components: adapters and utilities.

Utilities
---------

Utilities are just components that provide an interface and that are
looked up by an interface and a name.  Let's look at a trivial utility
definition:

    >>> import zope.interface

    >>> class IGreeter(zope.interface.Interface):
    ...     def greet():
    ...         "say hello"

    >>> class Greeter:
    ...     zope.interface.implements(IGreeter)
    ...
    ...     def __init__(self, other="world"):
    ...         self.other = other
    ...
    ...     def greet(self):
    ...         print "Hello", self.other

We can register an instance this class using `provideUtility` [1]_:

    >>> import zope.component
    >>> greet = Greeter('bob')
    >>> zope.component.provideUtility(greet, IGreeter, 'robert')

In this example we registered the utility as providing the `IGreeter`
interface with a name of 'bob'. We can look the interface up with
either `queryUtility` or `getUtility`:

    >>> zope.component.queryUtility(IGreeter, 'robert').greet()
    Hello bob

    >>> zope.component.getUtility(IGreeter, 'robert').greet()
    Hello bob

`queryUtility` and `getUtility` differ in how failed lookups are handled:

    >>> zope.component.queryUtility(IGreeter, 'ted')
    >>> zope.component.queryUtility(IGreeter, 'ted', 42)
    42
    >>> zope.component.getUtility(IGreeter, 'ted')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: (<InterfaceClass ...IGreeter>, 'ted')

If a component provides only one interface, as in the example above,
then we can omit the provided interface from the call to `provideUtility`:

    >>> ted = Greeter('ted')
    >>> zope.component.provideUtility(ted, name='ted')
    >>> zope.component.queryUtility(IGreeter, 'ted').greet()
    Hello ted

The name defaults to an empty string:

    >>> world = Greeter()
    >>> zope.component.provideUtility(world)
    >>> zope.component.queryUtility(IGreeter).greet()
    Hello world

Adapters
--------

Adapters are components that are computed from other components to
adapt them to some interface.  Because they are computed from other
objects, they are provided as factories, usually classes.  Here, we'll
create a greeter for persons, so we can provide personalized greetings
for different people:

    >>> class IPerson(zope.interface.Interface):
    ...     name = zope.interface.Attribute("Name")

    >>> class PersonGreeter:
    ...
    ...     zope.component.adapts(IPerson)
    ...     zope.interface.implements(IGreeter)
    ...
    ...     def __init__(self, person):
    ...         self.person = person
    ...
    ...     def greet(self):
    ...         print "Hello", self.person.name

The class defines a constructor that takes an argument for every
object adapted.

We use `zope.component.adapts` to declare what we adapt.  If we
declare the interfaces adapted and if we provide only one interface,
as in the example above, then we can provide the adapter very simply [1]_:

    >>> zope.component.provideAdapter(PersonGreeter)

For adapters that adapt a single interface to a single interface
without a name, we can get the adapter by simply calling the
interface:

    >>> class Person:
    ...     zope.interface.implements(IPerson)
    ...
    ...     def __init__(self, name):
    ...         self.name = name

    >>> IGreeter(Person("Sally")).greet()
    Hello Sally

We can also provide arguments to be very specific about what
how to register the adapter.

    >>> class BobPersonGreeter(PersonGreeter):
    ...     name = 'Bob'
    ...     def greet(self):
    ...         print "Hello", self.person.name, "my name is", self.name

    >>> zope.component.provideAdapter(
    ...                        BobPersonGreeter, [IPerson], IGreeter, 'bob')

The arguments can also be provided as keyword arguments:

    >>> class TedPersonGreeter(BobPersonGreeter):
    ...     name = "Ted"

    >>> zope.component.provideAdapter(
    ...     factory=TedPersonGreeter, adapts=[IPerson],
    ...     provides=IGreeter, name='ted')

For named adapters, use `queryAdapter`, or `getAdapter`:

    >>> zope.component.queryAdapter(Person("Sally"), IGreeter, 'bob').greet()
    Hello Sally my name is Bob

    >>> zope.component.getAdapter(Person("Sally"), IGreeter, 'ted').greet()
    Hello Sally my name is Ted

If an adapter can't be found, `queryAdapter` returns a default value
and `getAdapter` raises an error:

    >>> zope.component.queryAdapter(Person("Sally"), IGreeter, 'frank')
    >>> zope.component.queryAdapter(Person("Sally"), IGreeter, 'frank', 42)
    42
    >>> zope.component.getAdapter(Person("Sally"), IGreeter, 'frank')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: (...Person...>, <...IGreeter>, 'frank')

Adapters can adapt multiple objects:

    >>> class TwoPersonGreeter:
    ...
    ...     zope.component.adapts(IPerson, IPerson)
    ...     zope.interface.implements(IGreeter)
    ...
    ...     def __init__(self, person, greeter):
    ...         self.person = person
    ...         self.greeter = greeter
    ...
    ...     def greet(self):
    ...         print "Hello", self.person.name
    ...         print "my name is", self.greeter.name

    >>> zope.component.provideAdapter(TwoPersonGreeter)

To look up a multi-adapter, use either `queryMultiAdapter` or
`getMultiAdapter`:

    >>> zope.component.queryMultiAdapter((Person("Sally"), Person("Bob")),
    ...                                  IGreeter).greet()
    Hello Sally
    my name is Bob


.. [1] CAUTION: This API should only be used from test or
       application-setup code. This API shouldn't be used by regular
       library modules, as component registration is a configuration
       activity.
