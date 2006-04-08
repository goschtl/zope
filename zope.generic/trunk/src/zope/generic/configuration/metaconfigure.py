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

from zope.generic.information.api import queryInformation
from zope.generic.information.metaconfigure import provideInformation

from zope.generic.configuration import IConfigurationHandler
from zope.generic.configuration import IConfigurationHandlerConfiguration
from zope.generic.configuration import IConfigurationHandlerInformation
from zope.generic.configuration import IConfigurationHandlerType
from zope.generic.configuration import IConfigurationInformation
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations

from zope.generic.configuration.base import ConfigurationData
from zope.generic.configuration.base import ConfigurationHandler



def configurationDirective(_context, interface, label=None, hint=None):
    """Provide new configuration information."""

    registry = IConfigurationInformation
    iface_type = IConfigurationType

    # assert type as soon as possible
    if not iface_type.providedBy(interface):
        alsoProvides(interface, iface_type)

    _context.action(
        discriminator = ('provideInformation', interface, registry),
        callable = provideInformation,
        args = (interface, registry, label, hint),
        )

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (None, interface, iface_type),
        )  


def provideConfigurationHandlerConfiguration(interface, handler):
    """Provide the handler to an configuration information."""
    
    registry = IConfigurationHandlerInformation
    info = queryInformation(interface, IConfigurationHandlerInformation)

    # this should never happen...
    if info is None:
        ConfigurationError('No configuration handler information for %s' 
                           % interface.__name__)

    # Eventually wrap a callable
    if not IConfigurationHandler.providedBy(handler):
        handler = ConfigurationHandler(handler, interface)

    configurations = IConfigurations(info)
    # create configuration data
    data = ConfigurationData(IConfigurationHandlerConfiguration, {'handler': handler})
    # set configuration data
    configurations[IConfigurationHandlerConfiguration] = data



def configurationHandlerDirective(_context, interface, handler, label=None, hint=None):
    """Register a public configuration handler."""

    # assert type as soon as possible
    if not IConfigurationHandlerType.providedBy(interface):
        alsoProvides(interface, IConfigurationHandlerType)

    registry = IConfigurationHandlerInformation

    _context.action(
        discriminator = ('provideInformation', interface, registry),
        callable = provideInformation,
        args = (interface, registry, label, hint),
        )
    
    _context.action(
        discriminator = ('provideConfigurationHandlerConfiguration', interface, handler),
        callable = provideConfigurationHandlerConfiguration,
        args = (interface, handler),
        )
