##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Introspector funcional tests

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.app.tests.functional import BrowserTestCase


class TestIntrospector(BrowserTestCase):

    def test_introspector(self):
        response = self.publish('/@@classBrowser.html', basic='mgr:mgrpw')
        self.checkForBrokenLinks(response.getBody(), response.getPath(),
                                 basic='mgr:mgrpw')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntrospector))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
