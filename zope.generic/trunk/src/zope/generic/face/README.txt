============
Generic Face
============

This package provides interface types for key interfaces (IKeyfaceType) and 
context interfaces (IConfaceType). 

Typed interfaces can be used to register dedicated information providers 
(IInformationProvider see zope.generic.informationprovider). An information 
provider offers the possiblity to register information according to a pair of 
key- and context interfaces.

Key interface (Keyface: short for [key[ inter]face)
---------------------------------------------------

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

Context Interface (Conface: short for [con[text inter]face)
-----------------------------------------------------------

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
