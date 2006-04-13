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
from zope.interface import alsoProvides

from zope.generic.information.metaconfigure import provideInformation

from zope.generic.configuration import IConfigurationInformation
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations

from zope.generic.configuration.base import ConfigurationData


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
