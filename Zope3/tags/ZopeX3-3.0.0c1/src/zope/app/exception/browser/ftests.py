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
"""Functional tests for NotFoundError

$Id: ftests.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest
from zope.publisher.interfaces import NotFound
from zope.app.tests.functional import BrowserTestCase

class TestNotFound(BrowserTestCase):

    def testNotFound(self):
        response = self.publish('/foobar', basic='mgr:mgrpw',
                                handle_errors=True)
        self.assertEqual(response.getStatus(), 404)
        body = response.getBody()
        self.assert_(
            'The page that you are trying to access is not available' in body)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestNotFound),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
