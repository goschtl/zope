##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_browser.py,v 1.1 2004/01/16 12:39:04 philikon Exp $
"""

import unittest
from zope.publisher.browser import TestRequest
from zope.app import zapi
from zope.app.tests import ztapi

from zope.products.statictree.utils import TreeStateEncoder
from zope.products.statictree.browser import StaticTreeView

from basetest import BaseTestCase

class BrowserTestCase(BaseTestCase):

    def setUp(self):
        super(BrowserTestCase, self).setUp()
        self.makeItems()
        # provide the view for all objects (None)
        ztapi.browserView(None, 'static_cookie_tree', [StaticTreeView])

    def makeRequest(self):
        request = self.request = TestRequest()

    def makeRequestWithVar(self):
        varname = StaticTreeView.request_variable 
        encoder = TreeStateEncoder()
        tree_state = encoder.encodeTreeState(self.expanded_nodes)
        environ = {varname: tree_state}
        request = TestRequest(environ=environ)
        return request

    def test_cookie_tree_pre_expanded(self):
        request = self.makeRequestWithVar()
        view = zapi.getView(self.root_obj, 'static_cookie_tree', request)
        cookie_tree = view.cookieTree()
        self.assert_(self.root_node.expanded)
        for node in self.root_node.getFlatNodes():
            self.assertEqual(node.expanded, node.getId() in self.expanded_nodes)

    def test_cookie_tree_sets_cookie(self):
        request = self.makeRequestWithVar()
        view = zapi.getView(self.root_obj, 'static_cookie_tree', request)
        cookie_tree = view.cookieTree()
        self.failIf(request.response.getCookie(view.request_variable) is None)

def test_suite():
    return unittest.makeSuite(BrowserTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
