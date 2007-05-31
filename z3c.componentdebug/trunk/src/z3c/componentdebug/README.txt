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

z3c.componentdebug.inspect provides inspection of registrations that
provide a specific interface.  Unlike zope.app.apidoc, it takes a list
of objects to adapt and for each object reports which registrations
require an interface provided by that object for the correct position
in the list of objects.  Also unlike zope.app.apidoc, it examines the
contents of all site managers in the resolution order.

Registrations are sorted first by the number of objects that match and
then by the specificity of the required interfaces.

Start with some objects that provide some interfaces::

    >>> from zope.interface import Interface
    >>> class IFoo(Interface): pass
    >>> class IBar(Interface): pass
    >>> class IBaz(Interface): pass

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
    >>> from z3c.componentdebug import inspect
    >>> registrations = inspect((foo, bar), IBaz)
    >>> pprint([i for i in registrations.byObject()])
    [(<Foo object at ...>, []), (<Bar object at ...>, [])]

Register a factory for this lookup::

    >>> from zope.component import provideAdapter
    >>> def getBaz(foo, bar): return 'baz'
    >>> provideAdapter(getBaz, (IFoo, IBar), IBaz)

Now the registrations can be inspected::

    >>> queryMultiAdapter((foo, bar), IBaz)
    'baz'
    
    >>> registrations = inspect((foo, bar), IBaz)
    >>> pprint(registrations)
    [AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
    IBaz, '', getBaz, u'')]
    >>> pprint([i for i in registrations.byObject()])
    [(<Foo object at ...>,
      [(<InterfaceClass __builtin__.IFoo>,
        [AdapterRegistration(<BaseGlobalComponents base>, [IFoo,
        IBar], IBaz, '', getBaz, u'')])]),
     (<Bar object at ...>,
      [(<InterfaceClass __builtin__.IBar>,
        [AdapterRegistration(<BaseGlobalComponents base>, [IFoo,
        IBar], IBaz, '', getBaz, u'')])])]

When we remove one of the required interfaces, we can see what
regisration might have otherwise fulfilled the lookup and which object
is the one that prevents the lookup from succeeding::

    >>> from zope.interface import noLongerProvides
    >>> noLongerProvides(bar, IBar)

    >>> queryMultiAdapter((foo, bar), IBaz)
    
    >>> registrations = inspect((foo, bar), IBaz)
    >>> pprint(registrations)
    [AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
    IBaz, '', getBaz, u'')]
    >>> pprint([i for i in registrations.byObject()])
    [(<Foo object at ...>,
      [(<InterfaceClass __builtin__.IFoo>,
        [AdapterRegistration(<BaseGlobalComponents base>, [IFoo,
        IBar], IBaz, '', getBaz, u'')])]),
     (<Bar object at ...>, [])]

--------------------
ComponentLookupError
--------------------

z3c.componentdebug.lookup includes patches to the zope.component
lookup API that provide more verbose reporting from
ComponentLookupError exceptions::

    >>> from zope.component import _api
    >>> _api.getMultiAdapter((foo, bar), IBaz)
    Traceback (most recent call last):
    ...
    ComponentLookupError: ((<Foo object at ...>, <Bar object at ...>),
    <InterfaceClass __builtin__.IBaz>, u'')

    >>> from z3c.componentdebug.lookup.patch import patch
    >>> patch()

    >>> _api.getMultiAdapter((foo, bar), IBaz)
    Traceback (most recent call last):
    ...
    VerboseComponentLookupError:
    [AdapterRegistration(<BaseGlobalComponents base>, [IFoo, IBar],
    IBaz, '', getBaz, u'')]
    [(<Foo object at ...>,
      [(<InterfaceClass __builtin__.IFoo>,
        [AdapterRegistration(<BaseGlobalComponents base>, [IFoo,
        IBar], IBaz, '', getBaz, u'')])]),
     (<Bar object at ...>, [])]

    >>> from z3c.componentdebug.lookup.patch import cleanup
    >>> cleanup()

    >>> _api.getMultiAdapter((foo, bar), IBaz)
    Traceback (most recent call last):
    ...
    ComponentLookupError: ((<Foo object at ...>, <Bar object at ...>),
    <InterfaceClass __builtin__.IBaz>, u'')
