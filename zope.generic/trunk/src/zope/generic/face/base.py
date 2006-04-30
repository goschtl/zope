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

from persistent import Persistent
from zope.app.container.contained import Contained
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import implements

from zope.generic.directlyprovides.api import provides
from zope.generic.directlyprovides.api import updateDirectlyProvided
from zope.generic.directlyprovides.api import UpdateProvides

from zope.generic.face import IAttributeFaced
from zope.generic.face import IFace
from zope.generic.face import IGlobalInformationProvider
from zope.generic.face import IKeyfaceDescription
from zope.generic.face import ILocalInformationProvider
from zope.generic.face import INoConface
from zope.generic.face import INoKeyface



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
        >>> face.__keyface__ is INoKeyface
        Traceback (most recent call last):
        ...
        AttributeError: 'NoAttributeFaced' object has no attribute '__keyface__'
        >>> face.__conface__ is INoConface
        Traceback (most recent call last):
        ...
        AttributeError: 'NoAttributeFaced' object has no attribute '__conface__'
        >>> face.keyface is INoKeyface
        True
        >>> face.conface is INoConface
        True
    """

    implements(IFace)

    @property
    def keyface(self):
        return getattr(self, '__keyface__', INoKeyface)

    @property
    def conface(self):
        return getattr(self, '__conface__', INoConface)



class GlobalInformationProvider(object):
    """Global information provider."""

    implements(IGlobalInformationProvider)

    def __init__(self, __conface__=None, __keyface__=None):
        directlyprovided = []
        if __keyface__:
            self.__keyface__ = __keyface__
            directlyprovided.append(__keyface__)
        
        if __conface__:
            self.__conface__ = __conface__
            directlyprovided.append(__conface__)

        if directlyprovided:
            updateDirectlyProvided(self, directlyprovided)

    provides('__keyface__', '__conface__')

    __keyface__ = UpdateProvides(IAttributeFaced['__keyface__'])
    __conface__ = UpdateProvides(IAttributeFaced['__conface__'])
    
    @property
    def keyface(self):
        return self.__keyface__

    @property
    def conface(self):
        return self.__conface__



class LocalInformationProvider(Contained, Persistent):
    """Local information provider."""

    implements(ILocalInformationProvider)

    def __init__(self, __conface__=None, __keyface__=None):
        directlyprovided = []
        if __keyface__:
            self.__keyface__ = __keyface__
            directlyprovided.append(__keyface__)
        
        if __conface__:
            self.__conface__ = __conface__
            directlyprovided.append(__conface__)

        if directlyprovided:
            updateDirectlyProvided(self, directlyprovided)

    provides('__keyface__', '__conface__')

    __keyface__ = UpdateProvides(IAttributeFaced['__keyface__'])
    __conface__ = UpdateProvides(IAttributeFaced['__conface__'])
    
    @property
    def keyface(self):
        return self.__keyface__

    @property
    def conface(self):
        return self.__conface__



class KeyfaceDescription(Face):
    """Key interface description mixin."""

    implements(IKeyfaceDescription)

    def __init__(self, keyface, label=None, hint=None):
        self.__keyface__ = keyface

        if label is None:
            self.label = _(keyface.__name__)
        else:
            self.label = label

        if hint is None:
            self.hint = _(keyface.__doc__)
        else:
            self.hint = hint
