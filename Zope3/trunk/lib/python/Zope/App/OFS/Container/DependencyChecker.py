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

$Id: DependencyChecker.py,v 1.4 2002/12/12 11:32:29 mgedmin Exp $
"""
from Zope.ComponentArchitecture import queryAdapter
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.DependencyFramework.Exceptions import DependencyError
from Zope.Event.ISubscriber import ISubscriber
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.Traversing import getPhysicalPathString, locationAsUnicode

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
            dependents = dependency.dependents()
            if dependents:
                objectpath = getPhysicalPathString(event.object)
                dependents = map(locationAsUnicode, dependents)
                raise DependencyError("Removal of object (%s)"
                                      " which has dependents (%s)"
                                      % (objectpath,
                                         ", ".join(dependents)))

CheckDependency = DependencyChecker()
