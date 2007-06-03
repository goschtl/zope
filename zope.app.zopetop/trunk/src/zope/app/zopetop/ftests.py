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
"""Functional Tests for `ZopeTop` skin.

$Id$
"""
__docformat__ = 'restructuredtext'
import unittest
import os

from zope.app.testing.functional import ZCMLLayer, BrowserTestCase


ZopeTopLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'ZopeTopLayer', allow_teardown=True)

class ZopeTopSkinTests(BrowserTestCase):
    """Funcional tests for ZopeTop skin."""

    layer = ZopeTopLayer

    def test_ZopeTopIsNotRotterdam(self):
        response1 = self.publish("/++skin++Rotterdam", basic='mgr:mgrpw')
        response2 = self.publish("/++skin++ZopeTop", basic='mgr:mgrpw')
        self.assert_(response1.getBody() != response2.getBody())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZopeTopSkinTests))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
