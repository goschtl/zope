##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Global Factory Service

$Id: factory.py,v 1.8 2004/03/05 22:09:25 jim Exp $
"""
from zope.interface.verify import verifyObject
from zope.interface import implements
from zope.component.interfaces import IFactory
from zope.component.interfaces import IFactoryInfo
from zope.component.interfaces import IFactoryService
from zope.component.exceptions import ComponentLookupError

class IGlobalFactoryService(IFactoryService):

    def provideFactory(name, factory, info=None):
        """Provide a factory for the given name.

        If specified, info must implement IFactoryInfo.
        """

class FactoryInfo:

    implements(IFactoryInfo)

    def __init__(self, title, description):
        self.title = title
        self.description = description

class GlobalFactoryService:

    implements(IGlobalFactoryService)

    def __init__(self):
        self.__factories = {}
        self.__info = {}

    def provideFactory(self, name, factory, info=None):
        """See IGlobalFactoryService interface"""
        # XXX At this point the verify object code does not support variable
        # arguments well. For example, I was not able to register any factory
        # that requires constructor arguments! (SR) 
        # verifyObject(IFactory, factory)
        assert IFactory.providedBy(factory)
        self.__factories[name] = factory
        if info is not None:
            self.__info[name] = info

    def createObject(self, name, *args, **kwargs):
        """See IFactoryService interface"""
        try:
            return self.__factories[name](*args, **kwargs)
        except KeyError:
            raise ComponentLookupError(name)

    def getFactory(self, name):
        """See IFactoryService interface"""
        try:
            return self.__factories[name]
        except KeyError:
            raise ComponentLookupError(name)

    def queryFactory(self, name, default=None):
        """See IFactoryService interface"""
        return self.__factories.get(name, default)

    def getInterfaces(self, name):
        """See IFactoryService interface"""
        try: return self.__factories[name].getInterfaces()
        except KeyError:
            raise ComponentLookupError(name)

    def getFactoriesFor(self, iface):
        """See IFactoryService interface"""
        factories = self.queryFactoriesFor(iface, None)
        if factories is None:
            raise ComponentLookupError(iface)
        return factories

    def queryFactoriesFor(self, iface, default=None):
        """See IFactoryService interface"""
        return [(n, f) for n, f in self.__factories.items() \
                if iface in tuple(f.getInterfaces())] or default

    def getFactoryInfo(self, name):
        return self.__info.get(name)

    _clear = __init__

# the global factory service instance (see component.zcml )
factoryService = GlobalFactoryService()
provideFactory = factoryService.provideFactory

_clear = factoryService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
