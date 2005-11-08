 ##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for Placeful Worfklow Tests

$Id$
"""
from zope.app import zapi
from zope.app.component.testing import PlacefulSetup
from zope.app.testing import setup
from zope.app.utility import LocalUtilityService


class WorkflowSetup(PlacefulSetup):

    def setUp(self):
        self.root_sm = zapi.getSiteManager()

        self.sm = PlacefulSetup.setUp(self, site=True)

        self.default = zapi.traverse(self.sm, "default")
        self.cm = self.default.registrationManager

        self.sm1 = self.makeSite('folder1')

        self.default1 = zapi.traverse(self.sm1, "default")
        self.cm1 = self.default1.registrationManager
