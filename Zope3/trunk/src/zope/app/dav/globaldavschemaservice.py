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
"""
$Id: globaldavschemaservice.py,v 1.4 2003/08/16 00:43:23 srichter Exp $
"""

from zope.component.exceptions import ComponentLookupError
from zope.app.component.globalinterfaceservice import InterfaceService
from zope.app.interfaces.component import IGlobalDAVSchemaService
from zope.interface import implements

class DAVSchemaService(InterfaceService):
    implements(IGlobalDAVSchemaService)

    def __init__(self, data=None):
        if data is None:
            data = {}
        backref = {}
        for k, v in data:
            backref[v] = k
        self.__backref = backref
        super(DAVSchemaService, self).__init__(data)

    def provideInterface(self, id, interface):
        if not id:
            id = "%s.%s" % (interface.__module__, interface.getName())
        self.__backref[interface] = id
        super(DAVSchemaService, self).provideInterface(id, interface)

    def availableNamespaces(self):
        return super(DAVSchemaService, self).searchInterfaceIds('')

    def getNamespace(self, interface):
        ns = self.__backref.get(interface, None)
        if ns is None:
            raise ComponentLookupError(interface)

    def queryNamespace(self, interface, default=None):
        return self.__backref.get(interface, default)

davSchemaService = DAVSchemaService()
provideInterface = davSchemaService.provideInterface
getInterface = davSchemaService.getInterface
queryInterface = davSchemaService.queryInterface
searchInterface = davSchemaService.searchInterface
availableNamespaces = davSchemaService.availableNamespaces
getNamespace = davSchemaService.getNamespace
queryNamespace = davSchemaService.queryNamespace

_clear = davSchemaService._clear

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
