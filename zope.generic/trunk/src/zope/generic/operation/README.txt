=========
Operation
=========

Step 1: A few people develop generic base operations
----------------------------------------------------

An operation is a reusable processing unit. The unit is also marked by a
dedicated interface:
    
    >>> class IMakeSiteOperation(interface.Interface):
    ...    """This operation makes a folderish context to a site."""

    >>> class ISetupPAUOperation(interface.Interface):
    ...    """Setup a PAU within the context."""

    >>> class IConfigureAnythingOperation(interface.Interface):
    ...    """Write a configuration."""


If needed we have specify new or we can reuse existing input and output
configuration schema.

    >>> from zope.schema import TextLine

    >>> class IPAUConfig(interface.Interface):
    ...    """Configuration information to setup a pau."""
    ...    a = TextLine(required=False, default=u'Default pau config.')

    >>> class IAnyInputConfig(interface.Interface):
    ...    """Input configuration for the any application."""
    ...    a = TextLine()
    ...    b = TextLine(required=False)
    ...    c = TextLine(required=False)

    >>> class IAConfig(interface.Interface):
    ...    """Output a configuration."""
    ...    a = TextLine()

    >>> class IBConfig(interface.Interface):
    ...    """Output b configuration."""
    ...    b = TextLine()


    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IPAUConfig"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IAnyInputConfig"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IAConfig"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IBConfig"
    ...     />
    ... ''') 

The operation can be implemented in different ways:

    >>> def makeSiteOperation(context, *pos, **kws):
    ...     print 'makeSiteOperation'

    >>> def setupPAUOperation(context, *pos, **kws):
    ...     print 'setupPAUOperation'

    >>> def configureAnythingOperation(context, *pos, **kws):
    ...     print 'configureAnythingOperation'


    >>> registerDirective('''
    ... <generic:operation
    ...     interface="example.IMakeSiteOperation"
    ...     operations="example.makeSiteOperation"
    ...     />
    ... ''')

    >>> registerDirective('''
    ... <generic:operation
    ...     interface="example.ISetupPAUOperation"
    ...     operations="example.setupPAUOperation"
    ...     input="example.IPAUConfig"
    ...     />
    ... ''')

    >>> registerDirective('''
    ... <generic:operation
    ...     interface="example.IConfigureAnythingOperation"
    ...     operations="example.configureAnythingOperation"
    ...     input="example.IPAUConfig"
    ...     />
    ... ''')

Step 2: Build a complex operation by using the base operations
--------------------------------------------------------------

    >>> class IMakeSiteSetupPAUConfigureAnythingOperation(interface.Interface):
    ...    """Use the other three operation as nested information."""

    >>> class IComplexConfig(interface.Interface):
    ...    """Output complex configuration."""
    ...    pau = TextLine()
    ...    any_a = TextLine()
    ...    any_b = TextLine()
    ...    any_c = TextLine()

    >>> def privateOperation(context, *pos, **kws):
    ...    print 'privateOperation'

    >>> registerDirective('''
    ... <generic:configuration
    ...     interface="example.IComplexConfig"
    ...     />
    ... ''') 

    >>> registerDirective('''
    ... <generic:operation
    ...     interface="example.IMakeSiteSetupPAUConfigureAnythingOperation"
    ...     operations="example.IMakeSiteOperation example.setupPAUOperation
    ...         example.configureAnythingOperation example.privateOperation"
    ...     input="example.IComplexConfig"
    ...     output=""
    ...     />
    ... ''')

For each operation directive we registered an operation information. This
operation information can be retrieved:

    >>> from zope.generic.information.api import registeredInformations

    >>> listing = list(registeredInformations(api.IOperationInformation))
    >>> len(listing)
    4

    >>> config = api.queryOperationConfiguration(IMakeSiteSetupPAUConfigureAnythingOperation)
    >>> config.operation(None)
    makeSiteOperation
    setupPAUOperation
    configureAnythingOperation
    privateOperation

