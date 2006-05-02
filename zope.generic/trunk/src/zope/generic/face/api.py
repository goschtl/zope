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

from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import directlyProvidedBy

from zope.generic.face import *
from zope.generic.face.adapter import FaceForAttributeFaced
from zope.generic.face.base import Face
from zope.generic.face.helper import toDescription
from zope.generic.face.helper import toDottedName
from zope.generic.face.helper import toInterface



def getKeyface(object, default=IUndefinedKeyface):
    """Return the key interface from an object."""

    if object is None:
        return default

    # todo replace IInterface by IKeyfaceType
    if IInterface.providedBy(object):
        if not IKeyfaceType.providedBy(object):
            #print object
            pass
        
        return object

    if IAttributeFaced.providedBy(object):
        return getattr(object, '__keyface__', IUndefinedKeyface)

    try:
        return IFace(object).keyface

    except TypeError:
        return default



def getConface(object, default=IUndefinedContext):
    """Return the context interface from an object."""
    
    if object is None:
        return default

    if IConfaceType.providedBy(object):
        return object

    if IAttributeFaced.providedBy(object):
        return getattr(object, '__conface__', IUndefinedContext)

    try:
        return IFace(object).conface

    except TypeError:
        return default



def getInformationProvider(object=None, conface=IUndefinedContext):
    """Evaluate the next information provider utility for an object or keyface."""

    keyface = getKeyface(object)

    try:
        provider = getUtility(conface, toDottedName(keyface))
        # return only provider that is or extends a certain context.
        if provider.conface == conface:
            return provider
    except:
        pass

    raise KeyError('Missing information provider %s at %s.' % (keyface.__name__, conface.__name__))



def queryInformationProvider(object=None, conface=IUndefinedContext, default=None):
    """Evaluate the next information provider utility for an object or keyface."""
    try:
        return getInformationProvider(object, conface)

    except:
        return default



def acquireInformationProvider(object=None, conface=IUndefinedContext):
    """Evaluate the next information provider utility for an object or keyface."""
        
    keyface = getKeyface(object)

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
