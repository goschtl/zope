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

Revision information:
$Id: test_module.py,v 1.2 2002/12/31 18:41:47 jeremy Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner

from zope.interface import Interface
from zope.app.content.folder import RootFolder
from zope.app.content.folder import Folder
from zope.proxy.context import getWrapperContext, getWrapperContainer
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceConfiguration
from zope.component import getService, getServiceManager
from zope.exceptions import ZopeError
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.services.configuration import Registered
from zope.component.service import serviceManager
from zope.proxy.context import ContextWrapper as cw
from zope.app.services.module import Manager
from zodb.storage.file import FileStorage
from zodb.db import DB
from transaction import get_transaction


class ITestService(Interface):
    pass

class TestService:

    __implements__ = ITestService

class ServiceManagerTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

    def _Test__new(self):
        return ServiceManager()

    def test_resolve(self):
        self.rootFolder.setServiceManager(ServiceManager())
        sm = traverse(self.rootFolder, "++etc++Services")
        default = traverse(sm, "Packages/default")
        default.setObject('m1', Manager())
        manager = traverse(default, "m1")
        manager.new('zope.app.services.tests.sample1',
                    "class C:\n"
                    "    def __init__(self, v):\n"
                    "        self.ini = v\n"
                    "\n"
                    "x=1\n"
                    )

        db = DB(FileStorage('test.fs', create=1))
        conn = db.open()
        root = conn.root()
        root['Application'] = self.rootFolder
        get_transaction().commit()

        C = sm.resolve("zope.app.services.tests.sample1.C")
        c = C(42)
        self.assertEqual(c.ini, 42)
        x = sm.resolve("zope.app.services.tests.sample1.x")
        self.assertEqual(x, 1)
        
        conn2 = db.open()
        rootFolder2 = conn2.root()['Application']
        sm2 = traverse(rootFolder2, "++etc++Services")

        C = sm2.resolve("zope.app.services.tests.sample1.C")
        c = C(42)
        self.assertEqual(c.ini, 42)
        x = sm2.resolve("zope.app.services.tests.sample1.x")
        self.assertEqual(x, 1)


def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ServiceManagerTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
