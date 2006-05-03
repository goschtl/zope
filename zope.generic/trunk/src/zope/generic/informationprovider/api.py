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
from zope.interface import directlyProvidedBy

from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import ConfigurationData
from zope.generic.face import IConfaceType
from zope.generic.face import IKeyfaceType
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.generic.face.api import getConface
from zope.generic.face.api import getKeyface
from zope.generic.face.api import toDottedName
from zope.generic.face.api import toInterface

from zope.generic.informationprovider import *
from zope.generic.informationprovider.base import GlobalInformationProvider
from zope.generic.informationprovider.base import LocalInformationProvider
from zope.generic.informationprovider.base import UserDescription
from zope.generic.informationprovider.metaconfigure import ensureInformationProvider
from zope.generic.informationprovider.metaconfigure import getInformationProvider



def queryInformationProvider(object=None, conface=IUndefinedContext, default=None):
    """Evaluate the next information provider utility for an object or keyface."""
    try:
        return getInformationProvider(object, conface)

    except:
        return default



def acquireInformationProvider(object=None, conface=IUndefinedContext):
    """Evaluate the next information provider utility for an object or keyface."""
        
    keyface = getKeyface(object)
    if conface is None:
        conface = getConface(object)

    for more_general_conface in conface.__iro__:
        for more_general_keyface in keyface.__iro__:
            if IConfaceType.providedBy(more_general_conface) and IKeyfaceType.providedBy(more_general_keyface):
                #print '<Lookup %s at %s >' % (more_general_keyface.__name__, more_general_conface.__name__)
                try:
                    return getInformationProvider(more_general_keyface, more_general_conface)
                
                except:
                    pass

    raise KeyError('Missing information provider %s at %s.' % (keyface.__name__, conface.__name__))




def getInformationProvidersFor(face):
    """Evaluate all information providers of a certain information aspect."""

    if IConfaceType.providedBy(face):
        for name, provider in getUtilitiesFor(face):
            yield (toInterface(name), provider)
    
    elif IKeyfaceType.providedBy(face):
        for conface in [conface for conface in directlyProvidedBy(face).flattened() if IConfaceType.providedBy(conface)]:
            yield (conface, getInformationProvider(face, conface))

    else:
        raise TypeError('KeyfaceType or ConfaceType required.', face)




def getInformation(context, informationkey):
    """Evaluate an information by a keyface (string or key keyface)."""
    if IConfigurationType.providedBy(informationkey):
        return informationkey(IConfigurations(context))

    else:
        return IAnnotations(context)[informationkey]



def queryInformation(context, informationkey, default=None):
    """Evaluate an information by a keyface (string or key interface)."""
    try:
        return getInformation(context, informationkey)

    except:
        return default



def provideInformation(context, informationkey, information):
    """Set an information to a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(informationkey):
        if type(information) is dict:
            information = ConfigurationData(informationkey, information)
    
        IConfigurations(context)[informationkey] = information

    else:
        IAnnotations(context)[informationkey] = information



def deleteInformation(context, informationkey):
    """Delete an information of a context using a keyface (string or key interface)."""

    if IConfigurationType.providedBy(informationkey):
        del IConfigurations(context)[informationkey]
    
    else:
        del IAnnotations(context)[informationkey]
