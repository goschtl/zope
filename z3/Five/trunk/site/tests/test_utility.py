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
from zope.component.exceptions import ComponentLookupError
from zope.component.service import serviceManager
from zope.component.servicenames import Utilities
from zope.app import zapi
from zope.app.tests.placelesssetup import setUp, tearDown
from zope.app.component.hooks import setSite

import Products.Five
from Products.Five import zcml
from Products.Five.site.interfaces import IRegisterUtilitySimply
from Products.Five.site.localsite import enableLocalSiteHook
from Products.Five.site.tests.dummy import manage_addDummySite, \
     IDummyUtility, ISuperDummyUtility, DummyUtility

class LocalUtilityServiceTest(ZopeTestCase.ZopeTestCase):

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
        enableLocalSiteHook(self.folder.site)
        setSite(self.folder.site)

    def beforeTearDown(self):
        from zope.app.component.localservice import clearSite
        clearSite()
        tearDown()

    def test_getServicesHook(self):
        from Products.Five.site.localsite import FiveSiteManager
        from Products.Five.site.utility import SimpleLocalUtilityService

        local_sm = zapi.getServices(None)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

        local_sm = zapi.getServices(self.folder.site)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

        utils = zapi.getService(Utilities)
        self.failUnless(isinstance(utils, SimpleLocalUtilityService))

    def test_getUtilitiesNoUtilitiesFolder(self):
        utils = zapi.getService(Utilities)
        #XXX test whether utils really is a local utility service...
        self.assertRaises(ComponentLookupError, utils.getUtility, IDummyUtility)
        self.assertEquals(list(utils.getUtilitiesFor(IDummyUtility)), [])
        self.assertEquals(list(utils.getAllUtilitiesRegisteredFor(IDummyUtility)), [])

    def test_registerUtilityOnUtilityService(self):
        utils = zapi.getService(Utilities)
        dummy = DummyUtility()
        utils.registerUtility(IDummyUtility, dummy, 'dummy')

        self.assertEquals(zapi.getUtility(IDummyUtility, name='dummy'), dummy)
        self.assertEquals(list(zapi.getUtilitiesFor(IDummyUtility)), 
                          [('',dummy)])
        self.assertEquals(list(zapi.getAllUtilitiesRegisteredFor(
            IDummyUtility)), [dummy])

    def test_registerUtilityOnSiteManager(self):
        sm = zapi.getServices()
        self.failUnless(IRegisterUtilitySimply.providedBy(sm))
        dummy = DummyUtility()
        sm.registerUtility(IDummyUtility, dummy, 'dummy')

        self.assertEquals(zapi.getUtility(IDummyUtility, name='dummy'), dummy)
        self.assertEquals(list(zapi.getUtilitiesFor(IDummyUtility)), 
                          [('',dummy)])
        self.assertEquals(list(zapi.getAllUtilitiesRegisteredFor(
            IDummyUtility)), [dummy])

    def test_registerTwoUtilitiesWithSameNameDifferentInterface(self):
        sm = zapi.getServices()
        self.failUnless(IRegisterUtilitySimply.providedBy(sm))
        dummy = DummyUtility()
        superdummy = DummyUtility()
        directlyProvides(superdummy, ISuperDummyUtility)
        sm.registerUtility(IDummyUtility, dummy, 'dummy')
        sm.registerUtility(ISuperDummyUtility, superdummy, 'dummy')

        self.assertEquals(zapi.getUtility(IDummyUtility, 'dummy'), dummy)
        self.assertEquals(zapi.getUtility(ISuperDummyUtility, 'dummy'),
                          superdummy)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalUtilityServiceTest))
    return suite

if __name__ == '__main__':
    framework()
