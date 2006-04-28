=================
Generic Component
=================

The key interface (see zope.generic.keyface) can be used to lookup corresponding
information providers. This package offers a way to implement information
providers generically.

You can register different information providers to the same key interface. An
information provider encapsulates a certain information aspect of the key 
interface. The relation between information providers of a key interface to
components providing the same key interface is similar to the object class 
relation except that each informatio aspect follows its own information 
acquisition.

You can attache generic informations such as annotations or configurations
to an certain information provider.

The annotations mechanism is well-known and documented (zope.annotations).

The configurations mechansim works similar to the annotations mechansim, but 
references a single configuration (annotation) by its corresponding 
configuration schema (regular interfac-based schema see zope.schema). 
Such a configuration associates data and its corresponding schema. That means
the configuration data provides the related schema and you can allways lookup
dedicated configuration data by its configuration schema.

Similar atomic informations defined by an annotation key or a 
configuration schemas can be reused by different information providers. So
the identical information types will receive a contextual meaning that is related
to information provider type.

Information Provider
--------------------

You can use the information provider directive to register an information 
provider as utiliy with an interface extending IInformationProvider and a
dotted name of an corresponding key interface as utility name:

    >>> from zope.generic.informationprovider.api import IInformationProvider

    >>> class ISpecialInformation(IInformationProvider):
    ...    pass

    >>> from zope.interface import Interface
    >>> class IFooMarker(Interface):
    ...    pass

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IFooMarker"
    ...     registry="example.ISpecialInformation"
    ...     label='Foo Specials' hint='Bla bla foo.'
    ...     />
    ... ''')

After a registration the information provider can be looked up.
All information provider with the same interface can be gotten by the 
getInformationProvidersFor function:

    >>> from zope.component.eventtesting import getEvents, clearEvents
    >>> len(getEvents())
    2
    >>> clearEvents()

    >>> listing = list(api.getInformationProvidersFor(ISpecialInformation))
    >>> len(listing) is 1
    True
    >>> [(key.__name__, value) for key, value in listing]
    [('IFooMarker', <zope.generic.informationprovider.base.InformationProvider ...>)]

A single information provider can be retrieved by the get- or 
queryInformationProvider function:

    >>> info = api.getInformationProvider(IFooMarker, ISpecialInformation)
    >>> info = api.queryInformationProvider(IFooMarker, ISpecialInformation)

    >>> listing[0][1] == info
    True
    >>> listing[0][0] == IFooMarker
    True

    >>> info.keyface == IFooMarker
    True
    >>> ISpecialInformation.providedBy(info)
    True
    >>> info.label = u'Foo Specials'
    >>> info.hint = u'Bla bla foo.'

If no information provider is available for a certain interface the default
value is returned. If no default is defined None is returned:

    >>> class IBarMarker(Interface):
    ...    pass

    >>> default = object()
    >>> info = api.queryInformationProvider(IBarMarker, ISpecialInformation, default)
    >>> info is default
    True

    >>> info = api.queryInformationProvider(IBarMarker, ISpecialInformation)
    >>> info is None
    True

Information providers are extentable by informations
----------------------------------------------------

At the moment informations are an abstraction for annotations and
configurations.

Information providers are annotable. The annotations mechanism is used to provide
additional informations in a well-known manner. At the moment there are no 
configurations:

    >>> api.queryInformation(info, 'example.my_annotation') is None
    True

Information providers are configurable. The configurations mechanism is used 
to provide additional configurations in a generic manner too. A configuration
is declared by a configuration schema providing IConfigurationType:

    >>> from zope.schema import TextLine
        
    >>> class IMyConfiguration(interface.Interface):
    ...     my = TextLine(title=u'My')

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IMyConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> from zope.generic.configuration.api import IConfigurationType

    >>> IConfigurationType.providedBy(IMyConfiguration)
    True

At the moment there are no configurations:

    >>> api.queryInformation(info, IMyConfiguration) is None
    True

We now can use an annotation and a configuration to extend our information
provider of the key interface IFooMarker.

The annotation and configuration subdirective of the information provider
directive provides a mechanism to register further informations to an 
information provider:

    >>> my_annotation = object()

    >>> from zope.generic.configuration.api import ConfigurationData
    >>> my_configuration = ConfigurationData(IMyConfiguration, {'my': u'My!'})

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IFooMarker"
    ...     registry="example.ISpecialInformation"
    ...     label='Foo Specials' hint='Bla bla foo.'
    ...     >
    ...        <information
    ...            key="example.my_annotation"
    ...            annotation="example.my_annotation"
    ...            />
    ...        <information
    ...            keyface="example.IMyConfiguration"
    ...            configuration="example.my_configuration"
    ...            />
    ...     </generic:informationProvider>
    ... ''')

    >>> len(getEvents())
    1
    >>> clearEvents()

    >>> info = api.queryInformationProvider(IFooMarker, ISpecialInformation)
    >>> api.queryInformation(info, 'example.my_annotation') is my_annotation
    True

    >>> info = api.queryInformationProvider(IFooMarker, ISpecialInformation)
    >>> api.queryInformation(info, IMyConfiguration) is my_configuration
    True


Configurations
---------------

Configurations is a container of configuration data. Configuration data are
defined by an schema which is providing IConfigurationType. The configuration
data itself has to provide the schema that is used to reference it.

    >>> from zope.schema import TextLine
        
    >>> class IMyConfiguration(interface.Interface):
    ...     my = TextLine(title=u'My')

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IMyConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> len(getEvents())
    1
    >>> clearEvents()

    >>> from zope.generic.configuration.api import IConfigurationType
    >>> IConfigurationType.providedBy(IMyConfiguration)
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

Configuration data will be stored under an key interface within the
configurations. Such a configuration schema defines its configuration
data:

    >>> from zope.interface import Interface
    >>> from zope.schema import TextLine
    
    >>> class IFooConfiguration(Interface):
    ...    foo = TextLine(title=u'Foo')
    ...    optional = TextLine(title=u'Optional', required=False, default=u'Bla')

The configuration schema is a regular schema, but it has to be typed
by IConfigurationType (Regularly done by the configuration directive):

    >>> from zope.interface import directlyProvides

    >>> directlyProvides(IFooConfiguration, IConfigurationType)
    >>> IConfigurationType.providedBy(IFooConfiguration)
    True

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
configuration schema itself. This key interface must provide IConfigurationType:

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
implementation and a configuration schema:

    >>> from zope.generic.configuration.api import ConfigurationData

    >>> data = ConfigurationData(IFooConfiguration, {'foo': u'Foo!'})

    >>> configurations[IFooConfiguration] = data

The setting of the configuration is notified by a object configured event if 
the parent has a location an the parent's parent is not None:

    >>> from zope.generic.configuration.api import IObjectConfiguredEvent

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

