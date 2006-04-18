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

from zope.component.factory import Factory
from zope.component.interfaces import IFactory

from zope.generic.type import ITypeable
from zope.generic.type import ITyped
from zope.generic.type import IDirectlyTyped
from zope.generic.type import ITypeType
        


class TypeFactory(Factory):
    """Type factory implementation.

    Preset the type keyface for generic directly typed implementation 
    of its __init__ method.

    The type factory constructs directly typed objects of a given generic 
    implementation (class).

    First we declare a type marker:

        >>> from zope.interface import Interface

        >>> class IMyMarker(Interface):
        ...     pass

        >>> from zope.app.component.interface import provideInterface
        >>> provideInterface('', IMyMarker, ITypeType)

    Afterward we build a generic implementation implementing ITyped or a
    regular typeable class:

        >>> from zope.generic.type import IDirectlyTyped
        >>> from zope.generic.directlyprovides.api import provides
        >>> from zope.generic.directlyprovides.api import UpdateProvides
        >>> from zope.generic.directlyprovides.api import updateDirectlyProvided

        >>> class Object(object):
        ...     implements(IDirectlyTyped)
        ...
        ...     def __init__(self, __keyface__, **kws):
        ...         super(Object, self).__init__()
        ...         self.__dict__['__keyface__'] = __keyface__
        ...         updateDirectlyProvided(self, __keyface__)
        ...
        ...     provides('__keyface__')
        ...     __keyface__ = UpdateProvides(IDirectlyTyped['__keyface__'])
        ...     keyface = __keyface__

        >>> class Foo(object):
        ...    implements(ITypeable)

    Now we make a factory instance and check it:

        >>> myFactory = TypeFactory(Object, IMyMarker)

        >>> my = myFactory()
        >>> isinstance(my, Object)
        True
        >>> IMyMarker.providedBy(my)
        True

        >>> ITyped in myFactory.getInterfaces().flattened()
        False
        >>> IMyMarker in myFactory.getInterfaces().flattened()
        True

        >>> myFactory
        <TypeFactory for <class 'zope.generic.type.factory.Object'>>
        
    """

    implements(IFactory)

    def __init__(self, callable, __keyface__):
        # preconditions
        if not ITypeable.implementedBy(callable):
            raise ValueError('Callable must implement %s.' % ITypeable.__name__)

        if not ITypeType.providedBy(__keyface__):
            raise ValueError('Interface must provide %s.' % ITypeType.__name__)

        super(TypeFactory, self).__init__(callable, title='', description='', interfaces=(__keyface__,))

        # essentials
        self.__keyface__ = __keyface__

    def __call__(self, *pos, **kws):
        if IDirectlyTyped.implementedBy(self._callable):
            instance = self._callable(self.__keyface__, *pos, **kws)
        
        else:
            instance = self._callable(*pos, **kws)

        # TODO: query type information look for InitConfiguration and invoke the
        # handler if possible
        
        return instance

