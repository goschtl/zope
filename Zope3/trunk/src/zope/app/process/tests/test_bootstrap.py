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
"""Bootstrap tests

$Id: test_bootstrap.py,v 1.1 2003/07/02 10:59:19 alga Exp $
"""

import unittest
from transaction import get_transaction
from zodb.db import DB
from zodb.storage.memory import MemoryFullStorage
from zope.app.content.folder import RootFolder
from zope.app.interfaces.content.folder import IRootFolder
from zope.app.interfaces.services.error import IErrorReportingService
from zope.app.interfaces.services.principalannotation \
     import IPrincipalAnnotationService
from zope.app.interfaces.services.event import IEventService
from zope.app.interfaces.services.hub import IObjectHub
from zope.app.interfaces.component import IInterfaceService
from zope.app.publication.zopepublication import ZopePublication
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.error import ErrorReportingService
from zope.app.services.servicenames import ErrorLogging
from zope.app.traversing import traverse, traverseName
from zope.component.exceptions import ComponentLookupError
from zope.exceptions import NotFoundError
from zope.app.services.service import ServiceManager
__metaclass__ = type

class EventStub:

    def __init__(self, db):
        self.database = db


class TestBootstrapSubscriberBase(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.storage = MemoryFullStorage("Memory Storage")
        self.db = DB(self.storage)

    def createRootFolder(self):
        cx = self.db.open()
        root = cx.root()
        self.root_folder = RootFolder()
        root[ZopePublication.root_name] = self.root_folder
        get_transaction().commit()
        cx.close()

    def createRFAndSM(self):
        cx = self.db.open()
        root = cx.root()
        self.root_folder = RootFolder()
        root[ZopePublication.root_name] = self.root_folder
        self.service_manager = ServiceManager()
        self.root_folder.setServiceManager(self.service_manager)
        get_transaction().commit()
        cx.close()


    def test_notify(self):
        from zope.app.process.bootstrap import BootstrapSubscriberBase

        for setup in (lambda: None), self.createRootFolder, self.createRFAndSM:

            setup()

            BootstrapSubscriberBase().notify(EventStub(self.db))

            cx = self.db.open()
            root = cx.root()
            root_folder = root.get(ZopePublication.root_name, None)
            self.assert_(IRootFolder.isImplementedBy(root_folder))

            package_name = '/++etc++site/default'
            package = traverse(root_folder, package_name)

            cx.close()

    def test_ensureService(self):
        from zope.app.process.bootstrap import BootstrapSubscriberBase

        self.createRFAndSM()
        bs = BootstrapSubscriberBase()
        bs.notify(EventStub(self.db))
        for i in range(2):
            cx = self.db.open()
            name = bs.ensureService(ErrorLogging, ErrorReportingService)

            if i == 0:
                self.assertEqual(name, 'ErrorLogging-1')
            else:
                self.assertEqual(name, None)

            root = cx.root()
            root_folder = root[ZopePublication.root_name]

            package_name = '/++etc++site/default'
            package = traverse(root_folder, package_name)

            self.assert_(IErrorReportingService.isImplementedBy(
                traverse(package, 'ErrorLogging-1')))
            get_transaction().commit()
            cx.close()

class TestBootstrapInstance(TestBootstrapSubscriberBase):

    def test_bootstrapInstance(self):
        from zope.app.process.bootstrap import bootstrapInstance

        bootstrapInstance.notify(EventStub(self.db))

        cx = self.db.open()
        root = cx.root()
        root_folder = root[ZopePublication.root_name]

        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)

        self.assert_(IEventService.isImplementedBy(
            traverse(package, 'EventPublication-1')))

        self.assert_(IObjectHub.isImplementedBy(
            traverse(package, 'HubIds-1')))

        self.assert_(IErrorReportingService.isImplementedBy(
            traverse(package, 'ErrorLogging-1')))

        self.assert_(IPrincipalAnnotationService.isImplementedBy(
            traverse(package, 'PrincipalAnnotation-1')))

        cx.close()

    def test_bootstrapInstance_withServices(self):
        from zope.app.process.bootstrap import bootstrapInstance
        from zope.app.process.bootstrap import addService, configureService

        self.createRFAndSM()

        name = addService(self.root_folder, 'Errors',
                          ErrorReportingService, copy_to_zlog=True)
        configureService(self.root_folder, ErrorLogging, name)

        bootstrapInstance.notify(EventStub(self.db))

        cx = self.db.open()
        root = cx.root()
        root_folder = root[ZopePublication.root_name]

        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)

        self.assert_(IEventService.isImplementedBy(
            traverse(package, 'EventPublication-1')))

        self.assert_(IObjectHub.isImplementedBy(
            traverse(package, 'HubIds-1')))

        self.assertRaises(NotFoundError, traverse, root_folder,
                          '/++etc++site/default/ErrorLogging-1')

        self.assert_(IErrorReportingService.isImplementedBy(
            traverse(package, 'Errors-1')))

        self.assert_(IEventService.isImplementedBy(
            traverse(package, 'EventPublication-1')))

        self.assert_(IPrincipalAnnotationService.isImplementedBy(
            traverse(package, 'PrincipalAnnotation-1')))

        cx.close()

class TestCreateInterfaceService(TestBootstrapSubscriberBase):

    def test_createInterfaceService(self):
        from zope.app.process.bootstrap import createInterfaceService

        createInterfaceService.notify(EventStub(self.db))

        cx = self.db.open()
        root = cx.root()
        root_folder = root.get(ZopePublication.root_name, None)
        self.assert_(IRootFolder.isImplementedBy(root_folder))

        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)

        self.assert_(IInterfaceService.isImplementedBy(
            traverse(package, 'Interfaces-1')))

        cx.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBootstrapSubscriberBase))
    suite.addTest(unittest.makeSuite(TestBootstrapInstance))
    suite.addTest(unittest.makeSuite(TestCreateInterfaceService))
    return suite


if __name__ == '__main__':
    unittest.main()
