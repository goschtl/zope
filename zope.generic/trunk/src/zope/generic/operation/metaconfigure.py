##############################################################################
#
# Copyright (c) 2005, 2006 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import ConfigurationData
from zope.generic.informationprovider.api import provideInformation
from zope.generic.informationprovider.api import queryInformation
from zope.generic.informationprovider.api import queryInformationProvider
from zope.generic.informationprovider.metaconfigure import provideInformationProvider

from zope.generic.operation import IOperation
from zope.generic.operation import IOperationConfiguration
from zope.generic.operation import IOperationInformation
from zope.generic.operation import IOperationType
from zope.generic.operation.base import Operation
from zope.generic.operation.base import OperationChain


def _assertOperation(handler, keyface=None):
    """Assert that we get an operation."""

    if IOperation.providedBy(handler):
        return handler
    
    if IOperationType.providedBy(handler):
        registry = IOperationInformation
        info = queryInformationProvider(handler, IOperationInformation)

        if info is None:
            ConfigurationError('Operation %s does not exist.' % handler.__name__)

        config = queryInformation(info, IOperationConfiguration)

        if config is None:
            ConfigurationError('OperationConfiguration for Operation %s does not exist.' % handler.__name__)

        return config.operation

    # asume callabe (context)
    return Operation(handler, keyface)



def provideOperationConfiguration(keyface, operations=(), input=(), output=()):
    """Provide the handler to an configuration information."""
    
    registry = IOperationInformation
    info = queryInformationProvider(keyface, IOperationInformation)

    # this should never happen...
    if info is None:
        ConfigurationError('No operation information for %s' 
                           % keyface.__name__)

    if len(operations) == 0:
        # hidding overwrite -> pass handler
        operation = _assertOperation(None, keyface)
    
    elif len(operations) == 1:
        operation = _assertOperation(operations[0], keyface)
    
    else:
        operation = OperationChain([_assertOperation(handler) for handler in operations], keyface)

    configurations = IConfigurations(info)
    # create and set configuration data
    provideInformation(info, IOperationConfiguration, 
        {'operation': operation, 'input': tuple(input), 'output': tuple(output)})



def operationDirective(_context, keyface, operations=(), input=(), output=(), label=None, hint=None):
    """Register a public operation."""

    # assert type as soon as possible
    if not IOperationType.providedBy(keyface):
        alsoProvides(keyface, IOperationType)

    registry = IOperationInformation

    _context.action(
        discriminator = ('provideInformationProvider', keyface, registry),
        callable = provideInformationProvider,
        args = (keyface, registry, label, hint),
        )

    _context.action(
        discriminator = ('provideOperationConfiguration', keyface),
        callable = provideOperationConfiguration,
        args = (keyface, operations, input, output),
        )
