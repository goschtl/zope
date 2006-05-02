============================
Generic Information Provider
============================

The key interface (see zope.generic.face) can be used to lookup corresponding
information providers. This package offers a way to register information
providers and theirs information by a zcml directive.

You can register different contextual information providers for the same 
key interface. An information provider encapsulates a certain contextual 
information aspect of the key interface. The relation between information 
providers of a key interface to components providing the same key interface is
similar to the object class relation except that we have a contextual separation
of the information.

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
the identical information types receive theirs contextual meaning within a
information provider.

Information Provider
--------------------

You can use the information provider directive to register an information 
provider. For that purpose we need a key and a context interface:

    >>> class ISpecialContext(interface.Interface):
    ...    pass

    >>> from zope.interface import Interface
    >>> class IMyFoo(Interface):
    ...    pass

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IMyFoo"
    ...     conface="example.ISpecialContext"
    ...     />
    ... ''')

After a registration the information provider can be looked up.
All information provider with the same context interface can be looked up by the 
getInformationProvidersFor function:

    >>> listing = list(api.getInformationProvidersFor(ISpecialContext))
    >>> len(listing) is 1
    True
    >>> [(key.__name__, value) for key, value in listing]
    [('IMyFoo', <zope.generic.informationprovider.base.GlobalInformationProvider ...>)]

A single information provider can be retrieved by the get- or 
queryInformationProvider function:

    >>> provider = api.getInformationProvider(IMyFoo, ISpecialContext)
    >>> provider = api.queryInformationProvider(IMyFoo, ISpecialContext)

    >>> listing[0][1] is provider
    True
    >>> listing[0][0] is IMyFoo
    True

    >>> provider.keyface == IMyFoo
    True
    >>> ISpecialContext.providedBy(provider)
    True

If no information provider is available for a certain interface the default
value is returned. If no default is defined None is returned:

    >>> class IMyBar(Interface):
    ...    pass

    >>> default = object()
    >>> provider = api.queryInformationProvider(IMyBar, ISpecialContext, default)
    >>> provider is default
    True

    >>> provider = api.queryInformationProvider(IMyBar, ISpecialContext)
    >>> provider is None
    True

Information providers are extentable by informations
----------------------------------------------------

At the moment informations are an abstraction for annotations and
configurations.

Information providers are annotable. The annotations mechanism is used to provide
additional informations in a well-known manner. At the moment there are no 
configurations:

    >>> api.queryInformation(provider, 'example.my_annotation') is None
    True

Information providers are configurable. The configurations mechanism is used 
to provide additional configurations in a generic manner too. A configuration
is declared by a configuration schema providing IConfiguration:

    >>> from zope.schema import TextLine
        
    >>> class IMyConfiguration(interface.Interface):
    ...     my = TextLine(title=u'My')

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IMyConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> from zope.generic.configuration.api import IConfigurationType

    >>> IConfigurationType.providedBy(IMyConfiguration)
    True

At the moment there are no configurations:

    >>> api.queryInformation(provider, IMyConfiguration) is None
    True

We now can use an annotation and a configuration to extend our information
provider of the key interface IMyFoo.

The annotation and configuration subdirective of the information provider
directive provides a mechanism to register further informations to an 
information provider:

    >>> my_annotation = object()

    >>> from zope.generic.configuration.api import ConfigurationData
    >>> my_configuration = ConfigurationData(IMyConfiguration, {'my': u'My!'})

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IMyFoo"
    ...     conface="example.ISpecialContext"
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

    >>> provider = api.queryInformationProvider(IMyFoo, ISpecialContext)
    >>> api.queryInformation(provider, 'example.my_annotation') is my_annotation
    True

    >>> provider = api.queryInformationProvider(IMyFoo, ISpecialContext)
    >>> api.queryInformation(provider, IMyConfiguration) is my_configuration
    True

Complex information provider lookup using acquireInformationProvider
--------------------------------------------------------------------

see zope.generic.face README.txt