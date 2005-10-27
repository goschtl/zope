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

from zope.app import zapi
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.app.component.hooks import setSite, clearSite, setHooks
from zope.app import zapi

import Products.Five
from Products.Five import zcml
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

        # Hook up custom component architecture calls; we need to do
        # this here because zope.app.component.hooks registers a
        # cleanup with the testing cleanup framework, so the hooks get
        # torn down by placelesssetup each time.
        setHooks()

    def beforeTearDown(self):
        clearSite()
        tearDown()

    def test_getSiteManagerHook(self):
        from Products.Five.site.localsite import FiveSiteManager
        from Products.Five.site.utility import SimpleLocalUtilityRegistry

        local_sm = zapi.getSiteManager(None)
        self.failIf(local_sm is zapi.getGlobalSiteManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

        local_sm = zapi.getSiteManager(self.folder.site)
        self.failIf(local_sm is zapi.getGlobalSiteManager)
        self.failUnless(isinstance(local_sm, FiveSiteManager))

        sm = zapi.getSiteManager()
        self.failUnless(isinstance(sm.utilities, SimpleLocalUtilityRegistry))

    def test_getUtilitiesNoUtilitiesFolder(self):
        sm = zapi.getSiteManager()
        #XXX test whether sm really is a local site...
        self.failUnless(sm.queryUtility(IDummyUtility) is None)
        self.assertEquals(list(sm.getUtilitiesFor(IDummyUtility)), [])
        self.assertEquals(list(sm.getAllUtilitiesRegisteredFor(IDummyUtility)), [])

    def test_registerUtility(self):
        sm = zapi.getSiteManager()
        dummy = DummyUtility()
        sm.registerUtility(IDummyUtility, dummy, 'dummy')

        self.assertEquals(zapi.getUtility(IDummyUtility, name='dummy'), dummy)
        self.assertEquals(list(sm.getUtilitiesFor(IDummyUtility)), 
                          [('',dummy)])
        self.assertEquals(list(sm.getAllUtilitiesRegisteredFor(
            IDummyUtility)), [dummy])

    def test_registerTwoUtilitiesWithSameNameDifferentInterface(self):
        sm = zapi.getSiteManager()
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
