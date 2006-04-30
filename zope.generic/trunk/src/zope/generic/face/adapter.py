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

from zope.component import adapts
from zope.interface import implements
from zope.location import Location

from zope.generic.face import IAttributeFaced
from zope.generic.face import IFace
from zope.generic.face import INoConface
from zope.generic.face import INoKeyface



class FaceForAttributeFaced(Location):
    """Adapts IAttributeFaced to IFace.

    You can adapt IFace if you provide IAttributeFaced:

        >>> fake_keyface = object()
        >>> fake_conface = object()

        >>> class AnyAttributeFaced(object):
        ...    __keyface__ = fake_keyface
        ...    __conface__ = fake_conface

        >>> faced = AnyAttributeFaced()
        >>> face = FaceForAttributeFaced(faced)
        >>> face.keyface == fake_keyface
        True
        >>> face.conface == fake_conface
        True

        >>> class NoAttributeFaced(object):
        ...     pass

        >>> faced = NoAttributeFaced()
        >>> face = FaceForAttributeFaced(faced)
        >>> face.keyface is INoKeyface
        True
        >>> face.conface is INoConface
        True
    """

    implements(IFace)
    adapts(IAttributeFaced)

    def __init__(self, context):
        self.context = context

    @property
    def keyface(self):
        return getattr(self.context, '__keyface__', INoKeyface)

    @property
    def conface(self):
        return getattr(self.context, '__conface__', INoConface)
