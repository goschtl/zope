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

from zope.app.component.contentdirective import ClassDirective
from zope.app.component.metaconfigure import proxify
from zope.app.component.metaconfigure import adapter
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.component.interfaces import IFactory
from zope.configuration.exceptions import ConfigurationError
from zope.interface import implements
from zope.security.checker import CheckerPublic
from zope.security.checker import InterfaceChecker

from zope.generic.configuration.api import ConfigurationData
from zope.generic.informationprovider.api import provideInformation
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective
from zope.generic.keyface.api import toDottedName

from zope.generic.type import IInitializationHandler
from zope.generic.type import IInitializerConfiguration
from zope.generic.type import ITypeInformation
from zope.generic.type import ITypeType
from zope.generic.type.adapter import Initializer
from zope.generic.configuration.api import ConfigurationAdapterClass
from zope.generic.configuration.api import ConfigurationAdapterProperty
from zope.generic.type.factory import TypeFactory
from zope.generic.type.helper import queryTypeConfiguration
from zope.generic.type.helper import queryTypeInformation



def provideTypeConfiguration(keyface, configuration, data):
    """Set configuration data into the context."""

    info = queryTypeInformation(keyface)
    provideInformation(info, configuration, data)



_marker = object()

class _TypeConfigurationAdapterProperty(ConfigurationAdapterProperty):
    """Lookup type informations."""

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configurations = inst.__configurations__
        keyface = inst.__keyface__
        context = inst.__context__

        configuration = inst.__keyface__(configurations, None)
        if configuration is None:
            # Try to evaluate a type configuration
            configuration = queryTypeConfiguration(context, keyface)

        value = getattr(configuration, self._name, _marker)
        if value is _marker:
            field = self._field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self._name)

        return value



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


    def __init__(self, _context, keyface, class_, label=None, hint=None):
        # preconditions
        if isinstance(class_, ModuleType):
            raise ConfigurationError('Implementation attribute must be a class')
        
        # register types within the type information registry
        registry = ITypeInformation
        super(TypeDirective, self).__init__(_context, keyface, registry, label, hint)

        # create and proxy type factory
        factory = TypeFactory(class_, self._keyface) 
        component = proxify(factory, InterfaceChecker(IFactory, CheckerPublic))

        _context.action(
            discriminator = ('provideUtility', self._keyface),
            callable = provideUtility,
            args = (component, IFactory, toDottedName(self._keyface)),
            )

    def initializer(self, _context, keyface=None, handler=None):
        """Add initializer."""
        # preconditions
        if keyface is None and handler is None:
            raise ConfigurationError('Attribute keyface or handler must be defined')

        data = {}
        if handler is not None:
            if not IInitializationHandler.providedBy(handler):
                handler = InitializationHandler(handler)

            data['handler'] = handler

        if keyface is not None:
            data['keyface'] = keyface

        adapter(self._context, factory=[Initializer], provides=None, 
                for_=[self._keyface], permission=None, name='', trusted=True, 
                locate=False)

        _context.action(
            discriminator = (
            'initializer', self._keyface),
            callable = provideTypeConfiguration,
            args = (self._keyface, IInitializerConfiguration, data),
            )

    def configurationAdapter(self, _context, keyface, class_=None, writePermission=None, readPermission=None):
        """Provide a generic configuration adatper."""

        # we will provide a generic adapter class
        if class_ is None:
            class_ = ConfigurationAdapterClass(keyface, (), _TypeConfigurationAdapterProperty)

        # register class
        class_directive = ClassDirective(_context, class_)
        if writePermission:
            class_directive.require(_context, permission=writePermission, set_schema=[keyface])

        if readPermission:
            class_directive.require(_context, permission=readPermission, interface=[keyface])

        # register adapter
        adapter(self._context, factory=[class_], provides=keyface, 
                for_=[self._keyface], permission=None, name='', trusted=True, 
                locate=False)
