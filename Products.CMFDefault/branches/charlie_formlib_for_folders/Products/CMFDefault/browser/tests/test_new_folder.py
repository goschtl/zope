##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test Products.CMFDefault.browser.new_folder BrowserView tests
$Id$
"""

import unittest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.User import UnrestrictedUser

from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.tests.base.dummy import DummySite, DummyTool
from Products.CMFCore.tests.base.dummy import DummyUserFolder, DummyContent
from Products.CMFCore.interfaces import IPropertiesTool

from Products.CMFDefault.browser.new_folder import ContentsView

class FolderBrowserViewTests(unittest.TestCase):

    def setUp(self):
        """Setup a site"""
        # maybe there is a base class for this?
        self.site = site = DummySite('site')
        self.sm = getSiteManager()
        mtool = site._setObject('portal_membership', DummyTool())
        ptool = site._setObject('portal_properties', DummyTool())
        self.sm.registerUtility(ptool, IPropertiesTool)
        ttool = site._setObject('portal_types', DummyTool())
        utool = site._setObject('portal_url', DummyTool())
        folder = PortalFolder('test_folder')
        self.folder = site._setObject('test_folder', folder)
        self.uf = self.site._setObject('acl_users', DummyUserFolder())
    
    def test_view(self):
        view = ContentsView(self.folder, TestRequest())
        self.failUnless(IBrowserPublisher.providedBy(view))
        
    def test_up_info(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals({'url':u'', 'id':u'Root', 'icon':u''},
                            view.up_info())
        
    def test_list_batch_items(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals(view.list_batch_items(), [])
    
    def test_is_orderable(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.is_orderable())
        
    def test_sort_can_be_changed(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.can_sort_be_changed())
    
    def test_empty_has_subobjects(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.has_subobjects())
        
    def test_has_subobjects(self):
        self._make_one()
        view = ContentsView(self.folder, TestRequest())
        self.failUnless(view.has_subobjects())
        
    def test_check_clipboard_data(self):
        view = ContentsView(self.folder, TestRequest())
        self.failIf(view.check_clipboard_data())
    
    def test_validate_items(self):
        """Cannot validate forms without widgets"""
        view = ContentsView(self.folder, TestRequest())
        self.assertRaises(AttributeError, 
                            view.validate_items, "", {'foo':'bar'})
                            
    def test_get_ids(self):
        view = ContentsView(self.folder, TestRequest())
        self.assertEquals(
                        view._get_ids({'foo':'bar'}),
                        [])
        self.assertEquals(
                        view._get_ids({'DummyItem1.select':True,
                                       'DummyItem2.select':False,
                                       'DummyItem3.select':True}),
                        ['DummyItem1', 'DummyItem3'])
        self.assertEquals(
                        view._get_ids({'delta':True,
                                       'delta':1}),
                        []
                        )
        
    def _make_one(self, name="DummyItem"):
        content = DummyContent(name)
        content.portal_type = "Dummy Content"
        self.folder._setObject(name, content)
        
    def _make_batch(self):
        """Add enough objects to force pagination"""
        batch_size = ContentsView._BATCH_SIZE
        for i in range(batch_size + 2):
            content_id = "Dummy%s" % i
            self._make_one(content_id)

    def site_login(self):
        newSecurityManager(None, 
                    UnrestrictedUser('god', '', ['Manager'], ''))
                    
    def test_no_batches(self):
        """Empty folder should have no next or previous pages"""
        self.site_login()
        request = TestRequest(ACTUAL_URL='http://foo.com/bar')
        view = ContentsView(self.folder, request)
        self.failIf(view.navigation_next())
        self.failIf(view.navigation_previous())
    
    def test_check_next_page(self):
        """First page has a next but no previous page"""
        self.site_login()
        self._make_batch()
        request = TestRequest(ACTUAL_URL='http://foo.com/bar')
        view = ContentsView(self.folder, request)
        self.assertEquals(view.navigation_next()['title'], 
                            "Next ${count} items")
        self.failIf(view.navigation_previous())
                            
    def test_check_prev_page(self):
        """Last page has a previous but no next page"""
        self.site_login()
        self._make_batch()
        request = TestRequest(ACTUAL_URL='http://foo.com/bar')
        request.form = {'b_start':25}
        view = ContentsView(self.folder, request)
        self.assertEquals(view.navigation_previous()['title'], 
                            "Previous ${count} items")
        self.failIf(view.navigation_next())
        
    def test_page_count(self):
        """Check batch page count"""
        self._make_batch()
        request = TestRequest(ACTUAL_URL='http://foo.com/bar')
        view = ContentsView(self.folder, request)
        self.assertEquals(view.page_count(), 2)
        
    def test_page_range(self):
        """Check page range by starting on page fifteen.
        The page range should then be 10 to 19"""
        batch_size = ContentsView._BATCH_SIZE
        for i in range(batch_size * 20):
            content_id = "Dummy%s" % i
            self._make_one(content_id)
        request = TestRequest(ACTUAL_URL='http://foo.com/bar')
        request.form = {'b_start':batch_size * 14}
        view = ContentsView(self.folder, request)
        self.assertEquals(view.page_range()[0]['number'], 11)
        self.assertEquals(view.page_range()[-1]['number'], 20)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderBrowserViewTests))
    return suite