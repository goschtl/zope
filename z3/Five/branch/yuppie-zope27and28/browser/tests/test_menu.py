##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test browser menus

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

from zope.app.publisher.browser.globalbrowsermenuservice import \
     globalBrowserMenuService

import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.traversable import newInteraction, FakeRequest
from Products.Five.testing import manage_addFiveTraversableFolder

class MenuTest(ZopeTestCase):

    def afterSetUp(self):
	newInteraction()  # needed for menu configuration
	zcml.load_config('menu.zcml', package=Products.Five.browser.tests)
	manage_addFiveTraversableFolder(self.folder, 'test', 'Test')

    def test_menu(self):
        request = FakeRequest()
        # XXX not sure why we need this..
        request.getURL = lambda: 'http://www.infrae.com'
        menu = globalBrowserMenuService.getMenu('testmenu',
                                                self.folder.test,
                                                request)
        self.assertEquals(3, len(menu))
        # sort menu items by title so we get a stable testable result
        menu.sort(lambda x, y: cmp(x['title'], y['title']))
        self.assertEquals('Test Menu Item', menu[0]['title'])
        self.assertEquals('seagull.html', menu[0]['action'])
        self.assertEquals('Test Menu Item 2', menu[1]['title'])
        self.assertEquals('parakeet.html', menu[1]['action'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MenuTest))
    return suite

if __name__ == '__main__':
    framework()
