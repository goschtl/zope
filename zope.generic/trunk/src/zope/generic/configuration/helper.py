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


from zope.component import getUtility

from zope.generic.component.api import toDottedName

from zope.generic.configuration import IConfigurationHandlerConfiguration
from zope.generic.configuration import IConfigurationHandlerInformation
from zope.generic.configuration import IConfigurationInformation
from zope.generic.configuration import IConfigurations



def getConfigurationInformation(interface):
    return getInformation(interface, IConfigurationInformation)



def queryConfigurationInformation(interface, default=None):
    # cyclic import :(
    from zope.generic.information.api import queryInformation
    
    return queryInformation(interface, IConfigurationInformation, default)



def queryConfigurationData(context, interface, default=None):
    """Evaluate corresponding configuration data satisfying the interface."""

    configurations = IConfigurations(context, default)

    if configurations is default:
        return default

    else:
        return interface(configurations, default)



def provideConfigurationData(context, interface, data):
    """Set configuration data into the context."""
    from zope.generic.configuration.base import ConfigurationData 
    if type(data) is dict:
        data = ConfigurationData(interface, data)

    configurations = IConfigurations(context)
    configurations[interface] = data



def deleteConfigurationData(context, interface):
    """Delete configuration from context."""
    
    configurations = IConfigurations(context, None)
    if configurations:
        del configurations[interface]



def queryConfigurationHandler(interface, default=None):
    # cyclic import :(
    from zope.generic.information.api import queryInformation
    
    info = queryInformation(interface, IConfigurationHandlerInformation, None)
    
    if info is None:
        return default
    
    configuration = queryConfigurationData(info, IConfigurationHandlerConfiguration)
    
    if configuration is None:
        return default

    else:
        return configuration.handler



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

        >>> from zope.generic.configuration.base import ConfigurationData
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
        