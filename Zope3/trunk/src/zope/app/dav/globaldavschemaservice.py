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
$Id: globaldavschemaservice.py,v 1.1 2003/05/20 15:46:38 sidnei Exp $
"""

from zope.app.component.globalinterfaceservice import InterfaceService
from zope.app.interfaces.component import IGlobalDAVSchemaService

class DAVSchemaService(InterfaceService):
    __implements__ = IGlobalDAVSchemaService

davSchemaService = DAVSchemaService()
provideInterface = davSchemaService.provideInterface
getInterface = davSchemaService.getInterface
queryInterface = davSchemaService.queryInterface
searchInterface = davSchemaService.searchInterface

_clear = davSchemaService._clear

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
