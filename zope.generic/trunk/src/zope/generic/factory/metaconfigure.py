##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

from types import ModuleType

from zope.app.component.metaconfigure import proxify
from zope.component import IFactory
from zope.component import provideUtility
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.security.checker import CheckerPublic
from zope.security.checker import InterfaceChecker

from zope.generic.face import IUndefinedContext
from zope.generic.face.api import toDescription
from zope.generic.face.api import toDottedName
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective
from zope.generic.operation import INoParameter
from zope.generic.operation import IOperationConfiguration
from zope.generic.operation import IUndefinedParameter
from zope.generic.operation.api import assertOperation

from zope.generic.factory import IFactoryType
from zope.generic.factory.factory import Factory



def factoryDirective(_context, keyface, class_, operations=(), input=INoParameter,
                     providesFace=False, notifyCreated=False, storeInput=False, useConfig=True):
    """Register a public factory."""
    # preconditions
    if isinstance(class_, ModuleType):
        raise ConfigurationError('Implementation attribute must be a class')

    # provide type as soon as possilbe
    if not IFactoryType.providedBy(keyface):
        provideInterface(None, keyface, IFactoryType) 

    # set label and hint
    label, hint = toDescription(keyface)

    # create and proxy type factory
    factory = Factory(class_, keyface, providesFace, storeInput, 
                      notifyCreated, label, hint, useConfig) 
    proxied = proxify(factory, InterfaceChecker(IFactory, CheckerPublic))
    
    _context.action(
        discriminator = ('provideUtility', keyface),
        callable = provideUtility,
        args = (proxied, IFactory, toDottedName(keyface)),
        )

    if useConfig:
        # does the output provide the keyface?
        output = IUndefinedParameter
        if providesFace:
            output = keyface

        # register for undefined context
        conface = IUndefinedContext

        # register the operatio using the information provider directive
        directive = InformationProviderDirective(_context, keyface, conface)
    
        # create operation wrapper
        operation = assertOperation(operations, keyface, input, output)
        
        directive.information(_context, keyface=IOperationConfiguration, 
            configuration={'operation': operation, 'input': input, 'output': output})
