##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Introspector view tests

$Id: test_introspector.py,v 1.1 2003/07/02 11:02:16 alga Exp $
"""

import unittest
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.interface import LocalInterfaceService
from zope.app.services.servicenames import Interfaces
from zope.publisher.browser import TestRequest
from zope.app.tests import setup
from zope.interface import Interface
from zope.app.component.globalinterfaceservice import provideInterface

class I1(Interface):
    pass

class TestIntrospectorView(PlacefulSetup, unittest.TestCase):

    def test_getInterfaceURL(self):
        id = 'zope.app.browser.tests.test_introspector.I1'
        rootFolder = setup.buildSampleFolderTree()
        mgr = setup.createServiceManager(rootFolder)
        service = setup.addService(mgr, Interfaces, LocalInterfaceService())

        provideInterface(id, I1)

        from zope.app.browser.introspector import IntrospectorView

        request = TestRequest()
        view = IntrospectorView(rootFolder, request)

        self.assertEqual(
            view.getInterfaceURL(id),
            'http://127.0.0.1/++etc++site/default/Interfaces/detail.html?id=%s'
            % id)

        self.assertEqual(view.getInterfaceURL('zope.app.INonexistent'),
                         '')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntrospectorView))
    return suite


if __name__ == '__main__':
    unittest.main()
