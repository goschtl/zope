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
"""Setup for Placeful Worfklow Tests

$Id: workflowsetup.py,v 1.8 2004/03/03 20:20:36 srichter Exp $
"""
from zope.interface import implements
from zope.component.interfaces import IUtilityService

from zope.app import zapi
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.security import \
     IAuthenticationService, IPermissionService
from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.services.servicenames import \
     Permissions, Authentication, Workflows, Utilities
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.utility import LocalUtilityService
from zope.app.tests import setup
from zope.app.workflow.service import WorkflowService


class WorkflowServiceForTests(WorkflowService):
    implements(IAttributeAnnotatable)


class WorkflowSetup(PlacefulSetup):

    def setUp(self):
        self.root_sm = zapi.getServiceManager(None)

        self.sm = PlacefulSetup.setUp(self, site=True)
        setup.addService(self.sm, Utilities, LocalUtilityService())
        self.service = setup.addService(self.sm, Workflows,
                                        WorkflowServiceForTests())
        self.default = zapi.traverse(self.sm, "default")
        self.cm = self.default.getRegistrationManager()

        self.sm1 = self.makeSite('folder1')
        setup.addService(self.sm1, Utilities, LocalUtilityService())
        self.service1 = setup.addService(self.sm1, Workflows,
                                         WorkflowServiceForTests())
        self.default1 = zapi.traverse(self.sm1, "default")
        self.cm1 = self.default1.getRegistrationManager()


    def setupAuthService(self):
        self.root_sm.defineService(Authentication, IAuthenticationService)
        self.root_sm.provideService(Authentication, principalRegistry)
        return zapi.getService(self.rootFolder, Authentication)

    def setupPermissionService(self):
        self.root_sm.defineService(Permissions, IPermissionService)
        self.root_sm.provideService(Permissions, permissionRegistry)
        return zapi.getService(self.rootFolder, Permissions)

