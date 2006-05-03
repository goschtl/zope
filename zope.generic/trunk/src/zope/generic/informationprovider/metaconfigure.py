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
from zope.component import provideUtility
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import ConfigurationData
from zope.generic.face import IConfaceType
from zope.generic.face import IKeyfaceType
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.generic.face.api import getConface
from zope.generic.face.api import getKeyface
from zope.generic.face.api import toDescription
from zope.generic.face.api import toDottedName

from zope.generic.informationprovider.base import GlobalInformationProvider



def getInformationProvider(object=None, conface=IUndefinedContext):
    """Evaluate the next information provider utility for an object or keyface."""

    keyface = getKeyface(object)
    if conface is None:
        conface = getConface(object)

    try:
        provider = getUtility(conface, toDottedName(keyface))
        # return only provider that is or extends a certain context.
        if provider.conface == conface:
            return provider
    except:
        pass

    raise KeyError('Missing information provider %s at %s.' % (keyface.__name__, conface.__name__))



def ensureInformationProvider(keyface, conface):
    """Provide an information provider."""

    # preconditions
    if not IConfaceType.providedBy(conface):
        raise TypeError('Conface requires %s.' % IConfaceType.__name__)

    if not IKeyfaceType.providedBy(keyface):
        raise TypeError('Keyface requires %s.' % IKeyfaceType.__name__)

    # essentials
    name = toDottedName(keyface)

    provider = queryUtility(conface, name)

    # register
    if not (provider and provider.conface == conface):

        # type key face by its context interface
        alsoProvides(keyface, conface)

        # provide information provider utility
        provider = GlobalInformationProvider(conface, keyface)
        provideUtility(provider, conface, name=name)

    return provider



def provideConfiguration(keyface, conface, configuration_keyface, configuration):
    """Provide a configuration for a certain type marker."""

    if type(configuration) is dict:
        configuration = ConfigurationData(configuration_keyface, configuration)

    info = getInformationProvider(keyface, conface)
    
    configurations = IConfigurations(info)
    configurations[configuration_keyface] = configuration



def provideAnnotation(keyface, conface, annotation_key, annotation):
    """Provide an annotation for a certain type marker."""

    info = getInformationProvider(keyface, conface)
    
    annotations = IAnnotations(info)
    annotations[annotation_key] = annotation



class InformationProviderDirective(object):
    """Provide a new information of a certain information registry."""

    def __init__(self, _context, keyface=IUndefinedKeyface, conface=IUndefinedContext):
        # preconditions
        if IConfaceType.providedBy(keyface):
            raise ConfigurationError('Key interface %s can not be registered '
                                     'as context interface too.' % 
                                     keyface.__name__)
    
        if conface and IKeyfaceType.providedBy(conface):
            raise ConfigurationError('Context interface %s can not be '
                                     'registered as key interface too.' % 
                                     conface.__name__)

        # assign variables for the subdirecitives
        self._keyface = keyface
        self._context = _context
        self._conface = conface

        # provide type as soon as possilbe
        if not IKeyfaceType.providedBy(keyface):
            provideInterface(None, keyface, IKeyfaceType)

        if not IConfaceType.providedBy(conface):
            provideInterface(None, conface, IConfaceType)

        # ensure the corresponding information provider
        ensureInformationProvider(keyface, conface)

    def __call__(self):
        "Handle empty/simple declaration."
        return ()

    def information(self, _context, keyface=None, configuration=None, key=None, annotation=None):
        """Add a configuration to the information provider."""
        # handle configuration
        if keyface and configuration is not None:
            # preconditions
            if not (keyface.providedBy(configuration) or type(configuration) is dict):
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
                