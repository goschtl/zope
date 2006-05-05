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

from ConfigParser import SafeConfigParser

from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import provideUtility
from zope.component import queryUtility
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import ITuple

from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration.api import ConfigurationData
from zope.generic.face import IConfaceType
from zope.generic.face import IKeyfaceType
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.generic.face.api import getConface
from zope.generic.face.api import getKeyface
from zope.generic.face.api import toDescription
from zope.generic.face.api import toDottedName
from zope.generic.face.api import toInterface

from zope.generic.informationprovider.base import GlobalInformationProvider
from zope.generic.informationprovider.helper import toConfigFaceTriple



def getInformationProvider(keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Get the information provider for an faced object or face-typed interface."""
    if conface is None:
        conface = getConface(keyface)

    if not IKeyfaceType.providedBy(keyface):
        keyface = getKeyface(keyface)

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


def nestedConfigurationData(configparser, section, keyface, prefix=''):
    """Nested configuration support."""

    missedArguments = []
    data = {}

    for name in keyface:
        field = keyface[name]
        lookup_name = prefix + name.lower()
        # evalutate name: config parser options are always lower case
        try:
            value = configparser.get(section, lookup_name)
            try:
                data[name] = field.fromUnicode(unicode(value))

            except:
                data[name] = IFromUnicode(field).fromUnicode(unicode(value))

        except:
            if IObject.providedBy(field) and IConfigurationType.providedBy(field.schema):
                subkeyface = field.schema
                try:
                    subdata = nestedConfigurationData(configparser, section, subkeyface, lookup_name + '.')
                except:
                    subdata = {}

                if subdata or field.required is True:
                    try:
                        data[name] = ConfigurationData(subkeyface, subdata)
                        continue
                    except:
                        if field.required is False:
                            continue

            elif ISequence.providedBy(field):
                counter = 0
                subfield = field.value_type
                sequence = []
                while True:
                    try:
                        value = configparser.get(section, lookup_name + '.' + str(counter))

                        try:
                            sequence.append(subfield.fromUnicode(unicode(value)))
            
                        except:
                            sequence.append(IFromUnicode(subfield).fromUnicode(unicode(value)))
            
                    except:
                        break
                    
                    counter += 1
                    
                if sequence or field.required is True:
                    if ITuple.providedBy(field):
                        data[name] = tuple(sequence)
    
                    else:
                        data[name] = sequence
                    
                    continue
            
            elif IDict.providedBy(field):
                sublookup_name = lookup_name + '.'
                sublookup_len = len(sublookup_name)
                subfield = field.value_type
                subdict = {}
                for key, value in configparser.items(section):
                    if len(key) > sublookup_len and key.startswith(sublookup_name):
                        subkey = key[sublookup_len:]
                        if subkey.count('.'):
                            raise NotImplementedError('Not supported yet!')

                        try:
                            value = configparser.get(section, key)

                            try:
                                subdict[subkey] = subfield.fromUnicode(unicode(value))
                
                            except:
                                subdict[subkey] = IFromUnicode(subfield).fromUnicode(unicode(value))
                
                        except:
                            break

                if subdict or field.required is True:
                    data[name] = subdict
                    continue

            if field.required is True:
                missedArguments.append(lookup_name)

    if missedArguments:
        raise TypeError("__init__ requires '%s' of '%s'." % (', '.join(missedArguments), keyface.__name__))

    return data



_marker = object()

def iniFileToConfiguration(path, strict=True):
    """Parse ini file to an iterator over keyface, configuration pairs."""

    configparser = SafeConfigParser()
    configparser.read(path)

    for section in configparser.sections():

        if strict:
            configuration, keyface, conface = toConfigFaceTriple(section)
            yield (configuration, keyface, conface, nestedConfigurationData(configparser, section, configuration))

        else:
            configuration = toInterface(section)
            yield (configuration, nestedConfigurationData(configparser, section, configuration))



class InformationProviderDirective(object):
    """Provide a new information provider."""

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

    def information(self, _context, keyface=None, configuration=None, key=None, annotation=None, iniFiles=()):
        """Add a configuration to the information provider."""

        # handle ini files
        if iniFiles:
            if keyface or configuration or key or annotation:
                raise ConfigurationError('Attribute iniFiles does not allow other attributes.')

            for path in iniFiles:
                for configuration, data in iniFileToConfiguration(path, False):
                     _context.action(
                        discriminator = (
                        'informationprovider.configuration', self._keyface, self._conface, configuration),
                        callable = provideConfiguration,
                        args = (self._keyface, self._conface, configuration, data),
                        )
 
        # handle configuration
        elif keyface and configuration is not None:
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



def multiInformationProvidersDirective(_context, iniFiles=()):
    """Ini-file based configurations for multi information provider."""
        
    for path in iniFiles:
        for configuration, keyface, conface, data in iniFileToConfiguration(path):
            # register corresponding configuration information
            # provide type as soon as possilbe
            if not IKeyfaceType.providedBy(keyface):
                provideInterface(None, keyface, IKeyfaceType)
    
            if not IConfaceType.providedBy(conface):
                provideInterface(None, conface, IConfaceType)
    
            # ensure the corresponding information provider
            ensureInformationProvider(keyface, conface)

            _context.action(
                discriminator = (
                'informationprovider.configuration', keyface, conface, configuration),
                callable = provideConfiguration,
                args = (keyface, conface, configuration, data),
                )
                
                