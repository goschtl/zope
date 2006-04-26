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


from zope.generic.keyface import IKeyface

from zope.generic.configuration.base import ConfigurationData



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

        >>> from zope.generic.configuration.base import ConfigurationData
        >>> configuration = ConfigurationData(IAnyConfiguration, {'a': 'a bla'})
        >>> configuratonToDict(configuration)
        {'a': 'a bla'}

    Including defaults:
        >>> configuratonToDict(configuration, all=True)
        {'a': 'a bla', 'c': u'c default', 'b': None}

    """
    data = {}
    keyface = IKeyface(configuration).keyface

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

        >>> requiredInOrder(IAnyConfiguration)
        ['a', 'd']
    
    """
    
    return [name for name in configuration if configuration[name].required is True]



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
            return ConfigurationData(__keyface__, kws)

        except:
            pass

    # assume that first pos is already a configuration
    if len(pos) == 1 and not kws and __keyface__.providedBy(pos[0]):
        return pos[0]

    # pos and kws mixture
    attribution = requiredInOrder(__keyface__)
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

    return ConfigurationData(__keyface__, kws)
        