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

Revision information:
$Id: Role.py,v 1.2 2002/06/10 23:28:11 jim Exp $
"""

from Zope.App.Security.IRole import IRole
from Zope.ComponentArchitecture.IFactory import IFactory
from Zope.App.Security.RegisteredObject import RegisteredObject
from Persistence import Persistent

class Role(RegisteredObject, Persistent):
    __implements__ = IRole
    __class_implements__ = IFactory

    def __init__(self):
        super(Role, self).__init__('', '', '')
    
    def setId(self, id):
        self._id = id
        
    def getInterfaces(self):
        return self.__implements__


