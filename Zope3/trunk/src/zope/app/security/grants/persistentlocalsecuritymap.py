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
""" Generic two-dimensional array type """

from persistence import Persistent
from persistence.dict import PersistentDict
from zope.app.interfaces.security.grants.localsecuritymap import ILocalSecurityMap
from zope.app.security.grants.localsecuritymap import LocalSecurityMap

class PersistentLocalSecurityMap(LocalSecurityMap, Persistent):

    __implements__ = ILocalSecurityMap

    def _clear(self):
        self._byrow = PersistentDict()
        self._bycol = PersistentDict()

    def _empty_mapping(self):
        return PersistentDict()
