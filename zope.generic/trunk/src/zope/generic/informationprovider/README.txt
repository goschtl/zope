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
    [('IMyFoo', <GlobalInformationProvider IMyFoo at ISpecialContext>)]

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

    >>> api.queryInformation('example.my_annotation', provider) is None
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

    >>> api.queryInformation(IMyConfiguration, provider) is None
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
    ...   <information
    ...       key="example.my_annotation"
    ...       annotation="example.my_annotation"
    ...       />
    ...   <information
    ...       keyface="example.IMyConfiguration"
    ...       configuration="example.my_configuration"
    ...       />
    ... </generic:informationProvider>
    ... ''')

    >>> provider = api.queryInformationProvider(IMyFoo, ISpecialContext)
    >>> api.queryInformation('example.my_annotation', provider) is my_annotation
    True

    >>> provider = api.queryInformationProvider(IMyFoo, ISpecialContext)
    >>> api.queryInformation(IMyConfiguration, provider) is my_configuration
    True

Further information provider exploration
----------------------------------------

The following example should provide a further exploration about information
provider an theirs behavior:

    >>> class IMyContext(interface.Interface):
    ...    pass

    >>> class IFoo(interface.Interface):
    ...    pass

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IFoo" />
    ... ''')

An information provider should provide the contex interface itself. Further more
it is responsible to mark the key interface by the context interface:

    >>> api.IUndefinedContext.providedBy(IFoo)
    True
    >>> api.IUndefinedContext.providedBy(api.getInformationProvider(IFoo))
    True

Simple Lookup using queryInformationProvider and getInformationProvider
------------------------------------------------------------------------

    >>> api.getInformationProvider(IFoo)
    <GlobalInformationProvider IFoo at IUndefinedContext>

    >>> api.queryInformationProvider(IFoo)
    <GlobalInformationProvider IFoo at IUndefinedContext>

A key error is raised or the default is returned if no information provider 
could be evalutated for a certain key interface, context interface pair:

    >>> api.getInformationProvider(IFoo, IMyContext)
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

    >>> api.queryInformationProvider(IFoo, IMyContext, 'Missing information provider.')
    'Missing information provider.'

Attention information provider does not acquire from more specialized interface
like the regular utility lookup does:

    >>> class IYourContext(IMyContext):
    ...    pass

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IFoo"
    ...     conface="example.IYourContext" />
    ... ''')

    >>> component.getUtility(IMyContext, api.toDottedName(IFoo))
    <GlobalInformationProvider IFoo at IYourContext>

    >>> api.getInformationProvider(IFoo, IMyContext)
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

Complex Lookup using acquireInformationProvider
-----------------------------------------------

You can use the acquireInformationProvider function to lookup more general
information providers. The acquisition is based on the __iro__ of the key and
context interface. You will start within the first context looking up all key
interface in order of the __iro__. If no information provider could be found
the context will be switch to the next more general context. There the same
procedure will start until an information provider could be found. If no
information could be found a key error is raised.

In our example we cannot acquire anything therefore we still expect a key error.

    >>> api.acquireInformationProvider(IFoo, IMyContext) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IMyContext.'

We could derive a context from IUndefinedContext. That way we could acquire the
first provider registered to IFoo and IUndefinedContext:

    >>> class IOurContext(api.IUndefinedContext):
    ...    pass

    >>> api.getInformationProvider(IFoo, IOurContext) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IFoo at IOurContext.'

    >>> api.acquireInformationProvider(IFoo, IOurContext)
    <GlobalInformationProvider IFoo at IUndefinedContext>

The other way round we can play with key interface inheritance:

    >>> class IBar(interface.Interface):
    ...    pass

    >>> api.acquireInformationProvider(IBar) 
    Traceback (most recent call last):
    ...
    KeyError: 'Missing information provider IBar at IUndefinedContext.'

    >>> class IFooBar(IFoo, IBar):
    ...    pass

    >>> api.acquireInformationProvider(IFooBar) 
    <GlobalInformationProvider IFoo at IUndefinedContext>

If we register a new information provider to IBar and IUndefinedContext, we can
observe the following behavior:

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IBar" />
    ... ''')

    >>> api.acquireInformationProvider(IBar)
    <GlobalInformationProvider IBar at IUndefinedContext>

    >>> api.acquireInformationProvider(IFooBar) 
    <GlobalInformationProvider IFoo at IUndefinedContext>

    >>> class IBarFoo(IBar, IFoo):
    ...    pass

    >>> api.acquireInformationProvider(IBarFoo) 
    <GlobalInformationProvider IBar at IUndefinedContext>

But we always get the most specialized one:

    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <GlobalInformationProvider IBar at IUndefinedContext> 

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IBarFoo" />
    ... ''')

    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <GlobalInformationProvider IBarFoo at IUndefinedContext>

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IBar"
    ...     conface="example.IOurContext" />
    ... ''')

    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <GlobalInformationProvider IBar at IOurContext>

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IBarFoo"
    ...     conface="example.IOurContext" />
    ... ''')

    >>> api.acquireInformationProvider(IBarFoo, IOurContext) 
    <GlobalInformationProvider IBarFoo at IOurContext>

Complex Lookup using getInformationProvidersFor
-----------------------------------------------

Last but not least you can lookup all information provider registered for a 
certain key interface or context interface using getInformationProvidersFor
function.

If you lookup the providers for a context interface, you will get an iterator
that returns (keyface, provider) pairs:

    >>> [i.__name__ for i,p in api.getInformationProvidersFor(IOurContext)]
    ['IBar', 'IBarFoo']

If you lookup the providers for a key interface, you will get an iterator
which returns (conface, provider) pairs:

    >>> [i.__name__ for i,p in api.getInformationProvidersFor(IBarFoo)]
    ['IOurContext', 'IUndefinedContext']


Components can suggest key and context interfaces
-------------------------------------------------

You can use the IFace interface to provide key interface and context interface
by a component itself. Therefore the conface parameter has to be None:

    >>> from zope.generic.face.api import Face

    >>> class Foo(Face):
    ...    __keyface__ = IFoo
    ...    __conface__ = IOurContext

    >>> foo = Foo()
    >>> foo.keyface == IFoo
    True
    >>> foo.conface == IOurContext
    True

    >>> api.acquireInformationProvider(foo, None) 
    <GlobalInformationProvider IFoo at IUndefinedContext>

    >>> api.acquireInformationProvider(foo) 
    <GlobalInformationProvider IFoo at IUndefinedContext>


    >>> class Bar(Face):
    ...    __keyface__ = IBar
    ...    __conface__ = IOurContext

    >>> bar = Bar()
    >>> bar.keyface == IBar
    True
    >>> bar.conface == IOurContext
    True

    >>> api.acquireInformationProvider(bar, None) 
    <GlobalInformationProvider IBar at IOurContext>

    >>> api.acquireInformationProvider(bar) 
    <GlobalInformationProvider IBar at IUndefinedContext>


Ini-file based configurations for an information provider
---------------------------------------------------------

The configuration file holds several configuration in the ini-file style.

    >>> from zope.interface import Interface
    >>> from zope.schema import Text, TextLine
    
    >>> class IOneConfiguration(Interface):
    ...    textLine = TextLine(title=u'TextLine')
    ...    text = Text(title=u'Text', required=False, default=u'Bla\\n')

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IOneConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> from zope.schema import Bool, Int

    >>> class IOtherConfiguration(Interface):
    ...    bool = Bool(title=u'Bool')
    ...    int = Int(title=u'Int', required=False, default=42)

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IOtherConfiguration"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()
    >>> iniFile = os.path.join(temp_dir, 'example.ini')
    >>> open(iniFile, 'w').write('''
    ... [example.IOneConfiguration]
    ... textline = Foo
    ... text : Bla bla bla bla.
    ... 
    ... [example.IOtherConfiguration]
    ... bool = True
    ... int = 77
    ... ''')

    >>> registerDirective('''
    ... <generic:informationProvider
    ...     keyface="example.IFoo"
    ...     conface="example.ISpecialContext"
    ...     >
    ...   <informations
    ...       iniFiles="%s"
    ...       />
    ...     </generic:informationProvider>
    ... ''' % iniFile)

    >>> foo_config = api.getInformation(IOneConfiguration, IFoo, ISpecialContext)
    >>> foo_config.textLine
    u'Foo'

    >>> foo_config.text
    u'Bla bla bla bla.'

    >>> bar_config =  api.getInformation(IOtherConfiguration, IFoo, ISpecialContext)
    >>> bar_config.bool
    True

    >>> bar_config.int
    77

    >>> import shutil
    >>> shutil.rmtree(temp_dir)
