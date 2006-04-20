===============
Generic Keyface
===============

The behavior of components within the ca-framework depends heavily on their
provided interfaces. A component, except most of the adapters and utilities, 
regularly provides more than one interface. The adaption and subscriber 
mechanism of the ca-framework invokes the provided interfaces by a 
lookup-algorithmus similar to the method resolution order by class inherintance.

Most of the time this behavior satisfies our requirements. Additionally this 
package offers a mechanism to declare a single key interface (IKeyface).
This key interface can be used to lookup corresponding information providers
more explicitly.

A component that like to use this mechanism should provide a mechanism to look
up the key interface. This is regularly done providing IAttributeKeyfaced.

First we use a key interface:

    >>> class IFooMarker(interface.Interface):
    ...    pass

Then we have to decorate a corresponding key-faced component:

    >>> class FooKeyfaced(object):
    ...    interface.implements(api.IAttributeKeyfaced)
    ...    __keyface__ = IFooMarker

There is a default adapter to IKeyface for key-faced objects:

    >>> fookeyfaced = FooKeyfaced()

    >>> adapted = api.IKeyface(fookeyfaced)
    >>> adapted.keyface == IFooMarker
    True

Furthermore there is simple Keyface mixin for AttributeKeyfaced objects:

    >>> class FooKeyface(FooKeyfaced, api.Keyface):
    ...    __keyface__ = IFooMarker

    >>> fookeyface = FooKeyface()
    >>> fookeyface.keyface == IFooMarker
    True

The api provides convenience functions to get the key interfaces of components:

    >>> api.getKey(fookeyfaced) == IFooMarker
    True
    
    >>> api.getKey(fookeyface) == IFooMarker
    True

    >>> api.getKey(object())
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ...)

    >>> api.queryKey(fookeyfaced) == IFooMarker
    True
    
    >>> api.queryKey(fookeyface) == IFooMarker
    True

    >>> api.queryKey(object()) == None
    True


