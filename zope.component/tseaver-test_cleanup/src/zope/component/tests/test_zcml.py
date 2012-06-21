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
"""Tests for ZCML directives.
"""
import unittest


class Test_handle(unittest.TestCase):

    def test_uses_configured_site_manager(self):
        from zope.component import getSiteManager
        from zope.component.testfiles.components import comp, IApp
        from zope.component.zcml import handler
        from zope.interface.registry import Components

        registry = Components()
        def dummy(context=None):
            return registry
        getSiteManager.sethook(dummy)

        try:
            handler('registerUtility', comp, IApp, u'')
            self.assertTrue(registry.getUtility(IApp) is comp)
        finally:
            getSiteManager.reset()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_handle),
    ))

