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

from zope.annotation import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.component.interface import provideInterface
from zope.component import provideUtility
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import AttributeConfigurations
from zope.generic.face import IConfaceType
from zope.generic.face.api import ensureInformationProvider
from zope.generic.face.api import getNextInformationProvider
from zope.generic.face.api import toDescription
from zope.generic.face.api import toDottedName
from zope.generic.face.base import _global_information_hook
from zope.generic.face.base import _local_information_hook
from zope.generic.face.metaconfigure import faceDirective


# provide adapter via __conform__ mechanism
_global_information_hook[IAnnotations] = AttributeAnnotations
_global_information_hook[IConfigurations] = AttributeConfigurations
_local_information_hook[IAnnotations] = AttributeAnnotations
_local_information_hook[IConfigurations] = AttributeConfigurations



def provideConfiguration(keyface, conface, configuration_keyface, configuration):
    """Provide a configuration for a certain type marker."""

    info = getNextInformationProvider(keyface, conface)
    
    configurations = IConfigurations(info)
    configurations[configuration_keyface] = configuration



def provideAnnotation(keyface, conface, annotation_key, annotation):
    """Provide an annotation for a certain type marker."""

    info = getNextInformationProvider(keyface, conface)
    
    annotations = IAnnotations(info)
    annotations[annotation_key] = annotation



class InformationProviderDirective(object):
    """Provide a new information of a certain information registry."""

    def __init__(self, _context, keyface, conface, label=None, hint=None):
        self._keyface = keyface
        self._context = _context
        self._conface = conface

        # set label and hint
        label, hint = toDescription(keyface, label, hint)
        self._label = label
        self._hint = hint
    
        # assert type as soon as possible
        faceDirective(_context, keyface=keyface, conface=None, type=conface)

        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._keyface),
            )
    
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (None, self._conface),
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
                'informationprovider.configuration', self._keyface, self._conface, keyface),
                callable = provideConfiguration,
                args = (self._keyface, self._conface, keyface, configuration),
                )

        # handle annotation
        elif key and annotation:

            _context.action(
                discriminator = (
                'informationprovider.annotation', self._keyface, self._conface, key),
                callable = provideAnnotation,
                args = (self._keyface, self._conface, key, annotation),
                )

        # handle wrong usage
        else:
            raise ConfigurationError('Information subdirective must provide ' +
                'key and annotation or keyface and configuration.')
                