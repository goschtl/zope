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

from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError

from zope.generic.configuration import IConfigurations
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.generic.informationprovider.api import queryInformation
from zope.generic.informationprovider.api import queryInformationProvider
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective

from zope.generic.operation import IOperation
from zope.generic.operation import IOperationConfiguration
from zope.generic.operation import IOperationType
from zope.generic.operation.base import Operation
from zope.generic.operation.base import OperationPipe



def assertOperation(handlers, keyface=None, input=None, output=None):
    """Assert that we get an operation."""

    # handle operations tuple or lists
    if type(handlers) == tuple or type(handlers) == list:
        if len(handlers) > 1:
            return OperationPipe([assertOperation(handler) 
                                 for handler in handlers], 
                                 keyface, input, output)

        elif len(handlers) == 1:
            handler = handlers[0]

        else:
            handler=None

    # assume that handlers is a single handler
    else:
        handler = handlers

    # nothing to do, this is already an information
    if IOperation.providedBy(handler):
        return handler
    
    # sometimes we use an do nothing operation
    elif handler is None:
        return Operation(None, keyface, input, output)

    # evaluate an operation from a operation key interface
    elif IOperationType.providedBy(handler):
        info = queryInformationProvider(handler)

        if info is None:
            ConfigurationError('Operation %s does not exist.' % handler.__name__)

        config = queryInformation(IOperationConfiguration, info)

        if config is None:
            ConfigurationError('OperationConfiguration for Operation %s does not exist.' % handler.__name__)

        return config.operation

    # asume callabe (context)
    else:
        return Operation(handler, keyface, input, output)



def operationDirective(_context, keyface, conface=None, operations=(), input=None, output=None, label=None, hint=None):
    """Register a public operation."""

    if conface is None:
        conface = IUndefinedContext

    # provide type as soon as possilbe
    if not IOperationType.providedBy(keyface):
        provideInterface(None, keyface, IOperationType)      

    # register the operatio using the information provider directive
    directive = InformationProviderDirective(_context, keyface, conface)

    # create operation wrapper
    operation = assertOperation(operations, keyface, input, output)
    
    directive.information(_context, keyface=IOperationConfiguration, 
        configuration={'operation': operation, 'input': input, 'output': output})

