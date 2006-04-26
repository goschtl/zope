===============
Generic Adapter
===============

The directive generic:adapter allows to register trusted, locatable
adapters. This is a convenience directive that merges the regular class- and
adapter-directive.

The directive does invoke the regular adapter directive, but provides a few
convenience options:

-   If the class does not implement ILocation, the locatalbe flag is set to
    True.

-   If the read- or writePermission is set the class directive is invoked the
    following way:

    -   If no attributes or set_attributes are declared we use the
        provided interface for securtiy declarations. The interface or
        set_schema attribute of the required subdirective is taken.

    -   If attributes or set_attributes are those names are used for the 
        security declaration. The attributes or set_attributes attribute of 
        the required subdirective is taken.

-   You don't have to define the class attribute if the provides interface 
    provides zope.generic.configuration.IConfiguraitonType. In those cases the
    adapter class is build by a generic configuration adapter class factory.

-   You don't have to define the class attribute if the key attribute is 
    set. In those cases the adapter class is build by a generic annotation
    adapter class factory assuming the annotation is providing the provides
    interface. (TODO: NOT IMPLEMENTED YET)


Configurations convenience adapter
----------------------------------

First we declare a configuration schema that should adapted:

    >>> from zope.schema import TextLine

    >>> class IFooConfiguration(interface.Interface):
    ...    foo = TextLine(title=u'Foo', required=False, default=u'Default config.')

We register the configuration schema using generic:keyface directive:

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IFooConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> from zope.generic.configuration import IConfigurationType
    >>> IConfigurationType.providedBy(IFooConfiguration)
    True

We implement a class which is providing the configuration mechanism:

    >>> class IFoo(interface.Interface):
    ...    pass

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IFoo"
    ...     />
    ... ''')
    
    >>> from zope.generic.configuration.api import IAttributeConfigurable

    >>> class Foo(object):
    ...     interface.implements(IFoo, IAttributeConfigurable)

    >>> foo = Foo()

    >>> from zope.generic.configuration.api import queryConfiguration
    >>> queryConfiguration(foo, IFooConfiguration) is None
    True

Now we can provide an configuration adapter by a corresponding registration:

    >>> registerDirective('''
    ... <generic:adapter
    ...     for="example.IFoo"
    ...     provides="example.IFooConfiguration"
    ...     readPermission="zope.Public"
    ...     writePermission="zope.Public"
    ...     />
    ... ''')

We can adapt our foo to IFooConfiguration:

    >>> adapted = IFooConfiguration(foo)
    >>> IFooConfiguration.providedBy(adapted)
    True
    >>> adapted.foo
    u'Default config.'

    >>> adapted.foo = u'Foo config.'
    >>> adapted.foo
    u'Foo config.'

    >>> queryConfiguration(foo, IFooConfiguration).foo
    u'Foo config.'
