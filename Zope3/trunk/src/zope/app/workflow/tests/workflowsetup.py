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
Setup for Placeful Worfklow Tests
Revision information:
$Id: workflowsetup.py,v 1.1 2003/05/08 17:27:20 jack-e Exp $
"""
from zope.app.traversing import traverse, getPath
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceConfiguration

from zope.component import getService, getServiceManager
from zope.app.services.servicenames import Roles, Permissions, Adapters
from zope.app.services.servicenames import Authentication, Workflows

from zope.app.interfaces.security import IAuthenticationService
from zope.app.interfaces.security import IRoleService
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.principalregistry \
     import principalRegistry
from zope.app.security.registries.permissionregistry \
     import permissionRegistry

from zope.app.interfaces.dependable import IDependable
from zope.app.services.tests.placefulsetup \
     import PlacefulSetup
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.dependable import IDependable
from zope.app.dependable import Dependable
from zope.app.interfaces.services.configuration \
     import IUseConfiguration, IUseConfigurable
from zope.app.services.configuration import UseConfiguration
from zope.component.adapter import provideAdapter

from zope.app.interfaces.services.configuration \
     import Active, Unregistered, Registered

from zope.app.workflow.service import WorkflowService




class WorkflowServiceForTests(WorkflowService):

    __implements__ = WorkflowService.__implements__, IAttributeAnnotatable




class WorkflowSetup(PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)

        self.root_sm = getServiceManager(None)

        provideAdapter(IAttributeAnnotatable,
                       IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IDependable, Dependable)
        provideAdapter(IUseConfigurable, IUseConfiguration, UseConfiguration)
        
        # Set up a local workflow service
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())

        service_name = 'workflow_srv'
        self.sm = traverse(self.rootFolder, '++etc++site')
        self.default = default = traverse(self.sm, 'default')
        default.setObject(service_name, WorkflowServiceForTests())

        # XXX change to unique names 
        self.service = traverse(default, service_name)
        path = "%s/%s" % (getPath(default), service_name)
        configuration = ServiceConfiguration(Workflows, path, self.rootFolder)
        self.cm = default.getConfigurationManager()
        self.cm.setObject('', configuration)
        traverse(self.cm, '1').status = Active

        # Set up a more local workflow service
        folder1 = traverse(self.rootFolder, 'folder1')
        folder1.setServiceManager(ServiceManager())

        service_name1 = 'workflow_srv1'
        self.sm1 = traverse(folder1, '++etc++site')
        self.default1 = default1 = traverse(self.sm1, 'default')
        default1.setObject(service_name1, WorkflowServiceForTests())

        # XXX change to unique name
        self.service1 = traverse(self.default1, service_name1)
        path1 = "%s/%s" % (getPath(default1), service_name1)
        configuration1 = ServiceConfiguration(Workflows, path1, self.rootFolder)
        self.cm1 = default1.getConfigurationManager()
        self.cm1.setObject('', configuration1)
        traverse(self.cm1, '1').status = Active


    def setupAuthService(self):
        self.root_sm.defineService(Authentication, IAuthenticationService)
        self.root_sm.provideService(Authentication, principalRegistry)
        return getService(self.rootFolder, Authentication)


    def setupRoleService(self):
        self.root_sm.defineService(Roles, IRoleService)
        self.root_sm.provideService(Roles, roleRegistry)
        return getService(self.rootFolder, Roles)

    def setupPermissionService(self):
        self.root_sm.defineService(Permissions, IPermissionService)
        self.root_sm.provideService(Permissions, permissionRegistry)
        return getService(self.rootFolder, Permissions)

        

