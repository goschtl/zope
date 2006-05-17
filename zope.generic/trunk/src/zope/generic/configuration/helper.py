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


def provideConfigurationType(interface):
    """Mark an interface as IConfigurationType."""

    alsoProvides(interface, IConfigurationType)




_marker = object()

def configuratonToDict(configuration, all=False):
    """Extract values from configuration to a dictionary.

    First we have to specify a test configurtion interface:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IAnyConfiguration(Interface):
        ...    a = TextLine()
        ...    b = TextLine(required=False)
        ...    c = TextLine(required=False, readonly=True, default=u'c default')

    Minimal data without defaults:

        >>> from zope.generic.configuration.base import createConfiguration
        >>> configuration = createConfiguration(IAnyConfiguration, {'a': u'a bla'})
        >>> api.configuratonToDict(configuration)
        {'a': u'a bla'}

    Including defaults:
        >>> api.configuratonToDict(configuration, all=True)
        {'a': u'a bla', 'c': u'c default', 'b': None}

    """
    data = {}
    keyface = IFace(configuration).keyface

    for name in keyface:
        value = getattr(configuration, name, _marker)
        field = keyface[name]

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

    return data



def requiredInOrder(configuration):
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

        >>> api.requiredInOrder(IAnyConfiguration)
        ['a', 'd']
    
    """
    
    return [name for name in configuration if configuration[name].required is True]
