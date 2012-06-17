##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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

import unittest

class PackageAPITests(unittest.TestCase):

    def test_module_conforms_to_IComponentArchitecture(self):
        from zope.interface.verify import verifyObject
        from zope.component.interfaces import IComponentArchitecture
        import zope.component as zc
        verifyObject(IComponentArchitecture, zc)

    def test_module_conforms_to_IComponentRegistrationConvenience(self):
        from zope.interface.verify import verifyObject
        from zope.component.interfaces import IComponentRegistrationConvenience
        import zope.component as zc
        verifyObject(IComponentRegistrationConvenience, zc)

    def test_getGlobalSiteManager(self):
        from zope.component.globalregistry import base
        from zope.component.interfaces import IComponentLookup
        import zope.component as zc
        gsm = zc.getGlobalSiteManager()
        self.assertTrue(gsm is base)
        self.assertTrue(IComponentLookup.providedBy(gsm))
        self.assertTrue(zc.getGlobalSiteManager() is gsm)

    def test_getSiteManager_no_args(self):
        from zope.component.globalregistry import base
        from zope.component.interfaces import IComponentLookup
        import zope.component as zc
        sm = zc.getSiteManager()
        self.assertTrue(sm is base)
        self.assertTrue(IComponentLookup.providedBy(sm))
        self.assertTrue(zc.getSiteManager() is sm)

    def test_getSiteManager_w_None(self):
        import zope.component as zc
        self.assertTrue(zc.getSiteManager(None) is zc.getSiteManager())

    def test_getSiteManager_w_conforming_context(self):
        import zope.component as zc
        from zope.component.tests.test_doctests \
            import ConformsToIComponentLookup
        sitemanager = object()
        context = ConformsToIComponentLookup(sitemanager)
        self.assertTrue(zc.getSiteManager(context) is sitemanager)

    def test_getSiteManager_w_invalid_context(self):
        import zope.component as zc
        from zope.component.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, zc.getSiteManager, object())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PackageAPITests),
    ))
