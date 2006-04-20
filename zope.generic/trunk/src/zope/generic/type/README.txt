====
Type
====

An object provides often serval interfaces. This package provides a interace 
based type assoziation in a way like *classes* or *types* do. Typeable object
provides by adaption or implementation access to a type marker. This type
marker can be used to lookup further information about the referenced type.

For each interface typed by our type marker type (ITypeType) we provied a type 
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

In our example we register type using the generic:type directive. Therefore we
need an type marker:

    >>> class IFooMarker(interface.Interface):
    ...     pass

The only thing to register a specific logical type is this type marker interface.
The package offers four different generic implementation such as Object,
Contained, Container and Folder (Site) that you might use as implementation of
your logical type. Certainly you can provide your own implementation. Such an
implementation should implement at least the marker ITypeable and a corresponding
adapter to ITyped.

In our example we will use a simple generic object:

	>>> from zope.generic.type import api
	>>> api.ITypeable.implementedBy(api.Object)
	True
	>>> api.IDirectlyTyped.implementedBy(api.Object)
	True

    >>> registerDirective('''
    ... <generic:type
    ...     keyface="example.IFooMarker"
    ...     label='Foo Type' hint='Bla bla bla.'
    ...	    class='zope.generic.type.api.Object'
    ...     />
    ... ''')

After the typed is registered the type marker will provide ITypeType:

	>>> from zope.generic.type import api

    >>> api.ITypeType.providedBy(IFooMarker)
    True

You can create instances of the registered logical type:

	>>> foo = api.createObject(IFooMarker)
	>>> typed = api.ITyped(foo)
	>>> typed.keyface == IFooMarker
	True

In our example we use a generic directly typed implementation. In those cases
the instance will provide the type marker too:

	>>> IFooMarker.providedBy(foo)
	True

A corresponding type information utility will be available. Your can
retrieve this utility using the conventional utility api:

    >>> from zope.component import queryUtility
    >>> from zope.generic.keyface.api import toDottedName

    >>> info = queryUtility(api.ITypeInformation, toDottedName(IFooMarker))

    >>> info.keyface == IFooMarker
    True
    >>> info.label
    u'Foo Type'
    >>> info.hint
    u'Bla bla bla.'

There is convenience function for the lookup of corresponding type information.
You can lookup the type information by the type marker interface or an object
providing ITyped by implementation or adaption:

	>>> api.queryTypeInformation(IFooMarker) == info
	True

    >>> api.queryTypeInformation(foo) == info
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
    ... <generic:keyface
    ...     keyface="example.IAnyConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:keyface
    ...     keyface="example.IOtherConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

	>>> from zope.generic.configuration.api import ConfigurationData
	>>> typedata = ConfigurationData(IAnyConfiguration, {'any': u'Guguseli from Type!'})
	>>> IAnyConfiguration.providedBy(typedata)
	True

We can provide a specific intializer:

	>>> def barInitializer(context, *pos, **kws):
	...		print 'Initializing ...'

After all we register our component using the type directive:

    >>> registerDirective('''
    ... <generic:type
    ...     keyface="example.IBarMarker"
    ...     label='Bar Type' hint='Bla bla bla.'
    ...	    class='zope.generic.type.api.Object'
    ...     >
    ...    <initializer
    ...			keyface='example.IOtherConfiguration'
    ...			handler='example.barInitializer'
    ...	   />
    ...	   <configuration
    ...	       keyface='example.IAnyConfiguration'
    ...        data='example.typedata'
    ...	   />
    ...    <configurationAdapter
    ...        keyface='example.IAnyConfiguration'
    ...       />
    ... </generic:type>
    ... ''')

Now we can create an instance of the logical type. We defined an initializer
interface. Doing the **kws parameter are stored as configuration to the object.
If we do not satify the declaration an KeyError is raised:

	>>> api.createParameter(IBarMarker) == IOtherConfiguration
	True

	>>> bar = api.createObject(IBarMarker)
	Traceback (most recent call last):
	...
	AttributeError: 'IOtherConfiguration' object has no attribute 'other'.

	>>> bar = api.createObject(IBarMarker, other=u'Specific initialization data.')
	Initializing ...

This registration attached the specific configuration to the type information.
You can retrieve type information by a typed instance or the marker type itself
using the following convenience function:

	>>> api.queryTypeConfiguration(IBarMarker, IAnyConfiguration).any
	u'Guguseli from Type!'

	>>> api.queryTypeConfiguration(bar, IAnyConfiguration).any
	u'Guguseli from Type!'

	>>> api.queryTypeConfiguration(IBarMarker, IOtherConfiguration) is None
	True

This configuration is type specific. You cannot lookup any object- or 
instance-specific configuration, but you can use a function that `acquires`
different configurations:

	>>> api.queryObjectConfiguration(bar, IAnyConfiguration) is None
	True

	>>> api.queryObjectConfiguration(bar, IOtherConfiguration).other
	u'Specific initialization data.'

	>>> api.acquireObjectConfiguration(bar, IAnyConfiguration).any
	u'Guguseli from Type!'

	>>> api.acquireObjectConfiguration(bar, IOtherConfiguration).other
	u'Specific initialization data.'

    >>> from zope.generic.configuration.api import IConfigurations
	>>> objectdata = ConfigurationData(IAnyConfiguration, {'any': u'Guguseli from Object!'})
	>>> IConfigurations(bar)[IAnyConfiguration] = objectdata
	
	>>> api.queryObjectConfiguration(bar, IAnyConfiguration).any
	u'Guguseli from Object!'

	>>> api.acquireObjectConfiguration(bar, IAnyConfiguration).any
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
    >>> deleteInformation(bar, IAnyConfiguration)

    >>> IAnyConfiguration(bar).any
    u'Guguseli from Type!'

    >>> IAnyConfiguration(bar).any = u'Guguseli from Object another time!'
    >>> IAnyConfiguration(bar).any
    u'Guguseli from Object another time!'
