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
"""factory service
"""


from zope.interface.verify import verifyObject
from zope.component.interfaces import IFactory
from zope.component.interfaces import IFactoryService
from zope.component.exceptions import ComponentLookupError

class IGlobalFactoryService(IFactoryService):

    def provideFactory(name, factory):
        """Provide a factory for the given name.
        """

class GlobalFactoryService:

    __implements__ = IGlobalFactoryService

    def __init__(self):
        self.__factories={}

    def provideFactory(self, name, factory):
        """See IGlobalFactoryService interface"""
        verifyObject(IFactory, factory)
        self.__factories[name] = factory

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

    _clear = __init__

# the global factory service instance (see component.zcml )
factoryService = GlobalFactoryService()
provideFactory = factoryService.provideFactory



_clear         = factoryService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
