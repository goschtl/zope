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

$Id: skin.py,v 1.4 2003/05/01 19:35:38 faassen Exp $
"""

from zope.interface.implementor import ImplementorRegistry
from zope.component.interfaces import ISkinService

class IGlobalSkinService(ISkinService):

    def defineSkin(name, view_type, layers):
        """Define a skin for a given view type as a sequence of layers

        There is a predefined skin, '', with a single layer, ''.
        """

_default = ('default',)

class GlobalSkinService:

    def __init__(self):
        self.__skins = {}

    __implements__ = IGlobalSkinService

    def defineSkin(self, name, view_type, layers):
        '''See interface IGlobalSkinService'''

        reg = self.__skins.get(name, None)
        if reg is None:
            reg = self.__skins[name] = ImplementorRegistry()

        reg.register(view_type, layers)

    def getSkin(self, object, name, view_type):
        '''See interface ISkinService'''

        reg = self.__skins.get(name, None)
        if reg is not None:
            layers = reg.get(view_type)
            if layers is not None:
                return layers

        # XXX Jim thinks that this should raise an exception instead.
        #     But that's A Project, because there are unit tests
        #     that insist on the current behavior.
        return _default

    _clear = __init__

skinService = GlobalSkinService()



_clear     = skinService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
