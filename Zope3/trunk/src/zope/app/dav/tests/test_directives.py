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
"""Test the wiki ZCML namespace directives.

$Id: test_directives.py,v 1.4 2004/03/13 23:54:59 srichter Exp $
"""
import unittest

from zope.configuration import xmlconfig
from zope.interface import Interface

from zope.app import zapi
from zope.app.servicenames import Utilities
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.dav.interfaces import IDAVNamespace
import zope.app.dav.tests

ns = 'http://www.zope3.org/dav-schema'

class ISchema(Interface):
    pass

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def test_provideInterface(self):
        utils = zapi.getService(None, Utilities)
        self.assertEqual(utils.queryUtility(IDAVNamespace, name=ns), None)
        self.context = xmlconfig.file("dav.zcml", zope.app.dav.tests)
        self.assertEqual(utils.queryUtility(IDAVNamespace, name=ns), ISchema)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
