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

$Id: package.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""
__metaclass__ = type


from zope.app.container.btree import BTreeContainer
from zope.proxy.context import ContextMethod
from zope.proxy.context import ContextWrapper
from zope.app.traversing import getPhysicalPathString
from zope.app.component.nextservice import getNextServiceManager
from zope.app.interfaces.services.service \
     import IServiceManager
from zope.app.interfaces.services.service \
     import IComponentManager

from zope.app.interfaces.services.package import IPackages
from zope.app.interfaces.services.package import IPackage


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




"""XXX short summary goes here.

XXX longer description goes here.

$Id: package.py,v 1.2 2002/12/25 14:13:19 jim Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer

from zope.app.interfaces.services.package import IPackage
from zope.app.services.configurationmanager import ConfigurationManager


class Package(BTreeContainer):
    __implements__ = IPackage

    def __init__(self):
        super(Package, self).__init__()
        self.setObject('configure', ConfigurationManager())
