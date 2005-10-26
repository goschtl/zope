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

from zope.component import getServices
from zope.app.component.localservice import clearSite
from zope.app.tests.placelesssetup import tearDown
from zope.app.component.hooks import getSite

import Products.Five
from Products.Five import zcml
from Products.Five.site.localsite import enableLocalSiteHook
from Products.Five.site.tests.test_sitemanager import Folder, ServiceServiceStub

class BeforeTraversalTest(ZopeTestCase.FunctionalTestCase):

    def afterSetUp(self):
        zcml.load_config("configure.zcml", Products.Five)
        zcml_text = """\
        <five:localsite
            xmlns:five="http://namespaces.zope.org/five"
            class="Products.Five.testing.localsite.DummySite" />"""
        zcml.load_string(zcml_text)

    def beforeTearDown(self):
        clearSite()
        tearDown()

    def test_before_traversal_event_and_hook(self):
        f1 = Folder()
        f1.id = 'f1'
        self.folder._setObject('f1', f1)
        f1 = self.folder._getOb('f1')
        ss = ServiceServiceStub()
        f1.setSiteManager(ss)
        enableLocalSiteHook(f1)
        path = '/'.join(f1.getPhysicalPath())
        response = self.publish(path)
        self.assertEqual(getServices(), ss)

    def test_no_before_traversal_event(self):
        path = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(path)
        self.assertEqual(getSite(), None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BeforeTraversalTest))
    return suite

if __name__ == '__main__':
    framework()
