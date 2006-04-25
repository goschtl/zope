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

from zope.generic.keyface import *
from zope.generic.keyface.adapter import KeyfaceForAttributeKeyfaced
from zope.generic.keyface.base import Keyface
from zope.generic.keyface.base import KeyfaceDescription
from zope.generic.keyface.helper import toDescription
from zope.generic.keyface.helper import toDottedName
from zope.generic.keyface.helper import toKeyface



def getKeyface(object):
    """Evaluate the interface keyface from an object."""

    if IInterface.providedBy(object):
        keyface = object

    elif IKeyface.providedBy(object):
        keyface = object.keyface

    else:
        keyface = IKeyface(object).keyface

    return keyface



def queryKeyface(object, default=None):
    """Evaluate the keyface keyface from an object."""

    try:
        return getKeyface(object)

    except:
        return default
