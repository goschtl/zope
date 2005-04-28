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
"""Functional tests for testing pagelet content.

$Id$
"""
import unittest
from zope.app.testing.functional import BrowserTestCase


class TestPageletContent(BrowserTestCase):

    def testPagelet(self):
        # add the PageletContent
        response = self.publish(
            '/+/action.html',
            basic='mgr:mgrpw',
            form={'type_name': u'zope.app.demo.pagelet.PageletContent',
                  'id': u'pagelet'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
            'http://localhost/+/zope.app.demo.pagelet.PageletContent=pagelet')

        # check add form
        response = self.publish(
            '/+/zope.app.demo.pagelet.PageletContent',
            basic='mgr:mgrpw',
            form={'UPDATE_SUBMIT' : 'Add',
                  'add_input_name': u'pagelet',
                  'field.title': 'aTitle'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
            'http://localhost/@@contents.html')

        # check the content of the pagelet without permission
        # we should not get the pagelet content
        response = self.publish('/pagelet/@@index.html')
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('<div>aTitle</div>') != -1)

        # This pagelet is visible because of the zope.View permission
        self.assert_(body.find('Macro: demo_pagelet_macro') != -1)
        
        # we don't have zope.ManageContent permission where is required
        self.assert_(body.find('demo_pagelet_macro2') == -1)

        # check the content of the pagelet with permission
        # now we should see the content of the pagelet
        response = self.publish('/pagelet/@@index.html', basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('<div>aTitle</div>') != -1)

        # As zope.Manager we see both pagelets
        self.assert_(body.find('Macro: demo_pagelet_macro') != -1)
        self.assert_(body.find('demo_pagelet_macro2') == -1)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPageletContent),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
