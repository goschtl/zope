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

The key interface should be registered by the keyface directive. This asserts
that those interface got marked as IKeyfaceType:

    >>> api.IKeyfaceType.providedBy(IFooMarker)
    False

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IFooMarker"
    ...     />
    ... ''') 

    >>> api.IKeyfaceType.providedBy(IFooMarker)
    True

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

    >>> api.getKeyface(fookeyfaced) == IFooMarker
    True
    
    >>> api.getKeyface(fookeyface) == IFooMarker
    True

    >>> api.getKeyface(object())
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ...)

    >>> api.queryKeyface(fookeyfaced) == IFooMarker
    True
    
    >>> api.queryKeyface(fookeyface) == IFooMarker
    True

    >>> api.queryKeyface(object()) == None
    True


New key interface types can be created to provide key interfaces with a dedicated
usage (for example IConfigurationType). Attention keyfaces can be typed only
once by a type deriving from IKeyfaceType:

    >>> class IMyKeyfaceType(api.IKeyfaceType):
    ...    pass

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IFooMarker"
    ...     type="example.IMyKeyfaceType"
    ...     />
    ... ''') 
    Traceback (most recent call last):
    ...
    ZopeXMLConfigurationError: ...ConfigurationError: Keyface IFooMarker already registered.

    >>> class IBarMarker(interface.Interface):
    ...    pass


    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IBarMarker"
    ...     type="example.IMyKeyfaceType"
    ...     />
    ... ''') 

    >>> api.IKeyfaceType.providedBy(IBarMarker)
    True