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
$Id: Dependable.py,v 1.1 2002/10/14 11:51:05 jim Exp $
"""

__metaclass__ = type

from Persistence import Persistent
from Zope.App.DependencyFramework.IDependable import IDependable

class Dependable:
    __doc__ = IDependable.__doc__

    __implements__ =  IDependable

    def __init__(self):
        self.__dependents = {}

    def addDependent(self, location):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        self.__dependents[location] = 1
        self._p_changed = 1

    def removeDependent(self, location):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        del self.__dependents[location]
        self._p_changed = 1

    def dependents(self):
        "See Zope.App.DependencyFramework.IDependable.IDependable"
        return list(self.__dependents)
