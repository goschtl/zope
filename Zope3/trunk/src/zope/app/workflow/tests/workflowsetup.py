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

$Id: workflowsetup.py,v 1.13 2004/03/13 23:55:32 srichter Exp $
"""
from zope.interface import implements
from zope.component.interfaces import IUtilityService

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.security.interfaces import IAuthenticationService
from zope.app.security.principalregistry import principalRegistry
from zope.app.servicenames import Authentication, Workflows, Utilities
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.utility import LocalUtilityService
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
