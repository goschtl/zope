##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for testing pagelet chooser content.

$Id$
"""
import unittest
from zope.app.testing.functional import BrowserTestCase


class TestPageletChooserContent(BrowserTestCase):

    def testPagelet(self):
        # test add view
        type_name = u'zope.app.demo.pageletchooser.PageletChooserContent'
        response = self.publish(
            '/+/action.html',
            basic='mgr:mgrpw',
            form={'type_name': type_name,
                  'id': u'chooser'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'), 'http://localhost' \
            + '/+/zope.app.demo.pageletchooser.PageletChooserContent=chooser')

        # add pagelet
        response = self.publish(
            '/+/zope.app.demo.pageletchooser.PageletChooserContent',
            basic='mgr:mgrpw',
            form={'UPDATE_SUBMIT' : 'Add',
                  'add_input_name': u'chooser',
                  'field.title': 'aTitle'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
            'http://localhost/@@contents.html')

        # check the content of the pagelet
        response = self.publish('/chooser/@@index.html')
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('<span>aTitle</span>') >= 0)
        self.assert_(body.find("didn't find a pagelet macro!") >= 0)

        # change pagelet name
        response = self.publish(
            '/chooser/@@select_pageletmacroname.html',
            basic='mgr:mgrpw',
            form={'UPDATE_SUBMIT' : 'Change',
                  'field.firstlevel': 'firstlevel_macro_20'})
        self.assertEqual(response.getStatus(), 200)

        # check new pagelet content
        response = self.publish('/chooser/@@index.html')
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('Content of: firstlevel_macro_20') >= 0)
        


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPageletChooserContent),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
