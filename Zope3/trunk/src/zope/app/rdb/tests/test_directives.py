##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test 'rdb' ZCML Namespace Directives

$Id: test_directives.py,v 1.2 2003/08/17 06:07:52 philikon Exp $
"""
import unittest

from zope.configuration import xmlconfig
from zope.app.rdb import queryConnection, getAvailableConnections
from zope.app.rdb import ZopeConnection
import zope.app.rdb.tests

class DirectivesTest(unittest.TestCase):

    def test_provideConnection(self):
        self.assertEqual(getAvailableConnections(), [])
        self.assertEqual(queryConnection('stub', None), None)
        self.context = xmlconfig.file("rdb.zcml", zope.app.rdb.tests)
        self.assertEqual(getAvailableConnections(), ["stub"])
        self.assertEqual(queryConnection('stub').__class__, ZopeConnection)
        self.assertEqual(queryConnection('stubbie', None), None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
