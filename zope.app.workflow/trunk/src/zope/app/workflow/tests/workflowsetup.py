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
from zope.component import getGlobalSiteManager
from zope.interface import implements
from zope.traversing.api import traverse

from zope.app.security.principalregistry import principalRegistry
from zope.app.component.testing import PlacefulSetup
from zope.app.testing import setup


class WorkflowSetup(PlacefulSetup):

    def setUp(self):
        self.root_sm = getGlobalSiteManager()

        self.sm = PlacefulSetup.setUp(self, site=True)
        self.default = traverse(self.sm, "default")

