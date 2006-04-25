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

from zope.app.annotation import IAnnotations
from zope.app.component.interface import provideInterface
from zope.component import provideUtility
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import ConfigurationData
from zope.generic.keyface.api import toDescription
from zope.generic.keyface.api import toDottedName

from zope.generic.informationprovider.base import InformationProvider
from zope.generic.informationprovider import IInformationProvider
from zope.generic.informationprovider import IInformationProviderInformation
from zope.generic.informationprovider import IInformationProviderType
from zope.generic.informationprovider.api import queryInformationProvider



def provideInformationProvider(keyface, registry=IInformationProviderInformation, label=None, hint=None, factory=None):
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

        >>> from zope.generic.configuration.helper import queryInformationProvider
        >>> info = queryInformationProvider(IFooMarker, ISpecialInformation)
        >>> info.keyface == IFooMarker
        True
        >>> ISpecialInformation.providedBy(info)
        True

    """

    # precondition
    if not registry.extends(IInformationProvider):
        raise ValueError('Registry must extend %s.' % IInformationProvider.__name__)

    if factory is None:
        factory = InformationProvider
    
    component = factory(keyface, registry, label, hint)

    if not registry.providedBy(component):
        raise ValueError('Factory must implement %s.' % registry.__name__)
    
    provideUtility(component, provides=registry, name=toDottedName(keyface))



def provideConfiguration(keyface, registry, configuration_keyface, configuration):
    """Provide a configuration for a certain type marker."""

    info = queryInformationProvider(keyface, registry)
    
    configurations = IConfigurations(info)
    configurations[configuration_keyface] = configuration



def provideAnnotation(keyface, registry, annotation_key, annotation):
    """Provide an annotation for a certain type marker."""

    info = queryInformationProvider(keyface, registry)
    
    annotations = IAnnotations(info)
    annotations[annotation_key] = annotation



class InformationProviderDirective(object):
    """Provide a new information of a certain information registry."""
    
    _information_type = None

    def __init__(self, _context, keyface, registry, label=None, hint=None):
        self._keyface = keyface
        self._context = _context
        self._registry = registry

        # set label and hint
        label, hint = toDescription(keyface, label, hint)
        self._label = label
        self._hint = hint
    
        # assert type as soon as possible
        if self._information_type is not None:
            alsoProvides(keyface, self._information_type)
    
        _context.action(
            discriminator = ('provideInformationProvider', self._keyface, self._registry),
            callable = provideInformationProvider,
            args = (self._keyface, self._registry, label, hint),
            )
    
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._keyface),
            )
    
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._registry),
            )

    def __call__(self):
        "Handle empty/simple declaration."
        return ()

    def information(self, _context, keyface=None, configuration=None, key=None, annotation=None):
        """Add a configuration to the information provider."""
        # handle configuration
        if keyface and configuration:
            # preconditions
            if not keyface.providedBy(configuration):
                raise ConfigurationError('Data attribute must provide %s.' % keyface.__name__)
    
            _context.action(
                discriminator = (
                'informationprovider.configuration', self._keyface, self._registry, keyface),
                callable = provideConfiguration,
                args = (self._keyface, self._registry, keyface, configuration),
                )

        # handle annotation
        elif key and annotation:

            _context.action(
                discriminator = (
                'informationprovider.annotation', self._keyface, self._registry, key),
                callable = provideAnnotation,
                args = (self._keyface, self._registry, key, annotation),
                )

        # handle wrong usage
        else:
            raise ConfigurationError('Information subdirective must provide ' +
                'key and annotation or keyface and configuration.')
                