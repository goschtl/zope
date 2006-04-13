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

from zope.app.annotation import IAnnotations
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface.interfaces import IInterface

from zope.generic.component import *
from zope.generic.component.base import ConfigurationData
from zope.generic.component.base import InformationProvider
from zope.generic.component.base import KeyInterface
from zope.generic.component.base import KeyInterfaceDescription
from zope.generic.component.helper import configuratonToDict
from zope.generic.component.helper import toDottedName
from zope.generic.component.helper import toKeyInterface



def getKey(object):
    """Evaluate the interface key from an object."""

    if IInterface.providedBy(object):
        interface = object

    elif IKeyInterface.providedBy(object):
        interface = object.interface

    else:
        interface = IKeyInterface(object).interface

    return interface



def queryKey(object, default=None):
    """Evaluate the interface key from an object."""

    try:
        return getKey(object)

    except:
        return default



def getInformationProvider(object, provider=IInformationProviderInformation):
    """Evaluate an information provider for an object."""

    return getUtility(provider, toDottedName(getKey(object)))



def queryInformationProvider(object, provider=IInformationProviderInformation, default=None):
    """Evalute an information provider or return default."""
    try:
        return getInformationProvider(object, provider)

    except:
        return default



def getInformationProvidersFor(provider, default=None):
    """Evaluate all information providers of a certain information aspect."""

    for name, information in getUtilitiesFor(provider):
        yield (toKeyInterface(name), information)



def getInformation(context, key):
    """Evaluate an information by a key (string or key interface)."""
    if IConfigurationType.providedBy(key):
        return key(IConfigurations(context))

    else:
        return IAnnotations(context)[key]



def queryInformation(context, key, default=None):
    """Evaluate an information by a key (string or key interface)."""
    try:
        return getInformation(context, key)

    except:
        return default



def provideInformation(context, key, information):
    """Set an information to a context using a key (string or key interface)."""

    if IConfigurationType.providedBy(key):
        if type(information) is dict:
            information = ConfigurationData(key, information)
    
        IConfigurations(context)[key] = information

    else:
        IAnnotations(context)[key] = information



def deleteInformation(context, key):
    """Delete an information of a context using a key (string or key interface)."""

    if IConfigurationType.providedBy(key):
        del IConfigurations(context)[key]
    
    else:
        del IAnnotations(context)[key]
