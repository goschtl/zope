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
"""Tests for the Interface Documentation Module

$Id: tests.py,v 1.1 2004/01/29 17:51:12 srichter Exp $
"""
import unittest
from zope.app import zapi
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.location import LocationProxy
from zope.app.tests import placelesssetup
from zope.interface import implements
from zope.products.apidoc.interfaces import IDocumentationModule
from zope.products.apidoc.ifacemodule import InterfaceModule
from zope.products.apidoc.zcmlmodule import ZCMLModule
from zope.testing.doctestunit import DocTestSuite


def setUp():
    placelesssetup.setUp()
    service = zapi.getService(None, 'Utilities')
    service.provideUtility(IDocumentationModule, InterfaceModule(), 'Interface')
    service.provideUtility(IDocumentationModule, ZCMLModule(), 'ZCML')

def tearDown():
    placelesssetup.tearDown()


class Root:
    implements(IContainmentRoot)

    __parent__ = None
    __name__ = ''

def rootLocation(obj, name):
    return LocationProxy(obj, Root(), name)
    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.products.apidoc'),
        DocTestSuite('zope.products.apidoc.utilities'),
        ))

if __name__ == '__main__':
    unittest.main()
