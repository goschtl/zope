============
Generic Face
============

This package provides interface types for key interfaces (IKeyfaceType) and 
context interfaces (IConfaceType). 

Typed interfaces can be used to register dedicated information providers 
(IInformationProvider see zope.generic.informationprovider). An information 
provider offers the possiblity to register information according to a pair of 
key- and context interfaces.

Key interface
-------------

The key interface is the one piece to lookup information providers. 

Within the system domain the key interface represents a permanent marker for an
object. For example the marked object *is* a person. Regularly you will mark
your content components with domain-specific key interfaces. Such a keyface 
(short for: key[ inter]face) has a similar relation like classes and its 
instances, therefore it can be used to type components.

The behavior of components within the ca-framework depends heavily on their
provided interfaces. A component, except most of the adapters and utilities, 
regularly provides more than one interface. The adaption and subscriber 
mechanism of the ca-framework invokes the provided interfaces by a 
lookup-algorithmus similar to the method resolution order by class inherintance.

Most of the time this behavior satisfies our requirements. Additionally this 
package offers a mechanism to declare a single key interface (IKeyface). This 
key interface can be used to lookup corresponding information providers
explicitly.

Context Interface
-----------------

The context interface is the other piece to lookup information providers. 

The context interface allows an more explicit comprehension and lookup of 
information related to key interfaces. Contexts of understanding are often 
changing within the same system domain. For example your *name* is changing 
within the system domain *world*: Within your childs context it will be 'Dad', 
within your wife's context it will be 'Darling', within your friend's context 
it will be 'Dude' and within the official context will be 'Mr. Foo Bar'.

The key- and contes interfaces provide the fundament to model more complex, 
contextual object-behavior and -properties. The package allows a dedicated, 
but generic registration of information providers, which can be used for
facing or casing your objects contextually.

How to define a context interface
---------------------------------

You can implement a context interface simply by deriving from zope's Interface
and typing it by IConfaceType.

    >>> class IMyContext(interface.Interface):
    ...    pass

    >>> interface.alsoProvides(IMyContext, api.IConfaceType)
    >>> api.IConfaceType.providedBy(IMyContext)
    True

Context interfaces are pure marker interfaces. They can be used to register
contextual information providers as utility providing the context interface.

Information providers that are not aware of a context should use 
IUndefinedContext:

    >>> api.IConfaceType.providedBy(api.IUndefinedContext)
    True

How to define a key interface
-----------------------------

You can implement a key interface simply by deriving from zope's Interface and 
typing it by IKeyfaceType.

    >>> class IFoo(interface.Interface):
    ...    pass

    >>> interface.alsoProvides(IFoo, api.IKeyfaceType)
    >>> api.IKeyfaceType.providedBy(IFoo)
    True

If no key interface is available regularly IUndefinedKeyface is provided:

    >>> api.IKeyfaceType.providedBy(api.IUndefinedKeyface)
    True

How to use the face mechanism
-----------------------------

The IFaced interface promises access to keyface and/or conface of an object.
The lookup of key and context interfaces is regularly done by component that
are providing IAttributeFaced.

Then we have to decorate a corresponding key-faced component:

    >>> class FooFaced(object):
    ...    interface.implements(api.IAttributeFaced)
    ...    __keyface__ = IFoo

There is a default adapter to IFace for key-faced objects:

    >>> foofaced = FooFaced()

    >>> adapted = api.IFace(foofaced)
    >>> adapted.keyface == IFoo
    True
    >>> adapted.conface == api.IUndefinedContext
    True

Furthermore there is simple Face mixin for AttributeFaced objects:

    >>> class FooFace(api.Face):
    ...    __conface__ = IMyContext

    >>> fooface = FooFace()
    >>> fooface.keyface == api.IUndefinedKeyface
    True
    >>> fooface.conface == IMyContext
    True

getKeyface
----------

The api provides convenience functions to get the key interfaces of components:

    >>> api.getKeyface(foofaced) == IFoo
    True
    >>> api.getKeyface(fooface) == api.IUndefinedKeyface
    True
    >>> api.getKeyface(object()) == api.IUndefinedKeyface
    True
    >>> api.getKeyface(object(), None) is None
    True

getConface
----------

The api provides convenience functions to get the context interfaces of components:

    >>> api.getConface(foofaced) == api.IUndefinedContext
    True
    >>> api.getConface(fooface) == IMyContext
    True
    >>> api.getConface(object()) == api.IUndefinedContext
    True
    >>> api.getConface(object(), None) is None
    True

InformationProvider Lookup
--------------------------

You can register information providers. This is done by the informationProvider
directive (see zope.generic.informationprovider). This package defines the
way those information providers can be looked up too.

An information provider should provide the contex interface itself. Further more
it is responsible to mark the key interface by the context interface:


    >>> class DummyInformationProvider(object):
    ...    def __init__(self, keyface, conface):
    ...        self.keyface = keyface
    ...        self.conface = conface
    ...        interface.alsoProvides(self, conface)
    ...        interface.alsoProvides(keyface, conface)
    ...    def __repr__(self):
    ...        return '<Information provider %s at %s>' % (self.keyface.__name__, self.conface.__name__)

    >>> def ensureInformationProvider(keyface, conface):
    ...    provider = DummyInformationProvider(keyface, conface)
    ...    component.provideUtility(provider, conface, api.toDottedName(keyface))
    ...    return provider

    >>> provider_1 = ensureInformationProvider(IFoo, api.IUndefinedContext)

    >>> api.IUndefinedContext.providedBy(IFoo)
    True
    >>> api.IUndefinedContext.providedBy(provider_1)
    True

Simple Lookup using queryInformationProvider and getInformationProvider
------------------------------------------------------------------------

    >>> api.getInformationProvider(IFoo)
    <Information provider IFoo at IUndefinedContext>

    >>> api.queryInformationProvider(IFoo)
    <Information provider IFoo at IUndefinedContext>

A key error is raised or the default is returned if no information provider 
could be evalutated for a certain key interface, context interface pair:

    >>> api.getInformationProvider(IFoo, IMyContext)
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

    >>> api.queryInformationProvider(IFoo, IMyContext, 'Missing information provider.')
    'Missing information provider.'

Attention information provider does not acquire from more specialized interface
like the regular utility lookup does:

    >>> class IYourContext(IMyContext):
    ...    pass

    >>> interface.alsoProvides(IYourContext, api.IConfaceType)

    >>> provider_2 = ensureInformationProvider(IFoo, IYourContext)

    >>> component.getUtility(IMyContext, api.toDottedName(IFoo))
    <Information provider IFoo at IYourContext>

    >>> api.getInformationProvider(IFoo, IMyContext)
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

Complex Lookup using acquireInformationProvider
-----------------------------------------------

You can use the acquireInformationProvider function to lookup more general
information providers. The acquisition is based on the __iro__ of the key and
context interface. You will start within the first context looking up all key
interface in order of the __iro__. If no information provider could be found
the context will be switch to the next more general context. There the same
procedure will start until an information provider could be found. If no
information could be found a key error is raised.

In our example we cannot acquire anything therefore we still expect a key error.

    >>> api.acquireInformationProvider(IFoo, IMyContext) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

We could derive a context from IUndefinedContext. That way we could acquire the
first provider registered to IFoo and IUndefinedContext:

    >>> class IOurContext(api.IUndefinedContext):
    ...    pass

    >>> interface.alsoProvides(IOurContext, api.IConfaceType)

    >>> api.getInformationProvider(IFoo, IOurContext) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IOurContext.'

    >>> api.acquireInformationProvider(IFoo, IOurContext)
    <Information provider IFoo at IUndefinedContext>

The other way round we can play with key interface inheritance:

    >>> class IBar(interface.Interface):
    ...    pass

    >>> interface.alsoProvides(IBar, api.IKeyfaceType)

    >>> api.acquireInformationProvider(IBar) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IBar at IUndefinedContext.'

    >>> class IFooBar(IFoo, IBar):
    ...    pass

    >>> api.acquireInformationProvider(IFooBar) 
    <Information provider IFoo at IUndefinedContext>

If we register a new information provider to IBar and IUndefinedContext, we can
observe the following behavior:

    >>> provider_3 = ensureInformationProvider(IBar, api.IUndefinedContext)

    >>> api.acquireInformationProvider(IBar)
    <Information provider IBar at IUndefinedContext>

    >>> interface.alsoProvides(IFooBar, api.IKeyfaceType)

    >>> api.acquireInformationProvider(IFooBar) 
    <Information provider IFoo at IUndefinedContext>

    >>> class IBarFoo(IBar, IFoo):
    ...    pass

    >>> interface.alsoProvides(IBarFoo, api.IKeyfaceType)

    >>> api.acquireInformationProvider(IBarFoo) 
    <Information provider IBar at IUndefinedContext>

But we always get the most specialized one:

    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <Information provider IBar at IUndefinedContext> 

    >>> provider_4 = ensureInformationProvider(IBarFoo, api.IUndefinedContext)
    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <Information provider IBarFoo at IUndefinedContext>

    >>> provider_5 = ensureInformationProvider(IBar, IOurContext)
    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <Information provider IBar at IOurContext>

    >>> provider_6 = ensureInformationProvider(IBarFoo, IOurContext)
    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <Information provider IBarFoo at IOurContext>

Complex Lookup using getInformationProvidersFor
-----------------------------------------------

Last but not least you can lookup all information provider registered for a 
certain key interface or context interface using getInformationProvidersFor
function.

If you lookup the providers for a context interface, you will get an iterator
that returns (keyface, provider) pairs:

    >>> [i.__name__ for i,p in api.getInformationProvidersFor(IOurContext)]
    ['IBar', 'IBarFoo']

If you lookup the providers for a key interface, you will get an iterator
which returns (conface, provider) pairs:

    >>> [i.__name__ for i,p in api.getInformationProvidersFor(IBarFoo)]
    ['IOurContext', 'IUndefinedContext']
