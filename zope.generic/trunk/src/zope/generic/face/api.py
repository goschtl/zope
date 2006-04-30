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

from zope.generic.face import *
from zope.generic.face.adapter import FaceForAttributeFaced
from zope.generic.face.base import Face
from zope.generic.face.base import KeyfaceDescription
from zope.generic.face.helper import toDescription
from zope.generic.face.helper import toDottedName
from zope.generic.face.helper import toInterface
from zope.generic.face.metaconfigure import ensureInformationProvider



def getKeyface(object):
    """Return the key interface from an object."""

    # todo replace IInterface by IKeyfaceType
    if IInterface.providedBy(object):
        if not IKeyfaceType.providedBy(object):
            #print object
            pass
        
        return object

    if IAttributeFaced.providedBy(object):
        return getattr(object, '__keyface__', INoKeyface)

    return IFace(object).keyface



def queryKeyface(object, default=None):
    """Return the key interface from an object or default."""

    try:
        return getKeyface(object)

    except:
        return default



def getConface(object):
    """Return the context interface from an object."""

    if IConfaceType.providedBy(object):
        return object

    if IAttributeFaced.providedBy(object):
        return getattr(object, '__conface__', INoConface)

    return IFace(object).conface



def queryConface(object, default=None):
    """Return the context interface from an object or default."""

    try:
        return getConface(object)

    except:
        return default
