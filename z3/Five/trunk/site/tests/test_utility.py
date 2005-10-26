##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test local sites

$Id$
"""
import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase

from zope.interface import directlyProvides
from zope.component import getService, getServices
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Utilities
from zope.app.tests.placelesssetup import setUp, tearDown

import Products.Five
from Products.Five import zcml
from Products.Five.site.localsite import enableLocalSiteHook
from Products.Five.site.tests.dummy import manage_addDummySite, \
     IDummyUtility, ISuperDummyUtility, DummyUtility

class LocalUtilityServiceTest(ZopeTestCase.FunctionalTestCase):

    def afterSetUp(self):
        setUp()
        zcml.load_config("meta.zcml", Products.Five)
        zcml.load_config("permissions.zcml", Products.Five)
        zcml.load_config("configure.zcml", Products.Five.site)
        zcml_text = """\
        <five:localsite
            xmlns:five="http://namespaces.zope.org/five"
            class="Products.Five.site.tests.dummy.DummySite" />"""
        zcml.load_string(zcml_text)
        manage_addDummySite(self.folder, 'site')
        self.site = self.folder.site
        enableLocalSiteHook(self.site)
        self.path = '/'.join(self.site.getPhysicalPath())
        # Traverse to the site so that the local-thread site gets
        # setup correctly.
        self.publish(self.path)

    def beforeTearDown(self):
        from zope.app.component.localservice import clearSite
        clearSite()
        tearDown()

    def test_getServicesHook(self):
        from Products.Five.site.localsite import FiveSiteManager
        local_sm = getServices(None)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

        local_sm = getServices(self.site)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

    def test_getUtilityService(self):
        from Products.Five.site.utility import SimpleLocalUtilityService
        utils = getService(Utilities)
        self.failUnless(isinstance(utils, SimpleLocalUtilityService))

    def test_getUtilitiesNoUtilitiesFolder(self):
        utils = getService(Utilities)
        self.assertRaises(ComponentLookupError, utils.getUtility, IDummyUtility)
        self.assertEquals(list(utils.getUtilitiesFor(IDummyUtility)), [])
        self.assertEquals(list(utils.getAllUtilitiesRegisteredFor(IDummyUtility)), [])

    def test_registerUtility(self):
        utils = getService(Utilities)
        dummy = DummyUtility()
        utils.registerUtility(IDummyUtility, dummy, 'dummy')

        self.assertEquals(utils.getUtility(IDummyUtility, name='dummy'), dummy)
        self.assertEquals(list(utils.getUtilitiesFor(IDummyUtility)), 
                          [('',dummy)])
        self.assertEquals(list(utils.getAllUtilitiesRegisteredFor(
            IDummyUtility)), [dummy])

    def test_registerTwoUtilitiesWithSameNameDifferentInterface(self):
        utils = getService(Utilities)
        dummy = DummyUtility()
        superdummy = DummyUtility()
        directlyProvides(superdummy, ISuperDummyUtility)
        utils.registerUtility(IDummyUtility, dummy, 'dummy')
        utils.registerUtility(ISuperDummyUtility, superdummy, 'dummy')

        self.assertEquals(utils.getUtility(IDummyUtility, 'dummy'), dummy)
        self.assertEquals(utils.getUtility(ISuperDummyUtility, 'dummy'),
                          superdummy)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalUtilityServiceTest))
    return suite

if __name__ == '__main__':
    framework()
