====
Type
====

An object provides often serval interfaces. This package provides a interace 
based type assoziation in a way like *classes* or *types* do. Typeable object
provides by adaption or implementation access to a type marker. This type
marker can be used to lookup further information about the referenced type.

For each interface typed by our type marker type (IUndefinedContext) we provied a type 
factory that can create instaces of this certain *logical* type.

Furthermore a type information utility will be provided. This type information
allows to annotate additonal stuff like using the annotations and configurations
mechanism.

Informations provided by the type information should be accounted by the handling
of instances marked by a certain type marker interface.

The type directive does extend the information directive
(see zope.generic.configuration).


Base type directive
-------------------

In our example we register type using the generic:content directive. Therefore we
need an type marker:

    >>> class IFooMarker(interface.Interface):
    ...     pass

The only thing to register a specific logical type is this type marker interface.
The package offers four different generic implementation such as Object,
Contained, Container and Folder (Site) that you might use as implementation of
your logical type. Certainly you can provide your own implementation. Such an
implementation should implement at least the marker ITypeable and a corresponding
adapter to ITypedContent.

In our example we will use a simple generic object:

	>>> from zope.generic.content import api

	>>> api.IDirectlyTypedContent.implementedBy(api.Object)
	True

    >>> registerDirective('''
    ... <generic:content
    ...     keyface="example.IFooMarker"
    ...     >
    ...    <factory class='zope.generic.content.api.Object'
    ...        />
    ... </generic:content>
    ... ''')

After the typed is registered the type marker will provide IUndefinedContext:

	>>> from zope.generic.face import IUndefinedContext

    >>> IUndefinedContext.providedBy(IFooMarker)
    True

You can create instances of the registered logical type:

	>>> foo = api.createObject(IFooMarker)
	>>> typed = api.ITypedContent(foo)
	>>> typed.keyface == IFooMarker
	True

In our example we use a generic directly typed implementation. In those cases
the instance will provide the type marker too:

	>>> IFooMarker.providedBy(foo)
	True

A corresponding type information utility will be available. Your can
retrieve this utility using the conventional utility api:

    >>> from zope.component import queryUtility
    >>> from zope.generic.face.api import toDottedName

    >>> provider = queryUtility(IUndefinedContext, toDottedName(IFooMarker))

    >>> provider.keyface == IFooMarker
    True

There is convenience function for the lookup of corresponding type information.
You can lookup the type information by the type marker interface or an object
providing ITypedContent by implementation or adaption:

    >>> from zope.generic.informationprovider.api import getInformationProvider

	>>> getInformationProvider(IFooMarker) == provider
	True

    >>> getInformationProvider(foo.keyface) == provider
    True


Type subdirectives
------------------

There are serveral subdirectives like:

-	configurations (see zope.generic.configuration)
-	initializer

You can extend type informations by the annotations and configurations mechanism
like the information will do.

First we will provide a new bar type including an additional configuration:

    >>> class IBarMarker(interface.Interface):
    ...     pass

Then we provide two example configurations for our example:

	>>> from zope.schema import TextLine

    >>> class IAnyConfiguration(interface.Interface):
    ...     any = TextLine(title=u'Any')

    >>> class IOtherConfiguration(interface.Interface):
    ...		other = TextLine(title=u'Other')
    ...		optional = TextLine(title=u'Other', required=False, default=u'Default bla.')

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IAnyConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IOtherConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

	>>> from zope.generic.configuration.api import ConfigurationData
	>>> typedata = ConfigurationData(IAnyConfiguration, {'any': u'Guguseli from Type!'})
	>>> IAnyConfiguration.providedBy(typedata)
	True

We can provide a specific intializer handler:

	>>> def barInitializer(context, *pos, **kws):
	...		print 'Initializing bar'

Additionaly we can add other operation base object event handlers:

    >>> def objectEventHandler(context, event):
    ...     print 'Guguseli from object event.'


After all we register our component using the informationProvider and content
directive:

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IBarMarker"
    ...     >
    ...   <information
    ...       keyface='example.IAnyConfiguration'
    ...       configuration='example.typedata'
    ...       />
    ... </generic:informationProvider>
    ... ''')

    >>> registerDirective('''
    ... <generic:content
    ...     keyface="example.IBarMarker"
    ...     label='Bar Type' hint='Bla bla bla.'
    ...     >
    ...   <factory
    ...        class='zope.generic.content.api.Object'
    ...        input='example.IOtherConfiguration'
    ...        operations='example.barInitializer'
    ...        storeInput='True'
    ...        />
    ...    <adapter
    ...        provides='example.IAnyConfiguration'
    ...        acquire='True'
    ...        />
    ...    <handler
    ...        event='zope.component.interfaces.IObjectEvent'
    ...        operations='example.objectEventHandler'
    ...        />
    ... </generic:content>
    ... ''')

Now we can create an instance of the logical type. We defined an initializer
interface. Doing the **kws parameter are stored as configuration to the object.
If we do not satify the declaration an KeyError is raised:

	>>> api.createParameter(IBarMarker) == IOtherConfiguration
	True

	>>> bar = api.createObject(IBarMarker)
	Traceback (most recent call last):
	...
	TypeError: __init__ requires 'other' of 'IOtherConfiguration'.

    >>> bar = api.createObject(IBarMarker, other=u'Specific initialization data.')
    Guguseli from object event.
    Initializing bar

This registration attached the specific configuration to the type information.
You can retrieve type information by a typed instance or the marker type itself
using the following convenience function:

    >>> from zope.generic.informationprovider.api import queryInformation

	>>> queryInformation(IAnyConfiguration, IBarMarker).any
	u'Guguseli from Type!'

	>>> queryInformation(IAnyConfiguration, bar.keyface).any
	u'Guguseli from Type!'

	>>> queryInformation(IOtherConfiguration, IBarMarker) is None
	True

This configuration is type specific. You cannot lookup any object- or 
instance-specific configuration, but you can use a function that `acquires`
different configurations:

    >>> from zope.generic.informationprovider.api import acquireInformation
    

	>>> queryInformation(IAnyConfiguration, bar) is None
	True

	>>> queryInformation(IOtherConfiguration, bar).other
	u'Specific initialization data.'

	>>> acquireInformation(IAnyConfiguration, bar).any
	u'Guguseli from Type!'

	>>> acquireInformation(IOtherConfiguration, bar).other
	u'Specific initialization data.'

    >>> from zope.generic.configuration.api import IConfigurations
	>>> objectdata = ConfigurationData(IAnyConfiguration, {'any': u'Guguseli from Object!'})
	>>> IConfigurations(bar)[IAnyConfiguration] = objectdata
	
	>>> queryInformation(IAnyConfiguration, bar).any
	u'Guguseli from Object!'

	>>> acquireInformation(IAnyConfiguration, bar).any
	u'Guguseli from Object!'

The configurationAdapter subdirective provides an adapter too:

    >>> IOtherConfiguration(bar)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ... example.IOtherConfiguration>) 

    >>> IAnyConfiguration(bar).any
    u'Guguseli from Object!'

If we remove the object's configuration the adapter will invoke
the type configuration, but only the object's configuration can be set:

    >>> from zope.generic.informationprovider.api import deleteInformation
    >>> deleteInformation(IAnyConfiguration, bar)

    >>> IAnyConfiguration(bar).any
    u'Guguseli from Type!'

    >>> IAnyConfiguration(bar).any = u'Guguseli from Object another time!'
    >>> IAnyConfiguration(bar).any
    u'Guguseli from Object another time!'

Now we like to invoke an type-specific event handler:

    >>> from zope.component.interfaces import IObjectEvent
    >>> from zope.component.interfaces import ObjectEvent
    >>> from zope.event import notify

    >>> event = ObjectEvent(bar)
    >>> notify(event)
    Guguseli from object event.
    
    >>> notify(ObjectEvent(object()))