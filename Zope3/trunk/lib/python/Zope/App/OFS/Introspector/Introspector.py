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
from Interface import Interface
from Interface.Implements import implements, getImplements
from IIntrospector import IIntrospector

class Introspector:
    def __init__(self, component):
        self._component=component.__class__
        
    def getName(self):
        return self._component.__name__
        
    def getDocString(self):
        return self._component.__doc__
    
    def getInterfaces(self):
        imple=self._component.__implements__
        if type(imple) != tuple:
            imple=(imple,)
        else:
            imple=self._unpackTuple(imple)
        return imple
    
    def getInterfaceNames(self):
        names=[]
        for intObj in self.getInterfaces():
            names.append(intObj.__module__ + '.' + intObj.__name__)
        names.sort()
        return names
        
    def _unpackTuple(self, imple):
        res=[]
        for imp in imple:
            if type(imp)==tuple:
                res.extend(self._unpackTuple(imp))
            else: res.append(imp)
        return tuple(res)
    
    
implements(Introspector, IIntrospector)