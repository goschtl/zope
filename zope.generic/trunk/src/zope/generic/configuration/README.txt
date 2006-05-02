=====================
Generic Configuration
=====================

The configurations mechansim works similar to the annotations mechansim, but 
references a single configuration (annotation) by its corresponding 
configuration schema (regular interfac-based schema see zope.schema). 
Such a configuration associates data and its corresponding schema. That means
the configuration data provides the related schema and you can allways lookup
dedicated configuration data by its configuration schema.

The annotations mechanism is well-known and documented (zope.annotations).


Configurations
---------------

Configurations is a container of configuration data. Configuration data are
defined by an schema which is typed as IConfigurationType. IConfigurationType
is extending IKeyType because the configuration schemas are the key interface
of a configuration object too. The configuration object itself has to provide 
the schema too.

    >>> from zope.interface import Interface
    >>> from zope.schema import TextLine
    
    >>> class IFooConfiguration(Interface):
    ...    foo = TextLine(title=u'Foo')
    ...    optional = TextLine(title=u'Optional', required=False, default=u'Bla')

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IFooConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> api.IConfigurationType.providedBy(IFooConfiguration)
    True
 
    >>> from zope.generic.face import IKeyfaceType
    >>> IKeyfaceType.providedBy(IFooConfiguration)
    True

Regularly local configurations are provided by objects marked with
IAttributeConfigurations automatically:

    >>> from zope.interface import implements
    >>> from zope.generic.configuration.api import IAttributeConfigurable

    >>> class Foo(object):
    ...    implements(IAttributeConfigurable)

    >>> foo = Foo()
    >>> IAttributeConfigurable.providedBy(foo)
    True

Now you can adapt you to IConfigurations:

    >>> from zope.generic.configuration.api import IConfigurations

    >>> configurations = IConfigurations(foo)
    >>> IConfigurations.providedBy(configurations)
    True

At the beginning the IConfigurations storage does not exists:

    >>> configurations.__nonzero__()
    False

The configurations provides a regular dictionary api by the UserDictMixin
(like AttributeAnnotations). This mixin bases on the following methods:

    >>> configurations[IFooConfiguration]
    Traceback (most recent call last):
    ...
    KeyError: <InterfaceClass example.IFooConfiguration>

    >>> del configurations[IFooConfiguration]
    Traceback (most recent call last):
    ...
    KeyError: <InterfaceClass example.IFooConfiguration>

    >>> configurations.keys()
    []

... if a value might be set to the configurations it must provide the 
configuration schema itself. This key interface must provide IConfiguration:

    >>> class IBarConfiguration(Interface):
    ...    bar = TextLine(title=u'Bar')

    >>> configurations[IBarConfiguration] = object()
    Traceback (most recent call last):
    ...
    KeyError: 'Interface key IBarConfiguration requires IConfigurationType.'

    >>> configurations[IFooConfiguration] = object()
    Traceback (most recent call last):
    ...
    ValueError: Value does not provide IFooConfiguration.

Furthermore there is an update method that can be used to update a specific
configuration. This method can be only used if a configuration already exists:

    >>> configurations.update(IFooConfiguration, {'foo': u'Foo!'})
    Traceback (most recent call last):
    ...
    KeyError: <InterfaceClass example.IFooConfiguration>

You can create valid configuration data using the generic ConfigurationData
implementation and a configuration schema. The setting of the configuration is
notified by a object configured event if the parent has a location an the 
parent's parent is not None:

    >>> from zope.component.eventtesting import getEvents, clearEvents
    >>> from zope.generic.configuration.api import ConfigurationData
    >>> from zope.generic.configuration.api import IObjectConfiguredEvent

    >>> clearEvents()

    >>> data = ConfigurationData(IFooConfiguration, {'foo': u'Foo!'})

    >>> configurations[IFooConfiguration] = data

    >>> events = getEvents()
    >>> len(events)
    0

    >>> from zope.location import Location
    >>> parent = Location()
    >>> configurations.__parent__ = parent
    
    >>> configurations[IFooConfiguration] = data
    >>> events = getEvents()
    >>> len(events)
    0

    >>> parent.__parent__ = Location()
    >>> configurations[IFooConfiguration] = data
    >>> events = getEvents()
    >>> len(events)
    1

    >>> event = events.pop()
    >>> IObjectConfiguredEvent.providedBy(event)
    True
    >>> [(key.__name__, value) for key, value in event.items()]
    [('IFooConfiguration', {'foo': u'Foo!', 'optional': u'Bla'})]

If the configuration data is set the first time an oobtree storage is set
to the __configurations__ attribute of the context:

    >>> configurations.__nonzero__()
    True

    >>> IFooConfiguration in configurations
    True

    >>> configurations[IFooConfiguration] == data
    True

    >>> [iface.__name__ for iface in configurations.keys()]
    ['IFooConfiguration']

You should update a configuration using the update method instead of setting
new configuration data. If the change differs from the configuration an object
configuration modified event is notify else not:

    >>> clearEvents()
    >>> configurations.update(IFooConfiguration, {'foo': u'Bar!'})
    >>> events = getEvents()
    >>> len(events)
    1
    >>> event = events.pop()
    >>> [(key.__name__, value) for key, value in event.items()]
    [('IFooConfiguration', {'foo': u'Bar!'})]

Also the deletion is notified by an empty dict:

    >>> clearEvents()

    >>> del configurations[IFooConfiguration]
    >>> IFooConfiguration in configurations
    False

    >>> events = getEvents()
    >>> len(events)
    1
    >>> event = events.pop()
    >>> [(key.__name__, value) for key, value in event.items()]
    [('IFooConfiguration', {})]
