===========
Information
===========

The generic package relies heavily on interfaces. Often we have relation between
different interfaces. Informations provides dedicated data about an certain 
marker interface. Informations are implemented as utility. The package provides
some convenience functions and directives.

An information offers annotations and configurations.

Example
-------

You can use the information directive to register an information as utiliy 
under registry-interface using the dotted name of the interface as utility name:

    >>> from zope.generic.information import api

    >>> class ISpecialInformation(api.IInformation):
    ...    pass

    >>> from zope.interface import Interface
    >>> class IFooMarker(Interface):
    ...    pass

    >>> registerDirective('''
    ... <generic:information
    ...     interface="example.IFooMarker"
    ...     registry="example.ISpecialInformation"
    ...     label='Foo Specials' hint='Bla bla foo.'
    ...     />
    ... ''')

Afterward the information can be queried using the following method:

    >>> info = api.queryInformation(IFooMarker, ISpecialInformation)

    >>> info.interface == IFooMarker
    True
    >>> ISpecialInformation.providedBy(info)
    True
    >>> info.label = u'Foo Specials'
    >>> info.hint = u'Bla bla foo.'

	>>> listing = list(api.registeredInformations(ISpecialInformation))
	>>> len(listing) is 1
	True
	>>> listing[0][1] == info
	True
	>>> listing[0][0] == IFooMarker
	True

If no information is available for a certain interface the defined default
value is returned:

    >>> class IBarMarker(Interface):
    ...    pass

    >>> default = object()
    >>> info = api.queryInformation(IBarMarker, ISpecialInformation, default)
    >>> info is default
    True

    >>> info = api.queryInformation(IBarMarker, ISpecialInformation)
    >>> info is None
    True

Annotatable Informations
------------------------

Informations are annotable. The annotations mechanism is used to provide
additional information in a generic manner by adaption:

    >>> from zope.app.annotation.interfaces import IAnnotations

    >>> info = api.queryInformation(IFooMarker, ISpecialInformation)

    >>> annotations = IAnnotations(info)
    >>> annotations.get('test.annotation')
    >>> annotations['test.annotation']
    Traceback (most recent call last):
    ...
    KeyError: 'test.annotation'
    >>> list(annotations.keys())
    []
    >>> del annotations['test.annotation']
    Traceback (most recent call last):
    ...
    KeyError: 'test.annotation'
    >>> annotations['test.annotation'] = 'a'
    >>> annotations.get('test.annotation')
    'a'
    >>> annotations['test.annotation']
    'a'
    >>> list(annotations.keys())
    ['test.annotation']
    >>> del annotations['test.annotation']


Congigurable Informations
-------------------------

Informations are configurable. The configurations mechanism is used to provide 
additional configurations information in a generic manner. A configuration
is declared by a configuration schema. This is a regular schema that will be
typed a IConfigurationType after its registration (see zope.generic.configuration):

	>>> from zope.schema import TextLine
		
    >>> class IMyConfiguration(interface.Interface):
    ...     my = TextLine(title=u'My')

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IMyConfiguration"
    ...     label='My' hint='My bla.'
    ...     />
    ... ''') 

	>>> from zope.generic.configuration import IConfigurationType
	>>> IConfigurationType.providedBy(IMyConfiguration)
	True

For the further exploration we query this information:

    >>> from zope.generic.configuration.api import queryConfigurationInformation
    >>> from zope.generic.configuration.api import IConfigurationInformation

	>>> my_configuration_information = queryConfigurationInformation(IMyConfiguration)
	>>> my_configuration_information.interface == IMyConfiguration
	True
	>>> IConfigurationInformation.providedBy(my_configuration_information)
	True

We now use this configuration to extend our information about our IFooMarker. 
Before that there will be no configuration:

	>>> from zope.generic.configuration.api import IConfigurations

	>>> info_configurations = IConfigurations(info)
	>>> IMyConfiguration(info_configurations, None) is None
	True
	
	or simply:
	>>> from zope.generic.configuration.api import queryConfigurationData

	>>> queryConfigurationData(info, IMyConfiguration)is None
	True

The configuration subdirective of the information directive provides a mechanism
to register further configurations to an information:

	>>> from zope.generic.configuration.api import ConfigurationData
	>>> my_information_config = ConfigurationData(IMyConfiguration, {'my': u'My!'})

    >>> registerDirective('''
    ... <generic:information
    ...     interface="example.IFooMarker"
    ...     registry="example.ISpecialInformation"
    ...     label='Foo Specials' hint='Bla bla foo.'
    ...     >
    ...		<configuration
    ...		    interface="example.IMyConfiguration"
    ...			data="example.my_information_config"
    ...			/>
    ...	 </generic:information>
    ... ''')

    >>> info = api.queryInformation(IFooMarker, ISpecialInformation)
	>>> queryConfigurationData(info, IMyConfiguration) is my_information_config
	True
