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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: Packages.py,v 1.5 2002/11/30 18:40:57 jim Exp $
"""
__metaclass__ = type


from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.App.Traversing import getPhysicalPathString
from Zope.App.ComponentArchitecture.NextService import getNextServiceManager
from Zope.App.OFS.Services.ServiceManager.IServiceManager \
     import IServiceManager
from Zope.App.OFS.Services.ServiceManager.IComponentManager \
     import IComponentManager

from IPackages import IPackages
from IPackage import IPackage
from Package import Package

class Packages(BTreeContainer):
    __implements__ = IPackages

    def __init__(self):
        super(Packages, self).__init__()
        self.setObject('default', Package())

    def queryComponent(self, type=None, filter=None, all=0):

        local = []
        path = getPhysicalPathString(self)
        for package_name in self:
            package = ContextWrapper(self[package_name], self,
                                     name=package_name)
            for name in package:
                component = package[name]
                if type is not None and not type.isImplementedBy(component):
                    continue
                if filter is not None and not filter(component):
                    continue
                local.append({'path': "%s/%s/%s" % (path, package_name, name),
                              'component': ContextWrapper(component, package,
                                                          name=name),
                              })

        if all:
            next_service_manager = getNextServiceManager(self)
            if IComponentManager.isImplementedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    queryComponent = ContextMethod(queryComponent)

    def setObject(self, name, object):
        if not IPackage.isImplementedBy(object):
            raise TypeError("Can only add packages")
        return super(Packages, self).setObject(name, object)
    

