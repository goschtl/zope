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

    >>> from zope.schema import TextLine
    
    >>> class IFooConfiguration(interface.Interface):
    ...    foo = TextLine(title=u'Foo')
    ...    optional = TextLine(title=u'Optional', required=False, default=u'Bla')

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IFooConfiguration"
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

    >>> class IBarConfiguration(interface.Interface):
    ...    bar = TextLine(title=u'Bar')

    >>> configurations[IBarConfiguration] = object()
    Traceback (most recent call last):
    ...
    KeyError: 'Interface key IBarConfiguration requires IConfigurationType.'

    >>> configurations[IFooConfiguration] = object()
    Traceback (most recent call last):
    ...
    ValueError: Value does not provide IFooConfiguration or is not a dictionary.

    >>> from zope.generic.configuration.api import createConfiguration
    >>> data = createConfiguration(IFooConfiguration, {'foo': u'Foo!'})

    >>> configurations[IFooConfiguration] = data

You can set a configuraiton only once. Otherwise you should use the update method
or delete the configuraiton before a new setting:

    >>> configurations[IFooConfiguration] = data
    Traceback (most recent call last):
    ...
    ValueError: Configuration is already provided IFooConfiguration.

    >>> del configurations[IFooConfiguration]

You can also use only a dictionary as value instead of a configuration:

    >>> configurations[IFooConfiguration] = {'foo': u'Foo!'}
    >>> configurations[IFooConfiguration].foo
    u'Foo!'

    >>> del configurations[IFooConfiguration]

Furthermore there is an update method that can be used to update a specific
configuration. You can use the method to provide an initial configuration or
to update parts of a configuration:

    >>> configurations.update(IFooConfiguration, {'foo': u'Foo!'})
    >>> configurations[IFooConfiguration].foo
    u'Foo!'
    
    >>> configurations.update(IFooConfiguration, {'foo': u'Foo x!'})
    >>> configurations[IFooConfiguration].foo
    u'Foo x!'

    >>> config = createConfiguration(IFooConfiguration, {'foo': u'Foo y!'})
    >>> configurations.update(IFooConfiguration, config)
    >>> configurations[IFooConfiguration].foo
    u'Foo y!'

    >>> config = createConfiguration(IFooConfiguration, {'foo': u'Foo z!'})
    >>> configurations.update(config)
    >>> configurations[IFooConfiguration].foo
    u'Foo z!'

You can create valid configuration data using the generic createConfiguration
implementation and a configuration schema. The setting of the configuration is
notified by a object configured event if the parent has a location an the 
parent's parent is not None:

    >>> from zope.component.eventtesting import getEvents, clearEvents
    >>> from zope.generic.configuration.api import IObjectConfiguredEvent

    >>> clearEvents()

    >>> del configurations[IFooConfiguration]

    >>> from zope.location import Location
    >>> parent = Location()
    >>> configurations.__parent__ = parent

    >>> configurations[IFooConfiguration] = data
    >>> events = getEvents()
    >>> len(events)
    0

    >>> del configurations[IFooConfiguration]

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
configuration modified event is notify else not. This can be done by a dict
or a configuration:

    >>> clearEvents()
    >>> configurations.update(IFooConfiguration, {'foo': u'Bar!'})
    >>> events = getEvents()
    >>> len(events)
    1
    >>> event = events.pop()
    >>> [(key.__name__, value) for key, value in event.items()]
    [('IFooConfiguration', {'foo': u'Bar!'})]

    >>> clearEvents()
    >>> foo_config = api.createConfiguration(IFooConfiguration, {'foo': u'Bar !'})
    >>> configurations.update(foo_config)
    >>> events = getEvents()
    >>> len(events)
    1
    >>> event = events.pop()
    >>> [(key.__name__, value) for key, value in event.items()]
    [('IFooConfiguration', {'foo': u'Bar !'})]

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

Nested Configurations
---------------------

The configuration directive does evaluate if an key interface is nested:

    >>> class IMySubConfiguration(interface.Interface):
    ...    foo = api.SubConfiguration(schema=IFooConfiguration)

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IMySubConfiguration"
    ...     />
    ... ''') 

    >>> api.INestedConfigurationType.providedBy(IMySubConfiguration)
    True

    >>> from zope.schema import Text

    >>> class IMySubConfigurationList(interface.Interface):
    ...    foo = api.SubConfigurationList(value_type=Text())
    ...    bar = api.SubConfigurationList(required=False, 
    ...        value_type=api.SubConfiguration(schema=IFooConfiguration))

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IMySubConfigurationList"
    ...     />
    ... ''')

    >>> api.INestedConfigurationType.providedBy(IMySubConfigurationList)
    True

    >>> from zope.schema import BytesLine

    >>> class IMySubConfigurationDict(interface.Interface):
    ...    foo = api.SubConfigurationDict(value_type=Text())
    ...    bar = api.SubConfigurationDict(required=False, 
    ...        value_type=api.SubConfiguration(schema=IFooConfiguration))

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IMySubConfigurationDict"
    ...     />
    ... ''')

    >>> api.INestedConfigurationType.providedBy(IMySubConfigurationDict)
    True

You can suppress the evaluation by an explicite declaration using the nested
attribute:

    >>> class ISuppressedNestedConfiguration(interface.Interface):
    ...    foo = api.SubConfigurationDict(value_type=Text())

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.ISuppressedNestedConfiguration"
    ...     nested="False"
    ...     />
    ... ''')

    >>> api.INestedConfigurationType.providedBy(ISuppressedNestedConfiguration)
    False

We can create nested configurations by a dictionary where the hierarchy is
reflected by dotted names.

Nested sub-configuration:

    >>> data = {'foo.foo': u'bla', 'foo.optional': u'Blu'}
    >>> config = api.createConfiguration(IMySubConfiguration, data)
    >>> IFooConfiguration.providedBy(config.foo)
    True
    >>> config.foo.foo
    u'bla'
    >>> config.foo.optional
    u'Blu'

    >>> data = {'foo.foo': u'xxx'}
    >>> config = api.createConfiguration(IMySubConfiguration, data)
    >>> IFooConfiguration.providedBy(config.foo)
    True
    >>> config.foo.foo
    u'xxx'
    >>> config.foo.optional
    u'Bla'

    >>> data = {'foo.optional': u'Blu'}
    >>> config = api.createConfiguration(IMySubConfiguration, data)
    Traceback (most recent call last):
    ...
    TypeError: __init__ requires 'foo' of 'IFooConfiguration'.

    >>> subdata = {'foo': u'bla', 'optional': u'Blu'}
    >>> subconfig = api.createConfiguration(IFooConfiguration, subdata)
    >>> data = {'foo': subconfig}
    >>> config = api.createConfiguration(IMySubConfiguration, data)
    >>> IFooConfiguration.providedBy(config.foo)
    True
    >>> config.foo.foo
    u'bla'
    >>> config.foo.optional
    u'Blu'

Simple sub-configuration lists:

    >>> data = {'foo.0': u'bla', 'foo.1': u'Blu'}
    >>> config = api.createConfiguration(IMySubConfigurationList, data)
    >>> from persistent.list import PersistentList
    >>> isinstance(config.foo, PersistentList)
    True
    >>> config.foo[0]
    u'bla'
    >>> config.foo[1]
    u'Blu'

    >>> data = {'foo.1': u'bla', 'foo.2': u'Blu'}
    >>> config = api.createConfiguration(IMySubConfigurationList, data)
    Traceback (most recent call last):
    ...
    IndexError: list index out of range

Nested sub-configuration lists:

    >>> data = {'foo.0': u'bla', 'foo.1': u'Blu', 
    ...         'bar.0.foo': u'bla 0', 'bar.0.optional': u'Blu 0', 
    ...         'bar.1.foo': u'bla 1'}
    >>> config = api.createConfiguration(IMySubConfigurationList, data)
    >>> from persistent.list import PersistentList
    >>> isinstance(config.bar, PersistentList)
    True
    >>> config.foo[0]
    u'bla'
    >>> config.foo[1]
    u'Blu'
    >>> IFooConfiguration.providedBy(config.bar[0])
    True
    >>> config.bar[0].foo
    u'bla 0'
    >>> config.bar[0].optional
    u'Blu 0'
    >>> config.bar[1].foo
    u'bla 1'

    >>> data = {'foo.0': u'bla', 'foo.1': u'Blu', 
    ...         'bar.0.foo': u'bla 0', 'bar.0.optional': u'Blu 0', 
    ...         'bar.2.foo': u'bla 1'}
    >>> config = api.createConfiguration(IMySubConfigurationList, data)
    Traceback (most recent call last):
    ...
    IndexError: list index out of range

Simple sub-configuration dicts:

    >>> data = {'foo.a': u'bla', 'foo.b': u'Blu'}
    >>> config = api.createConfiguration(IMySubConfigurationDict, data)
    >>> from persistent.dict import PersistentDict
    >>> isinstance(config.foo, PersistentDict)
    True
    >>> config.foo['a']
    u'bla'
    >>> config.foo['b']
    u'Blu'

Nested sub-configuration dicts:

    >>> data = {'foo.a': u'bla', 'foo.b': u'Blu', 
    ...         'bar.c.foo': u'bla C', 'bar.c.optional': u'Blu C', 
    ...         'bar.d.foo': u'bla D'}
    >>> config = api.createConfiguration(IMySubConfigurationDict, data)
    >>> from persistent.dict import PersistentDict
    >>> isinstance(config.bar, PersistentDict)
    True
    >>> config.foo['a']
    u'bla'
    >>> config.foo['b']
    u'Blu'
    >>> IFooConfiguration.providedBy(config.bar['c'])
    True
    >>> config.bar['c'].foo
    u'bla C'
    >>> config.bar['c'].optional
    u'Blu C'
    >>> config.bar['d'].foo
    u'bla D'


Exception handling during the update
------------------------------------

If an error occurs during the update the last state of the configuration is
rolled back:
    
    TODO


