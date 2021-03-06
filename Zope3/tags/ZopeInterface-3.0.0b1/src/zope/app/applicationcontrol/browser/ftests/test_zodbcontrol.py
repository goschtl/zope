##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""ZODB Control Tests

$Id$
"""
import unittest

from zope.app.tests.functional import BrowserTestCase


class ZODBControlTest(BrowserTestCase):

    def testZODBControlOverview(self):
        response = self.publish('/++etc++process/@@ZODBControl.html',
                                basic='mgr:mgrpw',
                                form={'days': u'3'})
        body = response.getBody()
        self.assert_('value="3"' in body)
        self.assert_('<em>Demo Storage</em>' in body)
        self.assert_('<em>100 Bytes</em>' in body)
        
    # XXX: Disabled test, since we cannot packe demo storages.
    def _testPack(self):
        response = self.publish('/++etc++process/@@ZODBControl.html',
                                basic='mgr:mgrpw',
                                form={'days': u'0',
                                      'PACK': u'Pack'})
        body = response.getBody()
        self.assert_('value="0"' in body)
        self.assert_('<em>Demo Storage</em>' in body)
        self.assert_('<em>100 Bytes</em>' in body)
        self.assert_('ZODB successfully packed.' in body)
        



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZODBControlTest))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
