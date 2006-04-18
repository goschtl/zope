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

from zope.dottedname.resolve import resolve



def toDottedName(component):
    if component is None:
        return 'None'
    return component.__module__ + '.' + component.__name__


# cache
__name_to_component = {}

def toKeyface(name):
    try:
        return __name_to_component[name]
    except KeyError:
        return __name_to_component.setdefault(name, resolve(name))



_marker = object()

def configuratonToDict(interface, configuration, all=False):
    """Extract values from configuration to a dictionary.

    First we have to specify a test configurtion interface:

        >>> from zope.interface import Interface
        >>> from zope.schema import TextLine
        
        >>> class IFooConfiguration(Interface):
        ...    fo = TextLine(title=u'Fo')
        ...    foo = TextLine(title=u'Foo', required=False)
        ...    fooo = TextLine(title=u'Fooo', required=False, readonly=True, default=u'fooo bla')

    Minimal data without defaults:

        >>> from zope.generic.component.base import ConfigurationData
        >>> configuration = ConfigurationData(IFooConfiguration, {'fo': 'fo bla'})
        >>> configuratonToDict(IFooConfiguration, configuration)
        {'fo': 'fo bla'}

    Including defaults:
        >>> configuratonToDict(IFooConfiguration, configuration, all=True)
        {'fooo': u'fooo bla', 'foo': None, 'fo': 'fo bla'}

    """
    data = {}
    for name in interface:
        value = getattr(configuration, name, _marker)
        field = interface[name]

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
