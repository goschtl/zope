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

    from zope.component.testing import setUp, tearDown

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
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        self.assertTrue(gsm is base)
        self.assertTrue(IComponentLookup.providedBy(gsm))
        self.assertTrue(getGlobalSiteManager() is gsm)

    def test_getSiteManager_no_args(self):
        from zope.component.globalregistry import base
        from zope.component.interfaces import IComponentLookup
        from zope.component import getSiteManager
        sm = getSiteManager()
        self.assertTrue(sm is base)
        self.assertTrue(IComponentLookup.providedBy(sm))
        self.assertTrue(getSiteManager() is sm)

    def test_getSiteManager_w_None(self):
        from zope.component import getSiteManager
        self.assertTrue(getSiteManager(None) is getSiteManager())

    def test_getSiteManager_w_conforming_context(self):
        from zope.component import getSiteManager
        from zope.component.tests.test_doctests \
            import ConformsToIComponentLookup
        sitemanager = object()
        context = ConformsToIComponentLookup(sitemanager)
        self.assertTrue(getSiteManager(context) is sitemanager)

    def test_getSiteManager_w_invalid_context(self):
        from zope.component import getSiteManager
        from zope.component.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, getSiteManager, object())

    def test_getUtilty_anonymous_nonesuch(self):
        from zope.interface import Interface
        from zope.component import getUtility
        from zope.component.interfaces import ComponentLookupError
        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError, getUtility, IFoo)

    def test_getUtilty_named_nonesuch(self):
        from zope.interface import Interface
        from zope.component import getUtility
        from zope.component.interfaces import ComponentLookupError
        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError, getUtility, IFoo, name='bar')

    def test_getUtilty_anonymous_hit(self):
        from zope.interface import Interface
        from zope.component import getGlobalSiteManager
        from zope.component import getUtility
        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        self.assertTrue(getUtility(IFoo) is obj)

    def test_getUtilty_named_hit(self):
        from zope.interface import Interface
        from zope.component import getUtility
        from zope.component import getGlobalSiteManager
        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo, name='bar')
        self.assertTrue(getUtility(IFoo, name='bar') is obj)

    def test_getUtility_w_conforming_context(self):
        from zope.interface import Interface
        from zope.component import getGlobalSiteManager
        from zope.component import getUtility
        from zope.component.tests.test_doctests \
            import ConformsToIComponentLookup
        class SM(object):
            def __init__(self, obj):
                self._obj = obj
            def queryUtility(self, interface, name, default):
                return self._obj
        class IFoo(Interface):
            pass
        obj1 = object()
        obj2 = object()
        sm = SM(obj2)
        context = ConformsToIComponentLookup(sm)
        getGlobalSiteManager().registerUtility(obj1, IFoo)
        self.assertTrue(getUtility(IFoo, context=context) is obj2)

    def test_queryUtilty_anonymous_nonesuch(self):
        from zope.interface import Interface
        from zope.component import queryUtility
        class IFoo(Interface):
            pass
        self.assertEqual(queryUtility(IFoo), None)

    def test_queryUtilty_anonymous_nonesuch_w_default(self):
        from zope.interface import Interface
        from zope.component import queryUtility
        class IFoo(Interface):
            pass
        obj = object()
        self.assertTrue(queryUtility(IFoo, default=obj) is obj)

    def test_queryUtilty_named_nonesuch(self):
        from zope.interface import Interface
        from zope.component import queryUtility
        class IFoo(Interface):
            pass
        self.assertEqual(queryUtility(IFoo, name='bar'), None)

    def test_queryUtilty_named_nonesuch_w_default(self):
        from zope.interface import Interface
        from zope.component import queryUtility
        class IFoo(Interface):
            pass
        obj = object()
        self.assertTrue(queryUtility(IFoo, name='bar', default=obj) is obj)

    def test_queryUtilty_anonymous_hit(self):
        from zope.interface import Interface
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        self.assertTrue(queryUtility(IFoo) is obj)

    def test_queryUtilty_named_hit(self):
        from zope.interface import Interface
        from zope.component import queryUtility
        from zope.component import getGlobalSiteManager
        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo, name='bar')
        self.assertTrue(queryUtility(IFoo, name='bar') is obj)

    def test_queryUtility_w_conforming_context(self):
        from zope.interface import Interface
        from zope.component import getGlobalSiteManager
        from zope.component import queryUtility
        from zope.component.tests.test_doctests \
            import ConformsToIComponentLookup
        class SM(object):
            def __init__(self, obj):
                self._obj = obj
            def queryUtility(self, interface, name, default):
                return self._obj
        class IFoo(Interface):
            pass
        obj1 = object()
        obj2 = object()
        sm = SM(obj2)
        context = ConformsToIComponentLookup(sm)
        getGlobalSiteManager().registerUtility(obj1, IFoo)
        self.assertTrue(queryUtility(IFoo, context=context) is obj2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PackageAPITests),
    ))
