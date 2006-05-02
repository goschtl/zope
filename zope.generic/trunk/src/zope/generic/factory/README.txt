===============
Generic Factory
===============

Regular factories have two disadvantages:

    1.    The initialization parameters cannot be introspected
    2.    The factory id cannot be shared as easy as an interface

This package try to avoid those points:

    1.    You can declare the parameters parameters within input attribute
          using a configuration key interface.
    2.    The factory can be registered with and looked up by an key interface.

For simple example see factory.py

Complex sample
--------------

As usual first we have to declare an key interface for our implementation:

    >>> from zope.interface import Interface

    >>> class IMyInstance(Interface):
    ...     pass

Then we have to implement an example class with dedicated initalization
parameters:

    >>> from zope.generic.configuration import IAttributeConfigurable
    >>> from zope.generic.face import IAttributeFaced

    >>> class Example(object):
    ...    interface.implements(IAttributeFaced, IAttributeConfigurable)
    ...    def __init__(self, a, b, c):
    ...        print '__init__:', 'a=',a ,', b=', b, ', c=', c

Now we have to declare the signature for our key interface. We like to provide
default arguments. Afterward we register the schema as IConfiguration:

    >>> from zope.schema import TextLine

    >>> class IMyParameter(Interface):
    ...    a = TextLine()
    ...    b = TextLine(required=False)
    ...    c = TextLine(required=False, default=u'c default')

    >>> registerDirective('''
    ... <generic:interface
    ...     interface="example.IMyParameter"
    ...     type="zope.generic.configuration.IConfigurationType"
    ...     />
    ... ''') 

During the creation process we can invoke initializer operations. In our example
we are defining a simple handler, but you could use object providing IOperation
or interfaces providing IOperationType too:

    >>> def init_handler(context, *pos, **kws):
    ...    print 'initializing'

This stuff can be registered within the factory directive.

    >>> registerDirective('''
    ... <generic:factory
    ...     keyface="example.IMyInstance"
    ...     class="example.Example"
    ...     operations="example.init_handler"
    ...     input="example.IMyParameter"
    ...     providesFace="True"
    ...     storeInput="True"
    ...     notifyCreated="True"
    ...     />
    ... ''') 

The keyface defines the key interface to lookup the factory. The class
is the implementation. The operations attribute defines one operation or a
pipe of operations (see zope.generic.operation). Input declares the input
parameter. The attribute provideFace asserts that the key interface is
provided. Four cases are checked: 

1.  If the class does provide the keyface nothing happens. 

2.  If the instance provides zope.generic.face.IProvidesAttributeFaced
    the __keyface__ attribute is set and the updateDirectlyProvided is called.

3.  If zope.generic.face.IAttributeFaced is provided the the __keyface__ 
    attribute is set and the keyface is directly provided.

4.  Else only the keyface is directly provided.

The storeInput decides if the input configuration should be stored within the
instance's configurations. The notifyCreated is notifying an object created event.

After this registration we find the following stuff within the component
registration:

    >>> from zope.component.eventtesting import getEvents, clearEvents

    >>> clearEvents()

    >>> from zope.generic.face.api import toDottedName

    >>> util = component.getUtility(component.IFactory, name=toDottedName(IMyInstance))
    >>> util.keyface == IMyInstance
    True

    >>> from zope.generic.face import IUndefinedContext

    >>> util = component.getUtility(IUndefinedContext, name=toDottedName(IMyInstance))
    >>> util.keyface == IMyInstance
    True

    >>> from zope.generic.configuration import IConfigurations
    >>> from zope.generic.operation import IOperationConfiguration

    >>> configs_of_factory_info = IConfigurations(util)
    >>> create_config = IOperationConfiguration(configs_of_factory_info)
    >>> create_config.input == IMyParameter
    True
    >>> create_config.operation('ignore')
    initializing
    >>> create_config.output == IMyInstance
    True

Fortunately there is a convenience api for the daily questions:

Before you are going to invoke the factory you can look up the create parameters
for a certain key interface:

    >>> api.createParameter(IMyInstance) is IMyParameter
    True

You can create an instance, but don't forget to supply the input parameters:

    >>> ex = api.createObject(IMyInstance)
    Traceback (most recent call last):
    ... 
    TypeError: __init__ requires 'a' of 'IMyParameter'.

    >>> ex = api.createObject(IMyInstance, u'a bla')
    __init__: a= a bla , b= None , c= c default
    initializing

As you can see our intializer operation was invoked so as the regular intializer.

We selected to store the input. Therefore you can lookup the corresponding
configuration:

    >>> from zope.generic.informationprovider.api import getInformation
    >>> info = getInformation(ex, IMyParameter)
    >>> info.a, info.b, info.c
    (u'a bla', None, u'c default')

We selected object created event notification too:
    
    >>> events = getEvents()
    >>> len(events)
    1
    >>> events.pop().object is ex
    True

    >>> clearEvents()
