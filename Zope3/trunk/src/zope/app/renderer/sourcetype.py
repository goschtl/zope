##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Source Types Service

Allows us to register source types.

$Id: sourcetype.py,v 1.2 2003/07/31 18:48:38 srichter Exp $
"""
from zope.interface import implements
from zope.app.interfaces.renderer import IGlobalSourceTypeService

class GlobalSourceTypeService:
    __doc__ = IGlobalSourceTypeService.__doc__

    implements(IGlobalSourceTypeService)

    def __init__(self):
        self.__types = {}

    def provide(self, title, iface, klass):
        "See zope.app.interfaces.renderer.IGlobalSourceTypeService"
        self.__types[title] = (iface, klass)

    def get(self, title, default=None):
        "See zope.app.interfaces.renderer.IGlobalSourceTypeService"
        res = self.__types.get(title, default)
        if res is not default:
            res = res[0]
        return res

    def query(self, title):
        "See zope.app.interfaces.renderer.IGlobalSourceTypeService"
        return self.__types[title][0]

    def getAllTitles(self):
        "See zope.app.interfaces.renderer.IGlobalSourceTypeService"
        return self.__types.keys()

    def createObject(self, title, source):
        "See zope.app.interfaces.renderer.IGlobalSourceTypeService"
        klass = self.__types[title][1]
        return klass(source)

    _clear = __init__

SourceTypes = GlobalSourceTypeService()
clear = SourceTypes._clear
