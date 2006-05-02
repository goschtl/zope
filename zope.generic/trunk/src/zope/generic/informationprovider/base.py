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
from zope.annotation import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.app.container.contained import Contained
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import alsoProvides
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zope.generic.configuration import IConfigurations
from zope.generic.configuration.api import AttributeConfigurations
from zope.generic.directlyprovides.api import provides
from zope.generic.directlyprovides.api import updateDirectlyProvided
from zope.generic.directlyprovides.api import UpdateProvides

from zope.generic.informationprovider import IInformationProvider
from zope.generic.informationprovider import IGlobalInformationProvider
from zope.generic.informationprovider import IUserDescription
from zope.generic.informationprovider import ILocalInformationProvider



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

    implements(IInformationProvider)

    def __init__(self, __conface__=None, __keyface__=None):
        if __keyface__:
            self.__keyface__ = __keyface__
        
        if __conface__:
            self.__conface__ = __conface__
            updateDirectlyProvided(self, __conface__)
        
        # mark the key interface by the context
        alsoProvides(self.__keyface__, self.__conface__)

    provides('__conface__')

    __keyface__ = FieldProperty(IInformationProvider['__keyface__'])
    __conface__ = UpdateProvides(IInformationProvider['__conface__'])
    
    @property
    def keyface(self):
        return self.__keyface__

    @property
    def conface(self):
        return self.__conface__

    def __conform__(self, interface):

        if interface == IConfigurations:
            return AttributeConfigurations(self)

        elif interface == IAnnotations:
            return AttributeAnnotations(self)
            



class GlobalInformationProvider(BaseInformationProvider):
    """Global information provider."""

    implements(IGlobalInformationProvider)

    provides('__conface__')



class LocalInformationProvider(BaseInformationProvider, Contained, Persistent):
    """Local information provider."""

    implements(ILocalInformationProvider)

    provides('__conface__')



class UserDescription(object):
    """Key interface description mixin."""

    implements(IUserDescription)

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
