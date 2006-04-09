===================================
How to use the information package?
===================================

We are developing a logger framework that can be used by user-application
domains and supplier-application domains.

Therefore we provide two public information registries for the members of our
orthagonal application domain such as suppliers. The log-supplier-information 
registry is holding supplier-specific informations. The log-user-information 
registry is holding user-specific informations.

In order to implement such an information registry we have to declare an
*key-like* interface extending the IInformation interface:

	>>> from zope.generic.information import IInformation
	
	>>> class ILogSupplierInformation(IInformation):
	...		"""Store log supplier information."""

	>>> class ILogUserInformation(IInformation):
	...		"""Store log user information."""

This specialized information interface has to be registered later by 
informationRegistry-directive.

Such an extended information is logical container for configurations and
annotations. In our framework example we have now to specify concrete
configuration that are registered to the two registries by the corresponding
member group.

A supplier has to provide global log instance (dotted name) and an optional
time formatter. We capture this configuration information within a configuration
that can be attached to a dedicated supplier information.

	>>> from zope.interface import Interface
	>>> from zope.configuration.fields import GlobalObject
	>>> from zope.schema import BytesLine

	>>> class ILogConfiguration(Interface):
	...		"""Define the log output."""
	...		log = GlobalObject(title=u'Log')
	...		timeFormat = BytesLine(title=u'Time Format', required=False, default='%d.%m.%y')

This configuration should be registered by using the configuration directive:

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="zope.generic.example.ILogConfiguration"
    ...     />
    ... ''') 

A user has to provide logger configuration. This configuration defines the
selected logger and a user-specific source tag:

	>>> from zope.configuration.fields import GlobalInterface

	>>> class ILoggerConfiguration(Interface):
	...		"""Define the log output."""
	...		logger = GlobalInterface(title=u'Logger')
	...		sourceTag = BytesLine(title=u'Source Tag', required=False, default='     ')   

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="zope.generic.example.ILoggerConfiguration"
    ...     />
    ... ''') 

TODO: Should be a dependency between informationRegistry and its configuration?

    >>> registerDirective('''
    ... <generic:informationRegistry
    ...     interface='zope.generic.example.ILogSupplierInformation'
    ...     />
    ... ''')

    >>> registerDirective('''
    ... <generic:informationRegistry
    ...     interface='zope.generic.example.ILogUserInformation'
    ...     />
    ... ''')

The third part of our framework is the logger itself. The logger will be
implmented as an adapter. We have to declare the logger interface:

	>>> class ILogger(Interface):
	...		"""Log."""
	...		def log(message):
	...			"""Log the message."""

	>>> from zope.interface import implements
	>>> from zope.component import adapts
	>>> from zope.generic.information import IInformationDeclaration

	>>> class Logger(object):
	...		"""Generic logger adapter."""
	...		implements(ILogger)
	...		adapts(IInformationDeclaration)
	...		def __init__(self, context):
	...			self.context = context
	...		def log(self, message):
	...			id = IInformationDeclaration(self.context())
	...			info = queryInformation(id.interface, ILogUserInformation)



After the registration we can retrieve the registries using the
queryInformationRegistry function:

	>>> from zope.generic.information.api import queryInformationRegistry
	
	>>> supplier_registry =  queryInformationRegistry(ILogSupplierInformation)
	>>> supplier_registry.label
	u'ILogSupplierInformation'
	>>> supplier_registry.hint
	u'Store log supplier information.'

	>>> user_registry =  queryInformationRegistry(ILogUserInformation)
	>>> user_registry.label
	u'ILogUserInformation'
	>>> user_registry.hint
	u'Store log user information.'

