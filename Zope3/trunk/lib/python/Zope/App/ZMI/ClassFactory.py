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
""" ZMI Addable Registration

$Id: ClassFactory.py,v 1.2 2002/06/10 23:28:18 jim Exp $
"""

from Zope.ComponentArchitecture.IFactory import IFactory

class ClassFactory:
    
    __implements__ = IFactory

    def __init__(self, _class):
        self._class = _class

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)
    
    def getInterfaces(self):
        return getattr(self._class, '__implements__', None)