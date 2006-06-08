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

from zope.generic.face.api import getKeyface

from zope.generic.configuration import *
from zope.generic.configuration.adapter import AttributeConfigurations
from zope.generic.configuration.base import createConfiguration
from zope.generic.configuration.field import ISubConfiguration
from zope.generic.configuration.field import ISubConfigurationDict
from zope.generic.configuration.field import ISubConfigurationList
from zope.generic.configuration.field import SubConfiguration
from zope.generic.configuration.field import SubConfigurationDict
from zope.generic.configuration.field import SubConfigurationList
from zope.generic.configuration.helper import configurationToDict
from zope.generic.configuration.helper import provideConfigurationType
from zope.generic.configuration.helper import namesInOrder



def getConfiguration(context, keyface):
    """Evaluate a configuration."""
    return keyface(IConfigurations(context))



def queryConfiguration(context, keyface, default=None):
    """Evaluate a configuration or return default."""
    try:
        return getConfiguration(context, keyface)
    
    except:
        return default



def updateConfiguration(context, keyfaced_or_keyface, data=None):
    """Set or update a configuration to/of a context."""

    IConfigurations(context).update(keyfaced_or_keyface, data)



def deleteConfiguration(context, keyface):
    """Delete a configuration from a context."""

    del IConfigurations(context)[keyface]



def parameterToConfiguration(__keyface__, *pos, **kws):
    """Create configuration data

    The generic signature *pos, **kws can will be resolved into a configuration.

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IAnyConfiguration(Interface):
        ...    a = TextLine()
        ...    b = TextLine(required=False)
        ...    c = TextLine(required=False, readonly=True, default=u'c default')
        ...    d = TextLine()

    A: No arguments does not satisfy the configuration:

        >>> parameterToConfiguration(IAnyConfiguration)
        Traceback (most recent call last):
        ...
        TypeError: __init__ requires 'a, d' of 'IAnyConfiguration'.

    B: Provide the required as positionals:

        >>> config = parameterToConfiguration(IAnyConfiguration, u'a bla', u'd bla')
        >>> config.a, config.b, config.c, config.d
        (u'a bla', None, u'c default', u'd bla')

    C: Provide the required as positional and keyword:

        >>> config = parameterToConfiguration(IAnyConfiguration, u'a bla', d=u'd bla')
        >>> config.a, config.b, config.c, config.d
        (u'a bla', None, u'c default', u'd bla')

    D: Provide all required as keyword:

        >>> config = parameterToConfiguration(IAnyConfiguration, d=u'd bla', c=u'c bla', a=u'a bla')
        >>> config.a, config.b, config.c, config.d
        (u'a bla', None, u'c bla', u'd bla')

    E: You can also use an existing configuration as input:

        >>> parameterToConfiguration(IAnyConfiguration, config) == config
        True


    F: Provide the required as positional and keyword, do not messup the order otherwise
    a duplacted arguments error could occur:

        >>> config = parameterToConfiguration(IAnyConfiguration, u'a bla', d=u'd bla', c=u'c bla')
        >>> config.a, config.b, config.c, config.d
        (u'a bla', None, u'c bla', u'd bla')

        >>> parameterToConfiguration(IAnyConfiguration, u'd bla', a=u'd bla', c=u'c bla')
        Traceback (most recent call last):
        ...
        AttributeError: Duplicated arguments: a.

    G: Sometimes any parameters are allowed. This use case is indicated by a None key interface:

        >>> parameterToConfiguration(None) is None
        True

        >>> parameterToConfiguration(None, 'not allowed parameter')

    """
    # no arguments declared
    if __keyface__ is None:
#        if pos or kws:
#            raise AttributeError('No arguments allowed.')

        return None

    # assume that kws are ok
    if not pos:
        try:
            return createConfiguration(__keyface__, kws)

        except:
            pass

    # assume that first pos is already a configuration
    if len(pos) == 1 and not kws and __keyface__.providedBy(pos[0]):
        return pos[0]

    # pos and kws mixture
    attribution = namesInOrder(__keyface__)
    errors = []
    for i in range(len(pos)):
        key = attribution[i]
        value = pos[i]
        
        
        if key not in kws:
            kws[key] = value
        else:
            errors.append(key)

    if errors:
        raise AttributeError('Duplicated arguments: %s.' % ', '.join(errors))

    return createConfiguration(__keyface__, kws)
        