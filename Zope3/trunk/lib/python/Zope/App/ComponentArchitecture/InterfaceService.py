##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: InterfaceService.py,v 1.2 2002/11/19 23:15:14 jim Exp $
"""
from IGlobalInterfaceService import IGlobalInterfaceService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
import string


class InterfaceService:
    __implements__ = IGlobalInterfaceService

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.__data = data
    
    def getInterface(self, id):
        if id in self.__data:
            return self.__data[id][0]
        else:
            raise ComponentLookupError

    def queryInterface(self, id, default=None):
        if self.__data.has_key(id):
            return self.__data[id][0]
        else:
            return default

    def searchInterface(self, search_string):
        search_result = []

        for id in self.__data.keys():
            if search_string:
                if string.find(string.lower(self.__data[id][1]),
                               string.lower(search_string)
                               ) >= 0:
                    search_result.append(self.__data[id][0])
            else:
                search_result.append(self.__data[id][0])

        return search_result

    def searchInterfaceIds(self, search_string):
        search_result = []

        for id in self.__data.keys():
            if search_string:
                if string.find(string.lower(self.__data[id][1]),
                               string.lower(search_string)
                               ) >= 0:
                    search_result.append(id)
            else:
                search_result.append(id)

        return search_result
    
    def _getAllDocs(self,interface):
        docs = str(interface.__name__)+'\n'+str(interface.__doc__)
        for name in interface.names():
            docs = docs + '\n' + str(interface.getDescriptionFor(name).__doc__)
        return docs
    
    def provideInterface(self, id, interface):
        self.__data[id]=(interface, self._getAllDocs(interface))
    
    _clear = __init__ 



interfaceService = InterfaceService()
provideInterface = interfaceService.provideInterface
getInterface = interfaceService.getInterface
queryInterface = interfaceService.queryInterface
searchInterface = interfaceService.searchInterface

_clear = interfaceService._clear

from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp
