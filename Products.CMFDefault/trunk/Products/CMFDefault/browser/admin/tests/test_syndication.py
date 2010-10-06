##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for portal syndication form"""

import unittest

from zope.interface import alsoProvides
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.publisher.browser import TestRequest

from Products.CMFCore.tests.base.dummy import DummySite, DummyTool, DummyFolder


class DummySyndicationTool(object):

    isAllowed = False
    syUpdatePeriod = updatePeriod = "daily"
    syUpdateFrequency = updateFrequency = 1
    syUpdateBase = updateBase = ""
    max_items = 15

    def editProperties(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def isSiteSyndicationAllowed(self):
        return self.isAllowed


class DummyResponse(object):

    def redirect(self, value):
        self.location = value


class DummyRequest(TestRequest):


    def __init__(self, **kw):
        super(DummyRequest, self).__init__(kw)
        self.RESPONSE = DummyResponse()

    def getPreferredCharsets(self):
        return ['utf-8']


class SyndicationViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        self.site = site = DummySite('site')
        site.portal_syndication = DummySyndicationTool()
        site._setObject('portal_actions', DummyTool())
        site._setObject('portal_url', DummyTool())
        site._setObject('portal_membership', DummyTool())

    def _getTargetClass(self):
        from Products.CMFDefault.browser.admin.syndication import Site
        request = DummyRequest(ACTUAL_URL="http://example.com")
        alsoProvides(request, IUserPreferredCharsets)
        return Site(self.site, request)

    def test_enabled(self):
        view = self._getTargetClass()
        self.assertFalse(view.enabled())

    def test_disabled(self):
        view = self._getTargetClass()
        self.assertTrue(view.disabled())

    def test_handle_enable(self):
        view = self._getTargetClass()
        data = {'frequency':3, 'period':'weekly', 'base':'', 'max_items':10}
        view.handle_enable("enable", data)
        self.assertTrue(view.enabled())
        self.assertEqual(view.status, u"Syndication enabled")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20enabled")

    def test_handle_update(self):
        view = self._getTargetClass()
        self.assertEqual(view.syndtool.updatePeriod, 'daily')
        self.assertEqual(view.syndtool.updateFrequency,  1)
        self.assertEqual(view.syndtool.updateBase, "")
        self.assertEqual(view.syndtool.max_items, 15)
        data = {'frequency':3, 'period':'weekly', 'base':'active',
                'max_items':10}
        view.handle_update("update", data)
        self.assertEqual(view.syndtool.updatePeriod, 'weekly')
        self.assertEqual(view.syndtool.updateFrequency, 3)
        self.assertEqual(view.syndtool.updateBase, "active")
        self.assertEqual(view.syndtool.max_items, 10)
        self.assertEqual(view.status, u"Syndication updated")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20updated")

    def test_handle_disable(self):
        view = self._getTargetClass()
        view.syndtool.isAllowed = True
        self.assertTrue(view.enabled)
        view.handle_disable("disable", {})
        self.assertTrue(view.disabled)
        self.assertEqual(view.status, u"Syndication disabled")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20disabled")


from Products.CMFCore.interfaces import ISyndicationInfo, IFolderish
from Products.CMFDefault.SyndicationInfo import SyndicationInfo

class FolderSyndicationTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        from zope.component import getSiteManager
        self.site = site = DummySite('site')
        sm = getSiteManager()
        info = SyndicationInfo
        sm.registerAdapter(info, [IFolderish], ISyndicationInfo)
        site.portal_syndication = DummySyndicationTool()
        site._setObject('portal_actions', DummyTool())
        site._setObject('portal_url', DummyTool())
        site._setObject('portal_membership', DummyTool())

    def _getTargetClass(self):
        from Products.CMFDefault.browser.admin.syndication import Syndicate
        self.site._setObject('folder', DummyFolder('Folder'))
        alsoProvides(self.site, IFolderish)
        request = DummyRequest(ACTUAL_URL="http://example.com")
        alsoProvides(request, IUserPreferredCharsets)
        return Syndicate(self.site, request)

    def test_allowed(self):
        view = self._getTargetClass()
        self.assertFalse(view.allowed())

    def test_adapter(self):
        from Products.CMFCore.interfaces import ISyndicationInfo
        view = self._getTargetClass()
        self.assertTrue(ISyndicationInfo.providedBy(view.adapter))

    def test_enabled(self):
        view = self._getTargetClass()
        self.assertFalse(view.enabled())

    def test_disabled(self):
        view = self._getTargetClass()
        self.assertTrue(view.disabled())

    def test_handle_enable(self):
        self.site.portal_syndication.isAllowed = 1
        view = self._getTargetClass()
        view.handle_enable("enable", {})
        self.assertTrue(view.enabled())
        self.assertEqual(view.status, u"Syndication enabled")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20enabled")

    def test_handle_disable(self):
        self.site.portal_syndication.isAllowed = 1
        view = self._getTargetClass()
        view.adapter.enable()
        view.handle_disable("disable", {})
        self.assertFalse(view.enabled())
        self.assertEqual(view.status, u"Syndication disabled")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20disabled")

    def test_handle_update(self):
        view = self._getTargetClass()
        values = {'frequency': 4, 'period': 'weekly', 'base': '2010-01-01',
                  'max_items': 25}
        view.handle_update("update", values)
        self.assertEqual(view.adapter.get_info(), values)
        self.assertEqual(view.status, u"Syndication updated")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20updated")

    def test_handle_revert(self):
        view = self._getTargetClass()
        values = {'frequency': 4, 'period': 'weekly', 'base': '2010-01-01',
                  'max_items': 25}
        view.handle_update("update", values)
        view.handle_revert("", values)
        self.assertNotEqual(view.adapter.get_info(), values)
        self.assertEqual(view.status, u"Syndication reset to site default")
        self.assertEqual(view.request.RESPONSE.location,
            "http://www.foobar.com/bar/site?portal_status_message="
            "Syndication%20reset%20to%20site%20default")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SyndicationViewTests))
    suite.addTest(unittest.makeSuite(FolderSyndicationTests))
    return suite
