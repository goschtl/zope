##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Test Products.CMFDefault.browser.preferences

$Id$
"""

import unittest

from zope.component.testing import PlacelessSetup

from Products.CMFDefault.browser.skins.tests.test_ursa import (
                    DummyRequest, DummySite, DummyContext,
                    DummyPropertiesTool, DummyURLTool, DummyActionsTool
                    )

class PreferencesFormTests(unittest.TestCase, PlacelessSetup):
    
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)
        
    def _getTargetClass(self):
        from Products.CMFDefault.browser.membership.join import Join
        return Join

    def _makeOne(self, site=None):
        if site is None:
            site = self._makeSite()
        request = DummyRequest()
        return self._getTargetClass()(site, request)
        
    def _makeSite(self,):
        from zope.component import getSiteManager
        from Products.CMFCore.interfaces import IPropertiesTool
        site = DummyContext()
        tool = site.portal_properties = DummyPropertiesTool()
        sm = getSiteManager()
        sm.registerUtility(tool, IPropertiesTool)
        site.portal_url = DummyURLTool(site)
        site.portal_membership = DummyMembershipTool()
        site.portal_registration = DummyRegistrationTool()
        site.portal_actions = DummyActionsTool()
        site.absolute_url = lambda: 'http://example.com'
        return site
        
    def test_user_folder(self):
        site = self._makeSite()
        view = self._makeOne(site)
                        

class DummyRegistrationTool:
    pass


class DummyMembershipTool:
    pass


class DummyActionsTool:
    pass


class DummySkinsTool:
    pass