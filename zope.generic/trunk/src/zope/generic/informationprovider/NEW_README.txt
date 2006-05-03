===================================
How to use the information package?
===================================

Part one: Provide a framework based on information providers
------------------------------------------------------------

We are developing a logger framework that can be used by user-application
domains and supplier-application domains.

Therefore we provide two public information contexts for the members of our
orthagonal application domains. The supplier-context information provider 
should hold supplier-specific informations. The user-context information 
provider should hold user-specific informations.

In order to implement those information contexts we have to declare two context 
interfaces (short: conface con[text inter]face):

    >>> class ISupplierContext(interface.Interface):
    ...     """Store log supplier information."""

    >>> class IUserContext(interface.Interface):
    ...     """Store log user information."""

Within those contexts we like to provide log configuration information. In our
example logger frame work  we need to configure a specific log:

    >>> from zope.interface import Interface
    >>> from zope.configuration.fields import GlobalObject
    >>> from zope.schema import BytesLine

    >>> class ILogConfiguration(Interface):
    ...     """Define the log output."""
    ...     timeFormat = BytesLine(title=u'Time Format', required=False, default='%d.%m.%y')
    ...     header = BytesLine(title=u'Header', required=False, default='General')

We like to use the configuration mechansim of zope.generic.configuration. Within
this configuration facility we have to type the configuration interface by
the zope.generic.configuration.IConfiguration context interface. This should
be done the following way:

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.ILogConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''')

    >>> from zope.generic.face import IKeyfaceType
    >>> from zope.generic.configuration import IConfigurationType

    >>> IKeyfaceType.providedBy(ILogConfiguration)
    True
    >>> IConfigurationType.providedBy(ILogConfiguration)
    True

Components that are using our log framework can provide their own log 
configuration by adding a log configuration to the corresponding information
provider. That has to be done by information that is set for an key interface
within a dedicated context (ISupplierContext and IUserContext in our example).
For all components that will not provide their own log configuration information
we should provide default configuration within both contexts. This can be done
by ommiting the keyface attribute of information provider directive. This
assigns an information provider to IUndefinedKeyface

You can provide all configuration value, but at least you have to provide
the required ones.

    >>> from zope.generic.configuration.api import ConfigurationData

    >>> supplier_default = {'header': 'Supplier', 'timeFormat': '%y.%m.%d'}

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     conface="example.ISupplierContext"
    ...     >
    ...   <information
    ...       keyface="example.ILogConfiguration"
    ...       configuration="example.supplier_default"
    ...       />
    ... </generic:informationProvider>
    ... ''')

Not provided optional data are taken from the default field values:

    >>> user_default = {}

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     conface="example.IUserContext"
    ...     >
    ...   <information
    ...       keyface="example.ILogConfiguration"
    ...       configuration="example.user_default"
    ...       />
    ...  </generic:informationProvider>
    ... ''')

You can retrieve this configurations the following way:

    >>> provider_at_suppliercontext = api.getInformationProvider(conface=ISupplierContext)
    >>> data = api.getInformation(ILogConfiguration, provider_at_suppliercontext)
    >>> data.header, data.timeFormat
    ('Supplier', '%y.%m.%d')

    >>> provider_at_usercontext = api.getInformationProvider(conface=IUserContext)
    >>> data = api.getInformation(ILogConfiguration, provider_at_usercontext)
    >>> data.header, data.timeFormat
    ('General', '%d.%m.%y')

Last we have to define our application - the log itself.

    >>> class ILog(Interface):
    ...     """Log."""
    ...     def __call__(message):
    ...         """Log the message."""

    >>> import time
    >>> from zope.generic.face import IAttributeFaced
    >>> from zope.generic.face import IUndefinedKeyface, IUndefinedContext

    >>> class Log(object):
    ...     """Generic log adapter."""
    ...     __keyface__ = IUndefinedKeyface
    ...     __conface__ = IUndefinedContext
    ...
    ...     interface.implements(ILog, IAttributeFaced)
    ...     component.adapts(None)
    ...
    ...     def __init__(self, context):
    ...         self.context = context
    ...     def __call__(self, message):
    ...         keyface = api.getKeyface(self.context)
    ...         conface = api.getConface(self)
    ...         provider = api.acquireInformationProvider(keyface, conface)
    ...         logconfig = api.getInformation(ILogConfiguration, provider)
    ...         return '%s: %s, %s' % (logconfig.header, message, 
    ...                               time.strftime(logconfig.timeFormat))

We have to provide two contextual adapters. Preferably they will be implemented
as named adapter:

    >>> class SupplierLog(Log):
    ...     __conface__ = ISupplierContext

    >>> class UserLog(Log):
    ...     __conface__ = IUserContext

    >>> component.provideAdapter(SupplierLog, provides=ILog, 
    ...                         name=api.toDottedName(ISupplierContext))

    >>> component.provideAdapter(UserLog, provides=ILog, 
    ...                         name=api.toDottedName(IUserContext))


We are done. Our log framework implementation is finished. This work is done only
once a time. Now other developer can use this framework.


Part two: Use a framework based on information providers
--------------------------------------------------------

You can use the logger framework *as it is* without any further registrations or 
configuration:

    >>> my = object()
    
    >>> supplier_log = component.getAdapter(my, ILog, api.toDottedName(ISupplierContext))
    >>> entry = supplier_log('Guguseli'); entry
    'Supplier: Guguseli, ...'

    >>> entry == 'Supplier: Guguseli, %s' % time.strftime('%y.%m.%d')
    True

    >>> user_log = component.getAdapter(my, ILog, api.toDottedName(IUserContext))
    >>> entry = user_log('Guguseli'); entry
    'General: Guguseli, ...'

    >>> entry == 'General: Guguseli, %s' % time.strftime('%d.%m.%y')
    True

Often you like to configure the framework for dedicated components. You have
to define an own key interface that allows you to provide specific configuration:

    >>> class IMy(interface.Interface):
    ...     """My own key interface."""

    >>> my_supplier = ConfigurationData(ILogConfiguration, {'header': 'My Supplier'})

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IMy"
    ...     conface="example.ISupplierContext"
    ...     >
    ...   <information
    ...       keyface="example.ILogConfiguration"
    ...       configuration="example.my_supplier"
    ...       />
    ... </generic:informationProvider>
    ... ''')


    >>> from zope.generic.face.base import Face

    >>> class My(Face):
    ...    __keyface__ = IMy

    >>> my = My()

We configured a log configuration within the supplier context, but none within
the user context:

    >>> supplier_log = component.getAdapter(my, ILog, api.toDottedName(ISupplierContext))
    >>> entry = supplier_log('Guguseli'); entry
    'My Supplier: Guguseli, ...'

    >>> user_log = component.getAdapter(my, ILog, api.toDottedName(IUserContext))
    >>> entry = user_log('Guguseli'); entry
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IMy at IUserContext.'

If we like to acquire from the default user context configuration, we have
to derive our marker from IUndefinedKeyface.

    >>> class IMy(IUndefinedKeyface):
    ...     """My own key interface."""

    >>> my_supplier = ConfigurationData(ILogConfiguration, {'header': 'My Supplier'})

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IMy"
    ...     conface="example.ISupplierContext"
    ...     >
    ...   <information
    ...       keyface="example.ILogConfiguration"
    ...       configuration="example.my_supplier"
    ...       />
    ... </generic:informationProvider>
    ... ''')


    >>> from zope.generic.face.base import Face

    >>> class My(Face):
    ...    __keyface__ = IMy

    >>> my = My()

    >>> supplier_log = component.getAdapter(my, ILog, api.toDottedName(ISupplierContext))
    >>> entry = supplier_log('Guguseli'); entry
    'My Supplier: Guguseli, ...'

    >>> user_log = component.getAdapter(my, ILog, api.toDottedName(IUserContext))
    >>> entry = user_log('Guguseli'); entry
    'General: Guguseli, ...'

As soon as we configure the user context information provider we ca overwrite
the default settings, too:

    >>> my_user = ConfigurationData(ILogConfiguration, {'header': 'My User'})

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IMy"
    ...     conface="example.IUserContext"
    ...     >
    ...   <information
    ...       keyface="example.ILogConfiguration"
    ...       configuration="example.my_user"
    ...       />
    ... </generic:informationProvider>
    ... ''')

    >>> user_log = component.getAdapter(my, ILog, api.toDottedName(IUserContext))
    >>> entry = user_log('Guguseli'); entry
    'My User: Guguseli, ...'
