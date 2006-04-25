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
from zope.app.component.metaconfigure import adapter

from zope.generic.configuration.api import ConfigurationAdapterClass
from zope.generic.configuration.api import ConfigurationAdapterProperty
from zope.generic.factory.metaconfigure import factoryDirective
from zope.generic.informationprovider.api import provideInformation
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective

from zope.generic.type import ITypeInformation
from zope.generic.type import ITypeType
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



class TypeDirective(InformationProviderDirective):
    """Provide a new logical type."""

    # mark types with a type marker type
    _information_type = ITypeType


    def __init__(self, _context, keyface, label=None, hint=None):        
        # register types within the type information registry
        registry = ITypeInformation
        super(TypeDirective, self).__init__(_context, keyface, registry, label, hint)

    def factory(self, _context, class_, operations=(), input=None,
                providesKeyface=True, notifyCreated=True, storeInput=True):
        """Add factory."""
        factoryDirective(_context, self._keyface, class_, None, operations, input,
                     providesKeyface, notifyCreated, storeInput,
                     self._label, self._hint)


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
