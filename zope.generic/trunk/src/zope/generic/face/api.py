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

from zope.generic.face import *
from zope.generic.face.adapter import FaceForAttributeFaced
from zope.generic.face.base import Face
from zope.generic.face.base import GlobalInformationProvider
from zope.generic.face.base import KeyfaceDescription
from zope.generic.face.base import LocalInformationProvider
from zope.generic.face.helper import toDescription
from zope.generic.face.helper import toDottedName
from zope.generic.face.helper import toInterface
from zope.generic.face.metaconfigure import ensureInformationProvider



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



def getNextInformationProvider(object=None, conface=None):
    """Evaluate the next information provider utility for an object or keyface."""
    
    if conface is None:
        conface = getConface(object, IUndefinedContext)
        
    keyface = getKeyface(object)

    try:
        return getUtility(conface, toDottedName(keyface))

    except:
        # try to evaluate a matching super key interface
        for more_general_keyface in keyface.__iro__:
            if IKeyfaceType.providedBy(more_general_keyface):
                try:
                    return getUtility(conface, toDottedName(more_general_keyface))

                except:
                    pass
        else:
            raise



def queryNextInformationProvider(object=None, conface=None, default=None):
    """Evaluate the next information provider utility for an object or keyface."""
    try:
        return getNextInformationProvider(object, conface)

    except:
        return default



def getNextInformationProvidersFor(provider, default=None):
    """Evaluate all information providers of a certain information aspect."""

    for name, information in getUtilitiesFor(provider):
        yield (toInterface(name), information)