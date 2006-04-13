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
from zope.component import provideUtility
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.component import IConfigurationInformation
from zope.generic.component import IConfigurationType
from zope.generic.component import IConfigurations
from zope.generic.component import IInformationProvider
from zope.generic.component import IInformationProviderInformation
from zope.generic.component import IInformationProviderType
from zope.generic.component.api import queryInformationProvider
from zope.generic.component.base import ConfigurationData
from zope.generic.component.base import InformationProvider
from zope.generic.component.helper import toDottedName


def provideInformationProvider(interface, registry=IInformationProviderInformation, label=None, hint=None, factory=None):
    """Provide new information for the given registry-interface.

    Register an information as utiliy under registry-interface using
    the dotted name of the interface as utility name:

        >>> class ISpecialInformation(IInformationProvider):
        ...    pass

        >>> from zope.interface import Interface
        >>> class IFooMarker(Interface):
        ...    pass

        >>> provideInformationProvider(IFooMarker, ISpecialInformation)

    The information can be queried using the following method:

        >>> from zope.generic.component.helper import queryInformationProvider
        >>> info = queryInformationProvider(IFooMarker, ISpecialInformation)
        >>> info.interface == IFooMarker
        True
        >>> ISpecialInformation.providedBy(info)
        True

    """

    # precondition
    if not registry.extends(IInformationProvider):
        raise ValueError('Registry must extend %s.' % IInformationProvider.__name__)

    if factory is None:
        factory = InformationProvider
    
    component = factory(interface, registry, label, hint)

    if not registry.providedBy(component):
        raise ValueError('Factory must implement %s.' % registry.__name__)
    
    provideUtility(component, provides=registry, name=toDottedName(interface))



def provideConfiguration(interface, registry, configuration, data):
    """Provide configuration for a certain type marker."""

    info = queryInformationProvider(interface, registry)
    
    configurations = IConfigurations(info)
    configurations[configuration] = data



class InformationDirective(object):
    """Provide a new information of a certain information registry."""
    
    _information_type = None

    def __init__(self, _context, interface, registry, label=None, hint=None):
        self._interface = interface
        self._context = _context
        self._registry = registry
    
        # assert type as soon as possible
        if self._information_type is not None:
            alsoProvides(interface, self._information_type)
    
        _context.action(
            discriminator = ('provideInformationProvider', self._interface, self._registry),
            callable = provideInformationProvider,
            args = (self._interface, self._registry, label, hint),
            )
    
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._interface),
            )
    
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._registry),
            )

    def __call__(self):
        "Handle empty/simple declaration."
        return ()

    def configuration(self, _context, interface, data):
        # preconditions
        if not interface.providedBy(data):
            raise ConfigurationError('Data attribute must provide %s.' % interface.__name__)

        _context.action(
            discriminator = (
            'InformationConfiguration', self._interface, self._registry, interface),
            callable = provideConfiguration,
            args = (self._interface, self._registry, interface, data),
            )



def configurationDirective(_context, interface, label=None, hint=None):
    """Provide new configuration information."""

    registry = IConfigurationInformation
    iface_type = IConfigurationType

    # assert type as soon as possible
    if not iface_type.providedBy(interface):
        alsoProvides(interface, iface_type)

    _context.action(
        discriminator = ('provideInformationProvider', interface, registry),
        callable = provideInformationProvider,
        args = (interface, registry, label, hint),
        )

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (None, interface, iface_type),
        )



class InformationRegistryDirective(InformationDirective):
    """Provide a new information registry."""

    _information_type = IInformationProviderType

    def __init__(self, _context, interface, label=None, hint=None):
        super(InformationRegistryDirective, self).__init__(_context, interface, IInformationProviderInformation, label, hint)
