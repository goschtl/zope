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

from zope.generic.configuration.api import IConfigurations

from zope.generic.information import IInformation
from zope.generic.information import IInformationRegistryInformation
from zope.generic.information import IInformationRegistryType
from zope.generic.information.base import Information
from zope.generic.information.helper import dottedName
from zope.generic.information.helper import queryInformation



def provideInformation(interface, registry, label=None, hint=None, factory=None):
    """Provide new information for the given registry-interface.

    Register an information as utiliy under registry-interface using
    the dotted name of the interface as utility name:

        >>> class ISpecialInformation(IInformation):
        ...    pass

        >>> from zope.interface import Interface
        >>> class IFooMarker(Interface):
        ...    pass

        >>> provideInformation(IFooMarker, ISpecialInformation)

    The information can be queried using the following method:

        >>> from zope.generic.information.helper import queryInformation
        >>> info = queryInformation(IFooMarker, ISpecialInformation)
        >>> info.interface == IFooMarker
        True
        >>> ISpecialInformation.providedBy(info)
        True

    """

    # precondition
    if not registry.extends(IInformation):
        raise ValueError('Registry must extend %s.' % IInformation.__name__)

    if factory is None:
        factory = Information
    
    component = factory(interface, registry, label, hint)

    if not registry.providedBy(component):
        raise ValueError('Factory must implement %s.' % registry.__name__)
    
    provideUtility(component, provides=registry, name=dottedName(interface))



def provideConfiguration(interface, registry, configuration, data):
    """Provide configuration for a certain type marker."""

    info = queryInformation(interface, registry)
    
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
            discriminator = ('provideInformation', self._interface, self._registry),
            callable = provideInformation,
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



class InformationRegistryDirective(InformationDirective):
    """Provide a new information registry."""

    _information_type = IInformationRegistryType

    def __init__(self, _context, interface, label=None, hint=None):
        super(InformationRegistryDirective, self).__init__(_context, interface, IInformationRegistryInformation, label, hint)
