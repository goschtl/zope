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
"""Objects that take care of annotating dublin core meta data times

$Id: DependencyChecker.py,v 1.3 2002/11/30 18:32:14 jim Exp $
"""
from Zope.ComponentArchitecture import queryAdapter
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.DependencyFramework.Exceptions import DependencyError
from Zope.Event.ISubscriber import ISubscriber
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class DependencyChecker:
    """Checking dependency  while deleting object
    """
    __implements__ = ISubscriber
    
    def __init__(self):
        pass

    def notify(self, event):
        object = removeAllProxies(event.object)
        dependency = queryAdapter(object, IDependable)
        if dependency is not None:
            if dependency.dependents():
                raise DependencyError(" Removal of object dependable")
                
CheckDependency = DependencyChecker() 
    
        
        
