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

$Id: test_fieldfactory.py,v 1.1 2003/08/05 14:25:06 sidnei Exp $
"""

import unittest
from StringIO import StringIO

from zope.component.exceptions import ComponentLookupError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.management import newSecurityManager, system_user
from zope.security.proxy import Proxy
import zope.app.security
import zope.app.component
from zope.app.security.exceptions import UndefinedPermissionError
from zope.component import getService
from zope.app.services.servicenames import Factories
from zope.schema.interfaces import IField, IText
from zope.interface import Interface
from zope.configuration import xmlconfig

class IFoo(Interface): pass

class TestFieldFactory(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        newSecurityManager(system_user)
        context = xmlconfig.file('tests/test_fieldfactory.zcml',
                                 zope.app.schema)

    def testRegisterFields(self):
        factory = getService(None, Factories).getFactory('zope.schema._bootstrapfields.Text')
        self.assertEquals(factory.title, "Text Field")
        self.assertEquals(factory.description, "Text Field")

    def testGetFactoriesForIField(self):
        factories = getService(None, Factories).getFactoriesFor(IField)
        self.assertEqual(len(factories), 3)

    def testGetFactoriesForIText(self):
        factories = getService(None, Factories).getFactoriesFor(IText)
        self.assertEqual(len(factories), 2)

    def testGetFactoriesUnregistered(self):
        fservice = getService(None, Factories)
        self.assertRaises(ComponentLookupError, fservice.getFactoriesFor,
                          IFoo)

    def testQueryFactoriesUnregistered(self):
        fservice = getService(None, Factories)
        self.assertEqual(fservice.queryFactoriesFor(IFoo, None), None)

def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestFieldFactory))
    return suite


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
