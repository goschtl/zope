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
"""A package contains components and component configurations.

$Id: folder.py,v 1.1 2003/03/23 16:45:44 jim Exp $
"""

__metaclass__ = type

from zope.app.component.nextservice import getNextServiceManager
from zope.app.container.btree import BTreeContainer
from zope.app.interfaces.services.folder import ISiteManagementFolders
from zope.app.interfaces.services.folder import ISiteManagementFolder
from zope.app.interfaces.services.service import IComponentManager
from zope.app.interfaces.services.service import IServiceManager
from zope.app.services.configuration import ConfigurationManager
from zope.app.traversing import getPath
from zope.proxy.context import ContextMethod, ContextWrapper

class SiteManagementFolder(BTreeContainer):
    __implements__ = ISiteManagementFolder

    def __init__(self):
        super(SiteManagementFolder, self).__init__()
        self.setObject('configure', ConfigurationManager())

class SiteManagementFolders(BTreeContainer):
    __implements__ = ISiteManagementFolders

    def __init__(self):
        super(SiteManagementFolders, self).__init__()
        self.setObject('default', SiteManagementFolder())

    def queryComponent(self, type=None, filter=None, all=0):
        local = []
        path = getPath(self)
        for pkg_name in self:
            package = ContextWrapper(self[pkg_name], self, name=pkg_name)
            for name in package:
                component = package[name]
                if type is not None and not type.isImplementedBy(component):
                    continue
                if filter is not None and not filter(component):
                    continue
                wrapper =  ContextWrapper(component, package, name=name)
                local.append({'path': "%s/%s/%s" % (path, pkg_name, name),
                              'component': wrapper,
                              })

        if all:
            next_service_manager = getNextServiceManager(self)
            if IComponentManager.isImplementedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    queryComponent = ContextMethod(queryComponent)

    def setObject(self, name, obj):
        if not ISiteManagementFolder.isImplementedBy(obj):
            raise TypeError("Can only add packages")
        return super(SiteManagementFolders, self).setObject(name, obj)

# XXX Backward compatability. This is needed to support old pickles.
Package = SiteManagementFolder
Packages = SiteManagementFolders
import sys
sys.modules['zope.app.services.package'
            ] = sys.modules['zope.app.services.folder']
