.. _man-zca:

Zope Component Architecture
===========================

Introdction
-----------

`Zope Component Architecture (ZCA)` is a framework for supporting
component based design and programming.  It is very well suited to
developing large Python software systems.  The ZCA is not specific to
the BlueBream: it can be used for developing any Python application.

The ZCA is all about using Python objects effectively.  Components
are reusable objects with introspectable interfaces.  A component
provides an interface implemented in a class, or any other callable
object.  It doesn't matter how the component is implemented, the
important part is that it comply with its interface contracts.  Using
ZCA, you can spread the complexity of systems over multiple
cooperating components.  It helps you to create two basic kinds of
components: `adapter` and `utility`.

There are two core packages related to the ZCA:

* `zope.interface` is used to define the interface of a component.

* `zope.component` deals with registration and retrieval of
  components.

Remember, the ZCA is not about the components themselves, rather it
is about creating, registering, and retrieving components.  Remember
also, an `adapter` is a normal Python class (or a factory in general)
and `utility` is a normal Python callable object.

The ZCA framework was developed as part of the BlueBream project.  As
noted earlier, it is a pure Python framework, so it can be used in
any kind of Python application.  There are many projects including
non-web applications using it.

Adapters
--------

Implementation
~~~~~~~~~~~~~~

This section will describe adapters in detail.  Zope component
architecture, as you noted, helps to effectively use Python objects.
Adapter components are one of the basic components used by Zope
component architecture for effectively using Python objects.  Adapter
components are Python objects, but with well defined interface.

To declare a class is an adapter use `adapts` function defined in
`zope.component` package.  Here is a new `FrontDeskNG` adapter with
explicit interface declaration::

  >>> from zope.interface import implements
  >>> from zope.component import adapts

  >>> class FrontDeskNG(object):
  ...
  ...     implements(IDesk)
  ...     adapts(IGuest)
  ...
  ...     def __init__(self, guest):
  ...         self.guest = guest
  ...
  ...     def register(self):
  ...         guest = self.guest
  ...         next_id = get_next_id()
  ...         bookings_db[next_id] = {
  ...         'name': guest.name,
  ...         'place': guest.place,
  ...         'phone': guest.phone
  ...         }

What you defined here is an `adapter` for `IDesk`, which adapts
`IGuest` object.  The `IDesk` interface is implemented by
`FrontDeskNG` class.  So, an instance of this class will provide
`IDesk` interface.

::

  >>> class Guest(object):
  ...
  ...     implements(IGuest)
  ...
  ...     def __init__(self, name, place):
  ...         self.name = name
  ...         self.place = place

  >>> jack = Guest("Jack", "Bangalore")
  >>> jack_frontdesk = FrontDeskNG(jack)

  >>> IDesk.providedBy(jack_frontdesk)
  True

The `FrontDeskNG` is just one adapter you created, you can also
create other adapters which handles guest registration differently.


Registration
~~~~~~~~~~~~

To use this adapter component, you have to register this in a
component registry also known as site manager.  A site manager
normally resides in a site.  A site and site manager will be more
important when developing a Zope 3 application.  For now you only
required to bother about global site and global site manager ( or
component registry).  A global site manager will be in memory, but a
local site manager is persistent.

To register your component, first get the global site manager::

  >>> from zope.component import getGlobalSiteManager
  >>> gsm = getGlobalSiteManager()
  >>> gsm.registerAdapter(FrontDeskNG,
  ...                     (IGuest,), IDesk, 'ng')

To get the global site manager, you have to call
`getGlobalSiteManager` function available in `zope.component`
package.  In fact, the global site manager is available as an
attribute (`globalSiteManager`) of `zope.component` package.  So, you
can directly use `zope.component.globalSiteManager` attribute.  To
register the adapter in component, as you can see above, use
`registerAdapter` method of component registry.  The first argument
should be your adapter class/factory.  The second argument is a tuple
of `adaptee` objects, i.e, the object which you are adapting.  In
this example, you are adapting only `IGuest` object.  The third
argument is the interface implemented by the adapter component.  The
fourth argument is optional, that is the name of the particular
adapter.  Since you gave a name for this adapter, this is a `named
adapter`.  If name is not given, it will default to an empty string
('').

In the above registration, you have given the adaptee interface and
interface to be provided by the adapter.  Since you have already
given these details in adapter implementation, it is not required to
specify again.  In fact, you could have done the registration like
this::

  >>> gsm.registerAdapter(FrontDeskNG, name='ng')

There are some old API to do the registration, which you should
avoid.  The old API functions starts with `provide`, eg:
`provideAdapter`, `provideUtility` etc.  While developing a Zope 3
application you can use Zope configuration markup language (ZCML) for
registration of components.  In Zope 3, local components (persistent
components) can be registered from Zope Management Interface (ZMI) or
you can do it programmatically also.

You registered `FrontDeskNG` with a name `ng`.  Similarly you can
register other adapters with different names.  If a component is
registered without name, it will default to an empty string.


Querying adapter
~~~~~~~~~~~~~~~~

Retrieving registered components from component registry is achieved
through two functions available in `zope.component` package.  One of
them is `getAdapter` and the other is `queryAdapter`.  Both functions
accepts same arguments.  The `getAdapter` will raise
`ComponentLookupError` if component lookup fails on the other hand
queryAdapter will return `None`.

You can import the methods like this::

  >>> from zope.component import getAdapter
  >>> from zope.component import queryAdapter

In the previous section you have registered a component for guest
object (adaptee) which provides `IDesk` interface with name as `ng`.
In the first section of this chapter, you have created a guest object
named `jack`.

This is how you can retrieve a component which adapts the interface
of jack object (`IGuest`) and provides `IDesk` interface also
with name as `ng`.  Here both `getAdapter` and
`queryAdapter` works similarly::

  >>> getAdapter(jack, IDesk, 'ng') #doctest: +ELLIPSIS
  <FrontDeskNG object at ...>
  >>> queryAdapter(jack, IDesk, 'ng') #doctest: +ELLIPSIS
  <FrontDeskNG object at ...>

As you can see, the first argument should be adaptee then, the
interface which should be provided by component and last the name of
adapter component.

If you try to lookup the component with an name not used for
registration but for same adaptee and interface, the lookup will fail.
Here is how the two methods works in such a case::

  >>> getAdapter(jack, IDesk, 'not-exists') #doctest: +ELLIPSIS
  Traceback (most recent call last):
  ...
  ComponentLookupError: ...
  >>> reg = queryAdapter(jack,
  ...           IDesk, 'not-exists') #doctest: +ELLIPSIS
  >>> reg is None
  True

As you can see above, `getAdapter` raised a
`ComponentLookupError` exception, but `queryAdapter`
returned `None` when lookup failed.

The third argument, the name of registration, is optional.  If the
third argument is not given it will default to empty string ('').
Since there is no component registered with an empty string,
`getAdapter` will raise `ComponentLookupError`.  Similarly
`queryAdapter` will return `None`, see yourself how it
works::

  >>> getAdapter(jack, IDesk) #doctest: +ELLIPSIS
  Traceback (most recent call last):
  ...
  ComponentLookupError: ...
  >>> reg = queryAdapter(jack, IDesk) #doctest: +ELLIPSIS
  >>> reg is None
  True

In this section you have learned how to register a simple adapter and
how to retrieve it from component registry.  These kind of adapters is
called single adapter, because it adapts only one adaptee.  If an
adapter adapts more that one adaptee, then it is called multi adapter.


Retrieving adapter using interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapters can be directly retrieved using interfaces, but it will only
work for non-named single adapters.  The first argument is the adaptee
and the second argument is a keyword argument.  If adapter lookup
fails, second argument will be returned.

::

  >>> IDesk(jack, alternate='default-output')
  'default-output'

  Keyword name can be omitted:

  >>> IDesk(jack, 'default-output')
  'default-output'

  If second argument is not given, it will raise `TypeError`:

  >>> IDesk(jack) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt',
    <Guest object at ...>,
    <InterfaceClass __builtin__.IDesk>)

  Here `FrontDeskNG` is registered without name:

  >>> gsm.registerAdapter(FrontDeskNG)

  Now the adapter lookup should succeed:

  >>> IDesk(jack, 'default-output') #doctest: +ELLIPSIS
  <FrontDeskNG object at ...>

For simple cases, you may use interface to get adapter components.


Utility
-------

Now you know the concept of interface, adapter and component registry.
Sometimes it would be useful to register an object which is not
adapting anything.  Database connection, XML parser, object returning
unique Ids etc. are examples of these kinds of objects.  These kind of
components provided by the ZCA are called `utility` components.

Utilities are just objects that provide an interface and that are
looked up by an interface and a name.  This approach creates a global
registry by which instances can be registered and accessed by
different parts of your application, with no need to pass the
instances around as parameters.

You need not to register all component instances like this.  Only
register components which you want to make replaceable.


Simple utility
~~~~~~~~~~~~~~

A utility can be registered with a name or without a name.  A utility
registered with a name is called named utility, which you will see in
the next section.  Before implementing the utility, as usual, define
its interface.  Here is a `greeter` interface::

  >>> from zope.interface import Interface
  >>> from zope.interface import implements

  >>> class IGreeter(Interface):
  ...
  ...     def greet(name):
  ...         """Say hello"""

Like an adapter a utility may have more than one implementation.  Here
is a possible implementation of the above interface::

  >>> class Greeter(object):
  ...
  ...     implements(IGreeter)
  ...
  ...     def greet(self, name):
  ...         return "Hello " + name

The actual utility will be an instance of this class.  To use this
utility, you have to register it, later you can query it using the ZCA
API.  You can register an instance of this class (`utility`) using
`registerUtility`::

  >>> from zope.component import getGlobalSiteManager
  >>> gsm = getGlobalSiteManager()

  >>> greet = Greeter()
  >>> gsm.registerUtility(greet, IGreeter)

In this example you registered the utility as providing the `IGreeter`
interface.  You can look the interface up with either `queryUtility`
or `getUtility`::

  >>> from zope.component import queryUtility
  >>> from zope.component import getUtility

  >>> queryUtility(IGreeter).greet('Jack')
  'Hello Jack'

  >>> getUtility(IGreeter).greet('Jack')
  'Hello Jack'

As you can see, adapters are normally classes, but utilities are
normally instances of classes.  Only once you are creating the
instance of a utility class, but adapter instances are dynamically
created whenever you query for it.


Named utility
~~~~~~~~~~~~~

When registering a utility component, like adapter, you can use a
name.  As mentioned in the previous section, a utility registered with
a particular name is called named utility.

This is how you can register the `greeter` utility with a name::

  >>> greet = Greeter()
  >>> gsm.registerUtility(greet, IGreeter, 'new')

In this example you registered the utility with a name as providing
the `IGreeter` interface.  You can look up the interface with either
`queryUtility` or `getUtility`::

  >>> from zope.component import queryUtility
  >>> from zope.component import getUtility

  >>> queryUtility(IGreeter, 'new').greet('Jill')
  'Hello Jill'

  >>> getUtility(IGreeter, 'new').greet('Jill')
  'Hello Jill'

As you can see here, while querying you have to use the `name` as
second argument.

Calling `getUtility` function without a name (second argument) is
equivalent to calling with an empty string as the name.  Because, the
default value for second (keyword) argument is an empty string.
Then, component lookup mechanism will try to find the component with
name as empty string, and it will fail.  When component lookup fails
it will raise `ComponentLookupError` exception.  Remember, it will
not return some random component registered with some other name.
The adapter look up functions, `getAdapter` and `queryAdapter` also
works similarly.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
