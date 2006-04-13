=============
Configuration
=============

Configuration is a container of configuration data. Configuration data are
defined by an schema which is providing IConfigurationType.

	>>> from zope.schema import TextLine
		
    >>> class IMyConfiguration(interface.Interface):
    ...     my = TextLine(title=u'My')

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IMyConfiguration"
    ...     label='My' hint='My bla.'
    ...     />
    ... ''') 

	>>> from zope.generic.configuration.api import IConfigurationType
	>>> IConfigurationType.providedBy(IMyConfiguration)
	True

The configuration itself is an information (see zope.generic.information) which
is registered as utility providing IConfigurationInformation and named
by the dotted configuration schema name:

    >>> from zope.generic.configuration.api import IConfigurationInformation
    >>> from zope.generic.information.api import queryInformation

    >>> config_info = queryInformation(IMyConfiguration, 
    ...		IConfigurationInformation) 
    >>> config_info.label == u'My'
    True
    >>> config_info.hint == u'My bla.'
    True

There is a convenience function for configuration informations too:

    >>> from zope.generic.configuration.api import queryConfigurationInformation

	>>> config_info == queryConfigurationInformation(IMyConfiguration)
	True

The modification of configuration might cause object configuration modified event.
Those event extend the regular object modified event. This event regularly implies
a location of the referenced object. Therefore only locatable objects will get
notified. In our example we registered a transient global information which does
not satify the condition:

    >>> from zope.app.event.tests.placelesssetup import getEvents, clearEvents
    >>> from zope.generic.configuration import IObjectConfiguredEvent
    >>> events = getEvents()
    >>> len(events)
    0 

Attribute Configurations
------------------------
 
Regularly Configurations are provided by objects marked with
IAttributeConfigurations automatically:

    >>> from zope.interface import implements
    >>> from zope.generic.configuration import IAttributeConfigurable

    >>> class Foo(object):
    ...    implements(IAttributeConfigurable)

    >>> foo = Foo()
    >>> IAttributeConfigurable.providedBy(foo)
    True

Now you can adapt you to IConfigurations:

	>>> from zope.generic.configuration import IConfigurations

    >>> configurations = IConfigurations(foo)
    >>> IConfigurations.providedBy(configurations)
    True

At the beginning the IConfigurations storage does not exists:

    >>> configurations.__nonzero__()
    False

Configuration data will be stored under an interface-key within the
configurations. Such a configuration interface-key defines its configuration
data:

    >>> from zope.interface import Interface
    >>> from zope.schema import TextLine
    
    >>> class IFooConfiguration(Interface):
    ...    foo = TextLine(title=u'Foo')
    ...    optional = TextLine(title=u'Optional', required=False, default=u'Bla')

The configuration interface-key is a regular schema, but it has to be typed
by IConfigurationType (Regularly typed by the configuration directive):

    >>> from zope.interface import directlyProvides

    >>> directlyProvides(IFooConfiguration, IConfigurationType)
    >>> IConfigurationType.providedBy(IFooConfiguration)
    True

The configuration provides a regular dictionary api by the UserDictMixin
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
configuration interface-key itself. The interface-key must provide
IConfigurationType:

    >>> class IBarConfiguration(Interface):
    ...    bar = TextLine(title=u'Bar')

    >>> configurations[IBarConfiguration] = object()
    Traceback (most recent call last):
    ...
    KeyError: 'Interface key IBarConfiguration does not provide IConfigurationType.'

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
implementation:

    >>> from zope.generic.configuration.base import ConfigurationData

    >>> data = ConfigurationData(IFooConfiguration, {'foo': u'Foo!'})

    >>> configurations[IFooConfiguration] = data

The setting of the configuration is notified by a object configuration
modified event if the parent has a location an the parent's parent
is not None:

    >>> events = getEvents()
    >>> len(events)
    0

    >>> from zope.app.location import Location
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

Also the deletion is notified:

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
