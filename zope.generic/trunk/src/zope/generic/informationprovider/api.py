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
from zope.generic.informationprovider.helper import toConfigFaceTriple
from zope.generic.informationprovider.metaconfigure import ensureInformationProvider
from zope.generic.informationprovider.metaconfigure import getInformationProvider



def queryInformationProvider(keyface=IUndefinedKeyface, conface=IUndefinedContext, default=None):
    """Query the information provider for an faced object or face-typed interface."""
    try:
        return getInformationProvider(keyface, conface)

    except:
        return default



def acquireInformationProvider(keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Acquire the information provider for an faced object or face-typed interface."""

    if conface is None:
        conface = getConface(keyface)

    if not IKeyfaceType.providedBy(keyface):
        keyface = getKeyface(keyface)

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
    """Evaluate available information providers of a certain information aspect."""

    if IConfaceType.providedBy(face):
        for name, provider in getUtilitiesFor(face):
            yield (toInterface(name), provider)
    
    elif IKeyfaceType.providedBy(face):
        for conface in [conface for conface in directlyProvidedBy(face).flattened() if IConfaceType.providedBy(conface)]:
            yield (conface, getInformationProvider(face, conface))

    else:
        raise TypeError('KeyfaceType or ConfaceType required.', face)



def getInformation(informationkey, keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Evaluate an information by a keyface (string or key keyface)."""
    
    if IInformable.providedBy(keyface):
        context = keyface

    else:
        context = getInformationProvider(keyface, conface)
    
    if IConfigurationType.providedBy(informationkey):
        return informationkey(IConfigurations(context))

    else:
        return IAnnotations(context)[informationkey]



def queryInformation(informationkey, keyface=IUndefinedKeyface, conface=IUndefinedContext, default=None):
    """Evaluate an information by a keyface (string or key interface)."""
    try:
        return getInformation(informationkey, keyface, conface)

    except:
        return default



def acquireInformation(informationkey, keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Evaluate an information by a keyface (string or key keyface)."""
    
    if IInformable.providedBy(keyface):
        try:
            return getInformation(informationkey, keyface, conface)
        except:
            pass

    return getInformation(informationkey, getKeyface(keyface), conface)



def provideInformation(informationkey, information, keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Set an information to a context using a keyface (string or key interface)."""

    if IInformable.providedBy(keyface):
        context = keyface

    else:
        context = getInformationProvider(keyface, conface)

    if IConfigurationType.providedBy(informationkey):
        if type(information) is dict:
            information = ConfigurationData(informationkey, information)
    
        IConfigurations(context)[informationkey] = information

    else:
        IAnnotations(context)[informationkey] = information



def deleteInformation(informationkey, keyface, conface=IUndefinedContext):
    """Delete an information of a context using a keyface (string or key interface)."""

    if IInformable.providedBy(keyface):
        context = keyface

    else:
        context = getInformationProvider(keyface, conface)

    if IConfigurationType.providedBy(informationkey):
        del IConfigurations(context)[informationkey]
    
    else:
        del IAnnotations(context)[informationkey]
