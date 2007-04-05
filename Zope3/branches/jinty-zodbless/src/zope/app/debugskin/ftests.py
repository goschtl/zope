##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Functional Tests for Code Documentation Module.

$Id$
"""
import unittest
from zope.app.testing.functional import BrowserTestCase
from zope.app.debugskin.testing import DebugSkinLayer

class DebugSkinTests(BrowserTestCase):

    def testNotFound(self):
        response = self.publish('/++skin++Debug/foo', 
                                basic='mgr:mgrpw', handle_errors=True)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find(
            'zope.publisher.interfaces.NotFound') > 0)
        self.assert_(body.find(
            'raise NotFound(self.context, name, request)') > 0)
        self.checkForBrokenLinks(body, '/++skin++Debug/foo',
                                 basic='mgr:mgrpw')

def test_suite():
    DebugSkinTests.layer = DebugSkinLayer
    return unittest.TestSuite((
        unittest.makeSuite(DebugSkinTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
