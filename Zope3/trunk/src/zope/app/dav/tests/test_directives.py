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

$Id: test_directives.py,v 1.1 2003/08/02 17:26:15 srichter Exp $
"""
import unittest

from zope.app.dav.globaldavschemaservice import davSchemaService
from zope.app.interfaces.component import IDAVSchemaService
from zope.app.services.servicenames import DAVSchema
from zope.component.service import defineService, serviceManager
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
from zope.interface import Interface
import zope.app.dav.tests

  
class ISchema(Interface):
    pass


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        defineService(DAVSchema, IDAVSchemaService)
        serviceManager.provideService(DAVSchema, davSchemaService)

    def test_provideInterface(self):
        self.assertEqual(davSchemaService.queryNamespace(ISchema), None)
        self.context = xmlconfig.file("dav.zcml", zope.app.dav.tests)
        self.assertEqual(davSchemaService.queryNamespace(ISchema),
                         'http://www.zope3.org/dav-schema')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
