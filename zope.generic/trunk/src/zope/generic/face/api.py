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
from zope.generic.face.helper import toDescription
from zope.generic.face.helper import toDottedName
from zope.generic.face.helper import toFaceTuple
from zope.generic.face.helper import toInterface



def getKeyface(object, default=IUndefinedKeyface):
    """Return the key interface from an object."""

    if object is None:
        return default

    if IKeyfaceType.providedBy(object):
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
