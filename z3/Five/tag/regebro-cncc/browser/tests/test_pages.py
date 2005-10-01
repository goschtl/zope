##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Test browser pages

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from zope.app.tests.placelesssetup import setUp, tearDown

import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.browser.tests.pages import SimpleView
from Products.Five.testing.simplecontent import manage_addSimpleContent

from Acquisition import aq_parent, aq_base

ZopeTestCase.installProduct('Five')

class TestViewAcquisitionWrapping(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        #setUp()
        zcml.load_config("configure.zcml", Products.Five)
        zcml.load_config('pages.zcml', package=Products.Five.browser.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

    def test_view_wrapper(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assertNotEqual(view, None)
        self.assertEqual(isinstance(view, SimpleView), True)
        self.assertEqual(view(), 'The eagle has landed')

        # this sucks, but we know it
        self.assertEqual(aq_parent(view.context), view)

        # this is the right way to get the context parent
        self.assertNotEqual(view.context.aq_inner.aq_parent, view)
        self.assertEqual(view.context.aq_inner.aq_parent, self.folder)


def test_suite():
    import unittest
    from Testing.ZopeTestCase import installProduct, ZopeDocFileSuite
    from Testing.ZopeTestCase import FunctionalDocFileSuite
    installProduct('PythonScripts')  # for Five.testing.restricted
    suite = unittest.TestSuite(
       (ZopeDocFileSuite('pages.txt',
                         package='Products.Five.browser.tests'),
        FunctionalDocFileSuite('pages_ftest.txt',
                               package='Products.Five.browser.tests'))
       )
    suite.addTest(unittest.makeSuite(TestViewAcquisitionWrapping))
    return suite

if __name__ == '__main__':
    framework()
