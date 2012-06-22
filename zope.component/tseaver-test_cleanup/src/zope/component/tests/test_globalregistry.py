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
""" Tests for z.c._api
"""
import unittest

class Test_getGlobalSiteManager(unittest.TestCase):

    def _callFUT(self):
        from zope.component.globalregistry import getGlobalSiteManager
        return getGlobalSiteManager()

    def test_gsm_is_IComponentLookup(self):
        from zope.component.globalregistry import base
        from zope.component.interfaces import IComponentLookup
        gsm = self._callFUT()
        self.assertTrue(gsm is base)
        self.assertTrue(IComponentLookup.providedBy(gsm))

    def test_gsm_is_singleton(self):
        gsm = self._callFUT()
        self.assertTrue(self._callFUT() is gsm)

    def test_gsm_pickling(self):
        import cPickle
        gsm = self._callFUT()
        dumped = cPickle.dumps(gsm)
        loaded = cPickle.loads(dumped)
        self.assertTrue(loaded is gsm)

        dumped_utilities = cPickle.dumps(gsm.utilities)
        loaded_utilities = cPickle.loads(dumped_utilities)
        self.assertTrue(loaded_utilities is gsm.utilities)

        dumped_adapters = cPickle.dumps(gsm.adapters)
        loaded_adapters = cPickle.loads(dumped_adapters)
        self.assertTrue(loaded_adapters is gsm.adapters)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_getGlobalSiteManager),
    ))
