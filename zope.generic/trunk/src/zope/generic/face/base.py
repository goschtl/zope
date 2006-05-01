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
from zope.schema.fieldproperty import FieldProperty

from zope.generic.directlyprovides.api import provides
from zope.generic.directlyprovides.api import updateDirectlyProvided
from zope.generic.directlyprovides.api import UpdateProvides

from zope.generic.face import IAttributeFaced
from zope.generic.face import IFace
from zope.generic.face import IGlobalInformationProvider
from zope.generic.face import IKeyfaceDescription
from zope.generic.face import ILocalInformationProvider
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



class BaseInformationProvider(object):
    """Information provider mixin.

    Information provider provide contextual information for key interfaces
    (keyface). The context is defined by a context interface (conface):

        >>> from zope.interface import alsoProvides
        >>> from zope.interface import Interface
        >>> from zope.generic.face import IConfaceType

        >>> class ISpecialContext(Interface):
        ...    pass

        >>> alsoProvides(ISpecialContext, IConfaceType)

    The key interface is defined by a marker interface too.

        >>> from zope.generic.face import IKeyfaceType

        >>> class IFoo(Interface):
        ...    pass

        >>> alsoProvides(IFoo, IKeyfaceType)

    During the registration of a information provider the key interface should
    be marked by the context interface:

        >>> alsoProvides(IFoo, ISpecialContext)

    This typing asserts that there will be an information provider registered
    as utility providing the context and named by the dotted name of the
    key interface.

        >>> provider = BaseInformationProvider(ISpecialContext, IFoo)

    The information provider will provide the context interface:

        >>> ISpecialContext.providedBy(provider)
        True

    The information provider is related to the key interface:

        >>> provider.keyface == IFoo
        True
        >>> provider.conface == ISpecialContext
        True

    """

    def __init__(self, __conface__=None, __keyface__=None):
        if __keyface__:
            self.__keyface__ = __keyface__
        
        if __conface__:
            self.__conface__ = __conface__
            updateDirectlyProvided(self, __conface__)

    provides('__conface__')

    __keyface__ = FieldProperty(IAttributeFaced['__keyface__'])
    __conface__ = UpdateProvides(IAttributeFaced['__conface__'])
    
    @property
    def keyface(self):
        return self.__keyface__

    @property
    def conface(self):
        return self.__conface__

    def __conform__(self, interface):
        raise NotImplementedErro('__conform__')


_global_information_hook = {}

class GlobalInformationProvider(BaseInformationProvider):
    """Global information provider."""

    implements(IGlobalInformationProvider)

    provides('__conface__')

    def __conform__(self, interface):
        try:
            return _global_information_hook[interface](self)

        except:
            return None


_local_information_hook = {}

class LocalInformationProvider(BaseInformationProvider, Contained, Persistent):
    """Local information provider."""

    implements(ILocalInformationProvider)

    provides('__conface__')

    def __conform__(self, interface):
        try:
            return _global_information_hook[interface](self)

        except:
            return None



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
