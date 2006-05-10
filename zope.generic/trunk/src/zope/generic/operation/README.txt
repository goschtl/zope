=========
Operation
=========

Step 1: A few people develop generic base operations
----------------------------------------------------

An operation is a reusable processing unit. The unit is also marked by a
dedicated interface:

    >>> class IAnyOperation(interface.Interface):
    ...    """Write a configuration."""

Such an operation consists of an input-declaration, an 
output-declaration and a corresponding handler.

    >>> from zope.schema import TextLine

    >>> class IAnyInput(interface.Interface):
    ...    """A possible input declaration for any operation."""
    ...    a = TextLine()
    ...    b = TextLine(required=False)
    ...    c = TextLine(required=False, default=u'c default')

    >>> class IAnyOutput(interface.Interface):
    ...    """A possible output declaration for any operation."""
    ...    b = TextLine()

    >>> from zope.generic.configuration.api import parameterToConfiguration
    >>> from zope.generic.configuration.api import ConfigurationData

    >>> def anyOperation(context, *pos, **kws):
    ...     input = parameterToConfiguration(IAnyInput, *pos, **kws)
    ...     print 'Any input: a=%s, b=%s, c=%s.' % (input.a, input.b, input.c)
    ...     print 'Operate on *%s*.' % context
    ...     return ConfigurationData(IAnyOutput, {'b': u'b operated'})

We have to register those parts:

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IAnyInput"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IAnyOutput"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:operation
    ...     keyface="example.IAnyOperation"
    ...     operations="example.anyOperation"
    ...     input="example.IAnyInput"
    ...     output="example.IAnyOutput"
    ...     />
    ... ''')

We can retrieve and introspect any registered operation by the following ways
using itself or its keyface. For each operation directive an operation 
information will be registered:

    >>> operation = api.getOperation(IAnyOperation)

    >>> api.inputParameter(operation) is IAnyInput
    True
    >>> api.inputParameter(IAnyOperation) is IAnyInput
    True

    >>> api.outputParameter(operation) is IAnyOutput
    True
    >>> api.outputParameter(IAnyOperation) is IAnyOutput
    True

You can call an operation on a context:

    >>> operation('corresponding Context')
    Traceback (most recent call last):
    ...
    TypeError: __init__ requires 'a' of 'IAnyInput'.

    >>> output = operation('corresponding Context', u'a bla')
    Any input: a=a bla, b=None, c=c default.
    Operate on *corresponding Context*.

    >>> api.outputParameter(operation).providedBy(output)
    True
    >>> output.b
    u'b operated'


Step 2: Build a complex operation reusing the base operations
-------------------------------------------------------------

For this example we provide a few other example operations:

    >>> class IMakeSiteOperation(interface.Interface):
    ...    """This operation makes a folderish context to a site."""

    >>> class ISetupPAUOperation(interface.Interface):
    ...    """Setup a PAU within the context."""

    >>> class IPAUConfig(interface.Interface):
    ...    """Configuration information to setup a pau."""
    ...    a = TextLine(required=False, default=u'Default pau config.')

    >>> def makeSiteOperation(context, *pos, **kws):
    ...     print 'Public operation: makeSiteOperation'

    >>> def setupPAUOperation(context, *pos, **kws):
    ...     print 'Public operation: setupPAUOperation'
    ...     input = parameterToConfiguration(IPAUConfig, *pos, **kws)
    ...     print 'Pau input: a=%s.' % (input.a)

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IPAUConfig"
    ...     />
    ... ''')

    >>> registerDirective('''
    ... <generic:operation
    ...     keyface="example.IMakeSiteOperation"
    ...     operations="example.makeSiteOperation"
    ...     />
    ... ''')

    >>> registerDirective('''
    ... <generic:operation
    ...     keyface="example.ISetupPAUOperation"
    ...     operations="example.setupPAUOperation"
    ...     input="example.IPAUConfig"
    ...     />
    ... ''')

All of this registrations and the corresponding code might be provided by a
third party.

We will build a new pipped operation. Therefore we declare a new key
interface for the combined operations:

    >>> class IMakeSiteSetupPAUAndAnyOperation(interface.Interface):
    ...    """Invoke the other three operation."""

Regularly you will have to provide a new input configuration:

    >>> class IComplexConfig(interface.Interface):
    ...    """Output complex configuration."""
    ...    pau = TextLine()
    ...    any = TextLine()

    >>> registerDirective('''
    ... <generic:configuration
    ...     keyface="example.IComplexConfig"
    ...     />
    ... ''') 

Often you have to extend the base operations. Therefore you can include a simple
function. It's not necessary to register such a private function as a public
function using the operation directive. In our example we do need four private 
operations, one is setting the IAnyConfiguration and IPauConfiguration to the 
context and providing the pau configuration, the secound and third will provide
the input parameter for the pau- and the any-operation, and the fourth should
avoid the return value of the any-operation:

    >>> from zope.generic.configuration.api import ConfigurationData
    >>> from zope.generic.informationprovider.api import getInformation
    >>> from zope.generic.informationprovider.api import provideInformation

    >>> def inputToConfigurations(context, *pos, **kws):
    ...    print 'Private operation: inputToConfigurations'
    ...    input = parameterToConfiguration(IComplexConfig, *pos, **kws)
    ...    provideInformation(IAnyInput, {'a': input.any}, context)
    ...    provideInformation(IPAUConfig, {'a': input.pau}, context)

    >>> def pauInitializer(context, *pos, **kws):
    ...    print 'Private operation: pauInitializer'
    ...    return getInformation(IPAUConfig, context)

    >>> def anyOperationInitializer(context, *pos, **kws):
    ...    print 'Private operation: anyOperationInitializer'
    ...    return getInformation(IAnyInput, context)

    >>> def void(context, *pos, **kws):
    ...    print 'Private operation: void'

At least we register the complex operation using the operation marker interfaces
and the private operations:

    >>> registerDirective('''
    ... <generic:operation
    ...     keyface="example.IMakeSiteSetupPAUAndAnyOperation"
    ...     operations="example.inputToConfigurations example.IMakeSiteOperation 
    ...         example.pauInitializer example.setupPAUOperation
    ...         example.anyOperationInitializer example.anyOperation
    ...         example.void"
    ...     input="example.IComplexConfig"
    ...     />
    ... ''')

Now we will check the behavior of the example on a dedicated context:

    >>> from zope.generic.informationprovider import IAttributeInformable
    >>> from zope.generic.face.api import Face

    >>> class DummyContext(Face):
    ...     interface.implements(IAttributeInformable)
    ...     def __repr__(self):
    ...         return 'DummyContext'

    >>> context = DummyContext()

    >>> operation = api.getOperation(IMakeSiteSetupPAUAndAnyOperation)

    >>> operation(context, any=u'a any', pau=u'a pau')
    Private operation: inputToConfigurations
    Public operation: makeSiteOperation
    Private operation: pauInitializer
    Public operation: setupPAUOperation
    Pau input: a=a pau.
    Private operation: anyOperationInitializer
    Any input: a=a any, b=None, c=c default.
    Operate on *DummyContext*.
    Private operation: void
