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
from zope.component import provideUtility
from zope.component import IFactory
from zope.configuration.exceptions import ConfigurationError
from zope.security.checker import CheckerPublic
from zope.security.checker import InterfaceChecker

from zope.generic.informationprovider.api import getInformationProvider
from zope.generic.informationprovider.api import provideInformation
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective
from zope.generic.informationprovider.metaconfigure import provideInformationProvider
from zope.generic.face import IKeyfaceType
from zope.generic.face.api import toDescription
from zope.generic.face.api import toDottedName
from zope.generic.face.metaconfigure import keyfaceDirective
from zope.generic.operation.api import assertOperation
from zope.generic.operation.api import provideOperationConfiguration

from zope.generic.factory import IFactoryInformation
from zope.generic.factory.factory import Factory



def factoryDirective(_context, keyface, class_, type=None, operations=(), input=None,
                     providesFace=False, notifyCreated=False, storeInput=False,
                     label=None, hint=None):
    """Register a public factory."""
    # preconditions
    if isinstance(class_, ModuleType):
        raise ConfigurationError('Implementation attribute must be a class')

    # assert keyface type
    if not IKeyfaceType.providedBy(keyface):
        keyfaceDirective(_context, keyface, type)

    registry = IFactoryInformation
    
    # set label and hint
    label, hint = toDescription(keyface, label, hint)

    # how to invoke the factory
    if operations and input:
        mode = 3
    
    elif operations:
        mode = 2
    
    elif input:
        mode = 1
    
    else:
        mode = 0

    if mode and providesFace:
        output = keyface

    # create and proxy type factory
    factory = Factory(class_, keyface, providesFace, storeInput, 
                      notifyCreated, label, hint, mode) 
    component = proxify(factory, InterfaceChecker(IFactory, CheckerPublic))
    
    _context.action(
        discriminator = ('provideUtility', keyface),
        callable = provideUtility,
        args = (component, IFactory, toDottedName(keyface)),
        )

    if mode != 0:
        # create operation wrapper
        operation = assertOperation(operations, keyface, input, output)

        _context.action(
            discriminator = ('provideInformationProvider', keyface, registry),
            callable = provideInformationProvider,
            args = (keyface, registry, label, hint),
            )
    
        _context.action(
            discriminator = ('provideOperationConfiguration', keyface),
            callable = provideOperationConfiguration,
            args = (keyface, operation, registry, input, output),
            )
