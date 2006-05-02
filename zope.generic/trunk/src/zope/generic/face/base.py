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

from zope.interface import implements

from zope.generic.face import IFace
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface



class Face(object):
    """Face interface mixin for key- and conface attribute implementations.
    
    You can mixin this class if you like to provide IFace for
    IAttributeFaced implementations:

        >>> fake_keyface = object()
        >>> fake_conface = object()

        >>> class AnyAttributeFace(Face):
        ...    __keyface__ = fake_keyface
        ...    __conface__ = fake_conface

        >>> face = AnyAttributeFace()
        >>> face.__keyface__ == fake_keyface
        True
        >>> face.__conface__ == fake_conface
        True
        >>> face.keyface == fake_keyface
        True
        >>> face.conface == fake_conface
        True

        >>> class NoAttributeFaced(Face):
        ...     pass

        >>> face = NoAttributeFaced()
        >>> face.__keyface__ is IUndefinedKeyface
        Traceback (most recent call last):
        ...
        AttributeError: 'NoAttributeFaced' object has no attribute '__keyface__'
        >>> face.__conface__ is IUndefinedContext
        Traceback (most recent call last):
        ...
        AttributeError: 'NoAttributeFaced' object has no attribute '__conface__'
        >>> face.keyface is IUndefinedKeyface
        True
        >>> face.conface is IUndefinedContext
        True
    """

    implements(IFace)

    @property
    def keyface(self):
        return getattr(self, '__keyface__', IUndefinedKeyface)

    @property
    def conface(self):
        return getattr(self, '__conface__', IUndefinedContext)
