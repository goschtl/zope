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
from zope.app.component.metaconfigure import adapter
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.component.interfaces import IFactory
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements
from zope.security.checker import CheckerPublic
from zope.security.checker import InterfaceChecker

from zope.generic.component.api import toDottedName
from zope.generic.component.api import ConfigurationData
from zope.generic.component.api import provideInformation
from zope.generic.component.metaconfigure import InformationProviderDirective

from zope.generic.type import IInitializationHandler
from zope.generic.type import IInitializerConfiguration
from zope.generic.type import ITypeInformation
from zope.generic.type import ITypeType
from zope.generic.type.adapter import Initializer
from zope.generic.type.factory import TypeFactory
from zope.generic.type.helper import queryTypeInformation



def provideTypeConfiguration(interface, configuration, data):
    """Set configuration data into the context."""

    info = queryTypeInformation(interface)
    provideInformation(info, configuration, data)



class InitializationHandler(object):
    """Initialization handler.
    
    Wrap a callable:

        >>> def callable(context, *pos, **kws):
        ...     print context, pos, kws
        
        >>> init_handler = InitializationHandler(callable)
        
        >>> init_handler(1, 2, 3, x=4)
        1 (2, 3) {'x': 4}
    
    """

    implements(IInitializationHandler)

    def __init__(self, callable):
        self.__callable = callable

    def __call__(self, context, *pos, **kws):
        self.__callable(context, *pos, **kws)



class TypeDirective(InformationProviderDirective):
    """Provide a new logical type."""

    # mark types with a type marker type
    _information_type = ITypeType


    def __init__(self, _context, interface, class_, label=None, hint=None):
        # preconditions
        if isinstance(class_, ModuleType):
            raise ConfigurationError('Implementation attribute must be a class')
        
        # register types within the type information registry
        registry = ITypeInformation
        super(TypeDirective, self).__init__(_context, interface, registry, label, hint)

        # create and proxy type factory
        factory = TypeFactory(class_, self._interface) 
        component = proxify(factory, InterfaceChecker(IFactory, CheckerPublic))

        _context.action(
            discriminator = ('provideUtility', self._interface),
            callable = provideUtility,
            args = (component, IFactory, toDottedName(self._interface)),
            )

    def initializer(self, _context, interface=None, handler=None):
        """Add initializer."""
        # preconditions
        if interface is None and handler is None:
            raise ConfigurationError('Attribute interface or handler must be defined')

        data = {}
        if handler is not None:
            if not IInitializationHandler.providedBy(handler):
                handler = InitializationHandler(handler)

            data['handler'] = handler

        if interface is not None:
            data['interface'] = interface

        adapter(self._context, [Initializer], None, [self._interface], None, '', True, False)

        _context.action(
            discriminator = (
            'initializer', self._interface),
            callable = provideTypeConfiguration,
            args = (self._interface, IInitializerConfiguration, data),
            )
