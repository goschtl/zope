;-*-Doctest-*-
===================
Component Debugging
===================

The Zope component registry is a black box in normal operation.
Requests are made of the registry for components appropriate to the
request and it returns them.  If something goes wrong, it raises
ComponentLookupError.  This is very much as it should be since the
inner workings of the registry should no more be apart of application
design than should the inner workings of Python.

In the process, however, of developing an application that uses the
registry, it is often desirable to have more introspection of the
registry available.

Component Debugging provides a set of tools for inspecting the
component registry of site managers.  It also provides a patch that
catches various different ComponentLookupError exceptions and adds
more verbose reporting.

--------------------
Component Inspection
--------------------

A set of interfaces are needed to demonstrate the inspection
functions::

    >>> from zope.interface import Interface
    >>> class IFoo(Interface): pass
    >>> class IBar(Interface): pass
    >>> class IBaz(Interface): pass

reportRequiredAdapters
----------------------

reportRequiredAdapters provides inspection of registrations that
provide a specific interface.  Unlike
zope.app.apidoc.getRequiredAdapters, however, it takes a list of
objects to adapt and for each object reports which registrations
require an interface provided by that object for the correct position
in the list of objects.

Start with some objects that provide some interfaces::

    >>> from zope.interface import alsoProvides
    >>> class Foo(object): pass
    >>> foo = Foo()
    >>> alsoProvides(foo, IFoo)
    >>> class Bar(object): pass
    >>> bar = Bar()
    >>> alsoProvides(bar, IBar)

At this point there's nothing in the registry::

    >>> from zope.component import queryMultiAdapter
    >>> queryMultiAdapter((foo, bar), IBaz)

    >>> from pprint import pprint
    >>> from z3c.componentdebug import reportRequiredAdapters
    >>> pprint([i for i in reportRequiredAdapters((foo, bar), IBaz)])
    [(<Foo object at ...>, {}), (<Bar object at ...>, {})]

Register a factory for this lookup::

    >>> from zope.component import provideAdapter
    >>> def getBaz(foo, bar): return 'baz'
    >>> provideAdapter(getBaz, (IFoo, IBar), IBaz)

Now the registrations can be inspected::

    >>> queryMultiAdapter((foo, bar), IBaz)
    'baz'
    
    >>> pprint([i for i in reportRequiredAdapters((foo, bar), IBaz)])
    [(<Foo object at ...>,
      {<InterfaceClass __builtin__.IFoo>:
      AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
      IBaz, '', getBaz, u'')}),
     (<Bar object at ...>,
      {<InterfaceClass __builtin__.IBar>:
      AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
      IBaz, '', getBaz, u'')})] 

When we remove one of the required interfaces, we can see what
regisration might have otherwise fulfilled the lookup::

    >>> from zope.interface import noLongerProvides
    >>> noLongerProvides(bar, IBar)

    >>> queryMultiAdapter((foo, bar), IBaz)
    
    >>> pprint([i for i in reportRequiredAdapters((foo, bar), IBaz)])
    [(<Foo object at ...>,
      {<InterfaceClass __builtin__.IFoo>:
      AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
      IBaz, '', getBaz, u'')}),
     (<Bar object at ...>, {})]
