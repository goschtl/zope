============
Generic Face
============

This package provides a mechanism to define and access key interface marker 
(IKeyfaceType) and a context interface marker (IConfaceType). Those interfaces
can be used to provide dedicated information (IInformationProvider) such as 
configurations and annotations contextually.

Within the system domain the key interface represents a permanent marker for an
object. For example the marked object *is* a person. Regularly you will mark
your content components with domain-specific key interface markers. Such a
keyface (short for: key[ inter]face) has the same relation like classes
to its instances.

The context interface allows an more explicit comprehension and lookup of 
information related to objects. Contexts of understanding are often changing
within the same system domain. Regularly a certain information provider is 
contextual. That means different information providers will provide the same
type of information about one subject but the value of the provided information
might differ contextually. For example your *name* within the system domain 
*world* is changing: Within your childs context it will be 'Dad', within your 
wife's context it will be 'Darling', within your friend's context it will be 
'Dude' and within the official context will be 'Mr. Foo Bar'.

Both interface types provide the fundament to model more complex , contextual
object-behavior and -properties. The package allows to define keys that allows 
a dedicated, but generic invocation of information providers. This allows 
dedicated facing or casing of objects.

Context interface types
-----------------------

The context interface is one piece to lookup information providers contextually.
You can provide a context interface simply by deriving from zope's Interface.

    >>> class IMyContext(interface.Interface):
    ...    pass

The context interface should be registered by the conface directive. This
asserts that the interface get marked as IKeyfaceType:

    >>> api.IKeyfaceType.providedBy(IMyContext)
    False

    >>> registerDirective('''
    ... <generic:face
    ...     conface="example.IMyContext"
    ...     />
    ... ''') 

    >>> api.IConfaceType.providedBy(IMyContext)
    True

As usual the typed interface is registered as utility too:

    >>> component.getUtility(api.IConfaceType, 
    ...     api.toDottedName(IMyContext)) == IMyContext
    True

As usual you can type context interfaces with other interface types:

    >>> class IMyType(interface.interfaces.IInterface):
    ...    pass

    >>> registerDirective('''
    ... <generic:face
    ...     conface="example.IMyContext"
    ...     type="example.IMyType"
    ...     />
    ... ''') 

    >>> IMyType.providedBy(IMyContext)
    True
    >>> component.getUtility(IMyType, 
    ...     api.toDottedName(IMyContext)) == IMyContext
    True

Key interface types
-------------------

The behavior of components within the ca-framework depends heavily on their
provided interfaces. A component, except most of the adapters and utilities, 
regularly provides more than one interface. The adaption and subscriber 
mechanism of the ca-framework invokes the provided interfaces by a 
lookup-algorithmus similar to the method resolution order by class inherintance.

Most of the time this behavior satisfies our requirements. Additionally this 
package offers a mechanism to declare a single key interface (IFace).
This key interface can be used to lookup corresponding information providers
more explicitly.

First we use a key interface:

    >>> class IFoo(interface.Interface):
    ...    pass

The key interface should be registered by the keyface directive. This asserts
that the interface get marked as IKeyfaceType:

    >>> api.IKeyfaceType.providedBy(IFoo)
    False

    >>> registerDirective('''
    ... <generic:face
    ...     keyface="example.IFoo"
    ...     />
    ... ''') 

    >>> api.IKeyfaceType.providedBy(IFoo)
    True

As usual the typed interface is registered as utility too:

    >>> component.getUtility(api.IKeyfaceType, 
    ...     api.toDottedName(IFoo)) == IFoo
    True

As usual you can type context interfaces with other interface types:

    >>> registerDirective('''
    ... <generic:face
    ...     keyface="example.IFoo"
    ...     type="example.IMyType"
    ...     />
    ... ''') 

Afterward the interface will be typed regularly:

    >>> IMyType.providedBy(IFoo)
    True
    >>> component.getUtility(IMyType, 
    ...     api.toDottedName(IFoo)) == IFoo
    True

An exception of the directive in relation to the regular interface directive is,
that you can mark key interfaces by a context interface. This marking says there
might be contextual information. The abscence of a context marker asserts that
there are *no* contextual informations to an key interface:

    >>> registerDirective('''
    ... <generic:face
    ...     keyface="example.IFoo"
    ...     type="example.IMyContext"
    ...     />
    ... ''') 

    >>> IMyContext.providedBy(IFoo)
    True

Attention: Those contextual types will be not available as interface utility.
Instead there will be an information provider (see 
zope.generic.informationprovider too):

    >>> provider = component.getUtility(IMyContext, 
    ...     api.toDottedName(IFoo)) 

    >>> provider == IFoo
    False

    >>> IMyContext.providedBy(provider)
    True
    >>> provider.conface == IMyContext
    True

    >>> IFoo.providedBy(provider)
    False
    >>> provider.keyface == IFoo
    True

    >>> api.IInformationProvider.providedBy(provider)
    True


How to provide the face mechanism
---------------------------------

The IFaced interface promises access to keyface and/or conface of an object.
The lookup of key and context interfaces is regularly done by providing 
IAttributeFaced.

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

The api provides convenience functions to get the key interfaces of components:

    >>> api.getKeyface(foofaced) == IFoo
    True
    
    >>> api.getKeyface(fooface) == api.IUndefinedKeyface
    True

    >>> api.getKeyface(object()) == api.IUndefinedKeyface
    True


The api provides convenience functions to get the context interfaces of components:

    >>> api.getConface(foofaced) == api.IUndefinedContext
    True
    
    >>> api.getConface(fooface) == IMyContext
    True

    >>> api.getConface(object()) == api.IUndefinedContext
    True




