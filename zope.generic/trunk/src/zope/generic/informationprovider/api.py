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

from zope.annotation import IAnnotations
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.generic.keyface.api import getKeyface
from zope.generic.keyface.api import queryKeyface
from zope.generic.keyface.api import toDottedName
from zope.generic.keyface.api import toKeyface

from zope.generic.configuration import IConfigurations
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration.api import ConfigurationData

from zope.generic.informationprovider import *
from zope.generic.informationprovider.base import InformationProvider



def getInformationProvider(object, provider=IInformationProviderInformation):
    """Evaluate an information provider for an object."""

    return getUtility(provider, toDottedName(getKeyface(object)))



def queryInformationProvider(object, provider=IInformationProviderInformation, default=None):
    """Evalute an information provider or return default."""
    try:
        return getInformationProvider(object, provider)

    except:
        return default



def getInformationProvidersFor(provider, default=None):
    """Evaluate all information providers of a certain information aspect."""

    for name, information in getUtilitiesFor(provider):
        yield (toKeyface(name), information)



def getInformation(context, keyface):
    """Evaluate an information by a keyface (string or key keyface)."""
    if IConfigurationType.providedBy(keyface):
        return keyface(IConfigurations(context))

    else:
        return IAnnotations(context)[keyface]



def queryInformation(context, keyface, default=None):
    """Evaluate an information by a keyface (string or key interface)."""
    try:
        return getInformation(context, keyface)

    except:
        return default



def provideInformation(context, keyface, information):
    """Set an information to a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(keyface):
        if type(information) is dict:
            information = ConfigurationData(keyface, information)
    
        IConfigurations(context)[keyface] = information

    else:
        IAnnotations(context)[keyface] = information



def deleteInformation(context, keyface):
    """Delete an information of a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(keyface):
        del IConfigurations(context)[keyface]
    
    else:
        del IAnnotations(context)[keyface]
