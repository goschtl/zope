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
"""

$Id: test_connectiondirective.py,v 1.3 2003/07/28 22:20:09 jim Exp $
"""

import unittest
from StringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.management import newSecurityManager, system_user
import zope.configuration
import zope.app.component
from zope.component import getService
from zope.app.services.servicenames import SQLDatabaseConnections
from zope.app.rdb import queryConnection, getConnection, getAvailableConnections
from zope.app.rdb import ZopeConnection

def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/rdb'>
      %s
      </zopeConfigure>
      """ % s)

class TestConnectionDirective(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)
        newSecurityManager(system_user)
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.rdb)()
        XMLConfig('service.zcml', zope.app.rdb)()

    def testEmptyDirective(self):
        f = configfile("""
<provideConnection name="stub"
      component="zope.app.rdb.tests.test_zopedatabaseadapter.DAStub"
      dsn="dbi://dbname" />
                       """)
        xmlconfig(f)

    def testGetAvailableConnections(self):
        self.assertEqual(getAvailableConnections(), [])
        f = configfile("""
<provideConnection name="stub"
      component="zope.app.rdb.tests.test_zopedatabaseadapter.DAStub"
      dsn="dbi://dbname" />
                       """)
        xmlconfig(f)
        self.assertEqual(getAvailableConnections(), ["stub"])

    def testGetConnection(self):
        self.assertRaises(KeyError, getConnection, 'stub')
        f = configfile("""
<provideConnection name="stub"
      component="zope.app.rdb.tests.test_zopedatabaseadapter.DAStub"
      dsn="dbi://dbname" />
                       """)
        xmlconfig(f)
        self.failUnless(getConnection('stub'))
        self.assertEqual(getConnection('stub').__class__, ZopeConnection)

    def testQueryConnection(self):
        self.assertEqual(queryConnection('stub', None), None)
        f = configfile("""
<provideConnection name="stub"
      component="zope.app.rdb.tests.test_zopedatabaseadapter.DAStub"
      dsn="dbi://dbname" />
                       """)
        xmlconfig(f)
        self.failUnless(queryConnection('stub'))
        self.assertEqual(queryConnection('stubbie', None), None)

def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestConnectionDirective))
    return suite

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
