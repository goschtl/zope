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

from zope.interface import alsoProvides

from zope.generic.face import IFace

from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import INestedConfiguration
from zope.generic.configuration.field import ISubConfiguration
from zope.generic.configuration.field import ISubConfigurationDict
from zope.generic.configuration.field import ISubConfigurationList
from zope.generic.field import IToUnicode



def provideConfigurationType(interface):
    """Mark an interface as IConfigurationType."""

    alsoProvides(interface, IConfigurationType)



_marker = object()

def configurationToDict(configuration, all=False, tounicode=False):
    """Extract values from configuration to a dictionary.

    First we have to specify a test configurtion interface:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        >>> from zope.generic.field.api import EuroDate
        
        >>> class IAnyConfiguration(Interface):
        ...    a = TextLine()
        ...    b = TextLine(required=False)
        ...    c = TextLine(required=False, readonly=True, default=u'c default')
        ...    d = EuroDate(required=False)

    Minimal data without defaults:

        >>> from zope.generic.configuration.base import createConfiguration
        >>> configuration = createConfiguration(IAnyConfiguration, {'a': u'a bla'})
        >>> api.configurationToDict(configuration)
        {'a': u'a bla'}

    Including defaults:
        >>> api.configurationToDict(configuration, all=True)
        {'a': u'a bla', 'c': u'c default', 'b': None, 'd': None}

    Unicode support:
        >>> configuration = createConfiguration(IAnyConfiguration, {'a': u'a bla', 'd': u'12.3.2006'}, fromunicode=True)
        >>> api.configurationToDict(configuration, all=True)
        {'a': u'a bla', 'c': u'c default', 'b': None, 'd': datetime.date(2006, 3, 12)}
        >>> api.configurationToDict(configuration, all=True, tounicode=True)
        {'a': u'a bla', 'c': u'c default', 'b': None, 'd': u'12.03.2006'}
    """
    data = {}
    keyface = IFace(configuration).keyface

    for name in keyface:
        value = getattr(configuration, name, _marker)
        field = keyface[name]
        
        if INestedConfiguration.providedBy(field):
            if ISubConfiguration.providedBy(field):
                if value:
                    data[name] = configurationToDict(value, all, tounicode)

            elif ISubConfigurationList.providedBy(field):
                if ISubConfiguration.providedBy(field.value_type):
                    data[name] = [configurationToDict(v, all, tounicode) for v in value]
                # regular objects
                else:
                    data[name] = [v for v in value]

            elif ISubConfigurationDict.providedBy(field):
                if ISubConfiguration.providedBy(field.value_type):
                    data[name] = dict([(k, configurationToDict(v, all, tounicode)) for k, v in value.items()])
                # regular objects
                else:
                    data[name] = dict([item for item in value.items()])

        # no sub-configuraiton
        else:
            if field.required is False:
                if value is not _marker and value != field.default:
                   data[name] = value
    
                elif value == field.default:
                    if all:
                        data[name] = value
    
                else:
                    if all:
                        data[name] = field.default
    
            elif value is not _marker:
                data[name] = value
    
            else:
                raise RuntimeError('Data is missing', name)

            if tounicode and IToUnicode.providedBy(field):
                data[name] = field.toUnicode(data[name])

    return data



def namesInOrder(configuration, required_only=True):
    """Evaluate the relevant order of positional arguments.

    The relevant order of positional arguments is evaluated by a configuration
    key interface.

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IAnyConfiguration(Interface):
        ...    a = TextLine()
        ...    b = TextLine(required=False)
        ...    c = TextLine(required=False, readonly=True, default=u'c bla')
        ...    d = TextLine()

        >>> api.namesInOrder(IAnyConfiguration)
        ['a', 'd']

        >>> api.namesInOrder(IAnyConfiguration, False)
        ['a', 'b', 'c', 'd']
    """
    
    if required_only:
        names = [name for name in configuration if configuration[name].required is True]
    else:
        names = [name for name in configuration]

    names.sort()
    return names
