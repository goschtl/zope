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

$Id: test_templatedpage.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
__docformat__ = 'restructuredtext'
import unittest

from zope.app.testing.functional import BrowserTestCase

class ZopeTopSkinTests(BrowserTestCase):
    """Funcional tests for ZopeTop skin."""

    def test_ZopeTopIsNotRotterdam(self):
        response1 = self.publish("/++skin++zope.app.rotterdam.Rotterdam",
                                 basic='mgr:mgrpw')
        response2 = self.publish("/++skin++zope.app.zopetop.ZopeTop",
                                 basic='mgr:mgrpw')
        self.assert_(response1.getBody() != response2.getBody())

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopeTopSkinTests),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
