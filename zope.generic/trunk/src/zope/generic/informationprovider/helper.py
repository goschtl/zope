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

from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.generic.face.api import toFaceTuple
from zope.generic.face.api import toInterface




def toConfigFaceTriple(identifier):
    """Split configface:keyface@conface to (configface, keyface, conface).

        >>> from zope.interface import Interface
        
        >>> class IA(Interface):
        ...     pass

        >>> from zope.generic.face.api import toDottedName

        >>> api.toConfigFaceTriple(toDottedName(IA) + ':')
        (<InterfaceClass example.IA>, <....IUndefinedKeyface>, <....IUndefinedContext>)
    """

    parts = identifier.split(':')

    if len(parts) == 1:
        return (toInterface(parts[0]), IUndefinedKeyface, IUndefinedContext)

    else:
        keyface, conface = toFaceTuple(parts[1])
        return (toInterface(parts[0]), keyface, conface)
            
        
