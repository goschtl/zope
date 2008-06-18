##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Representations of simple objects.
"""

import inspect
from zope.interface import implements
from zope.introspector.interfaces import IObjectInfo

class ObjectInfo(object):
    implements(IObjectInfo)
    
    def __init__(self, obj):
        self.obj = obj

    def getType(self):
        return type(self.obj)

    def isModule(self):
        return inspect.ismodule(self.obj)

    def isClass(self):
        return inspect.isclass(self.obj)
