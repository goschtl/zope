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
from zope.publisher.interfaces import NotFound
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

        # check the content of the pagelet
        response = self.publish('/pagelet/@@index.html')
        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find('<div>aTitle</div>') >= 0)
        self.assert_(body.find('<span>global demo variable</span>') >= 0)
        self.assert_(body.find('<h4>Pagelet: demo_pagelet.pt</h4>') >= 0)
        self.assert_(body.find('<h4>Pagelet: demo_pagedata_pagelet.pt</h4>')
            >= 0)
        self.assert_(body.find('<span>DemoPageData title</span>') >= 0)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPageletContent),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
