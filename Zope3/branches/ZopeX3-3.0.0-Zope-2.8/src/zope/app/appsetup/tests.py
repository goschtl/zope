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
"""Bootstrap tests

$Id$
"""
import unittest
import transaction
from ZODB.tests.util import DB
from zope.exceptions import NotFoundError

from zope.app.folder import rootFolder
from zope.app.folder.interfaces import IRootFolder
from zope.app.errorservice.interfaces import IErrorReportingService
from zope.app.principalannotation.interfaces import IPrincipalAnnotationService
from zope.app.publication.zopepublication import ZopePublication
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.errorservice import ErrorReportingService
from zope.app.servicenames import ErrorLogging
from zope.app.traversing.api import traverse
from zope.app.site.service import ServiceManager

class EventStub(object):

    def __init__(self, db):
        self.database = db


class TestBootstrapSubscriberBase(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.db = DB()

    def tearDown(self):
        PlacefulSetup.tearDown(self)
        self.db.close()

    def createRootFolder(self):
        cx = self.db.open()
        root = cx.root()
        self.root_folder = rootFolder()
        root[ZopePublication.root_name] = self.root_folder
        transaction.commit()
        cx.close()

    def createRFAndSM(self):
        cx = self.db.open()
        root = cx.root()
        self.root_folder = rootFolder()
        root[ZopePublication.root_name] = self.root_folder
        self.service_manager = ServiceManager(self.root_folder)
        self.root_folder.setSiteManager(self.service_manager)
        transaction.commit()
        cx.close()


    def test_notify(self):
        from zope.app.appsetup.bootstrap import BootstrapSubscriberBase

        for setup in (lambda: None), self.createRootFolder, self.createRFAndSM:

            setup()

            BootstrapSubscriberBase()(EventStub(self.db))

            cx = self.db.open()
            root = cx.root()
            root_folder = root.get(ZopePublication.root_name, None)
            self.assert_(IRootFolder.providedBy(root_folder))

            package_name = '/++etc++site/default'
            package = traverse(root_folder, package_name)

            cx.close()

    def test_ensureService(self):
        from zope.app.appsetup.bootstrap import BootstrapSubscriberBase

        self.createRFAndSM()
        bs = BootstrapSubscriberBase()
        bs(EventStub(self.db))
        for i in range(2):
            cx = self.db.open()
            name = bs.ensureService(ErrorLogging, ErrorReportingService)

            if i == 0:
                self.assertEqual(name, 'ErrorLogging')
            else:
                self.assertEqual(name, None)

            root = cx.root()
            root_folder = root[ZopePublication.root_name]

            package_name = '/++etc++site/default'
            package = traverse(root_folder, package_name)

            self.assert_(IErrorReportingService.providedBy(
                traverse(package, 'ErrorLogging')))
            transaction.commit()
            cx.close()

class TestBootstrapInstance(TestBootstrapSubscriberBase):

    def test_bootstrapInstance(self):
        from zope.app.appsetup.bootstrap import bootstrapInstance

        bootstrapInstance(EventStub(self.db))

        cx = self.db.open()
        root = cx.root()
        root_folder = root[ZopePublication.root_name]

        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)

        self.assert_(IErrorReportingService.providedBy(
            traverse(package, 'ErrorLogging')))

        self.assert_(IPrincipalAnnotationService.providedBy(
            traverse(package, 'PrincipalAnnotation')))

        cx.close()

    def test_bootstrapInstance_withServices(self):
        from zope.app.appsetup.bootstrap import bootstrapInstance
        from zope.app.appsetup.bootstrap import addService, configureService

        self.createRFAndSM()

        name = addService(self.root_folder, 'Errors',
                          ErrorReportingService, copy_to_zlog=True)
        configureService(self.root_folder, ErrorLogging, name)

        bootstrapInstance(EventStub(self.db))

        cx = self.db.open()
        root = cx.root()
        root_folder = root[ZopePublication.root_name]

        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)

        self.assertRaises(NotFoundError, traverse, root_folder,
                          '/++etc++site/default/ErrorLogging')

        self.assert_(IErrorReportingService.providedBy(
            traverse(package, 'Errors')))

        self.assert_(IPrincipalAnnotationService.providedBy(
            traverse(package, 'PrincipalAnnotation')))

        cx.close()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBootstrapSubscriberBase))
    suite.addTest(unittest.makeSuite(TestBootstrapInstance))
    return suite


if __name__ == '__main__':
    unittest.main()
