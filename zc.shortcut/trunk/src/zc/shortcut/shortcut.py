##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""shortcut class

$Id$
"""
import persistent
from zope import interface
from zope.location.interfaces import ILocation

from zc.shortcut import interfaces, proxy

class Shortcut(persistent.Persistent):
    interface.implements(interfaces.IShortcut, ILocation)

    def __init__(self, target):
        self.__parent__ = None
        self.__name__ = None
        self.raw_target = target

    @property
    def target(self):
        target = self.raw_target
        return proxy.TargetProxy(target, self.__parent__, self.__name__, self)
