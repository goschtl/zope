##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
from transaction import get_transaction
from ZODB.tests.util import DB
from zope.exceptions import NotFoundError

from zope.app.folder import rootFolder
from zope.app.folder.interfaces import IRootFolder
from zope.app.traversing.api import traverse
from zope.app.errorservice.interfaces import IErrorReportingService
from zope.app.principalannotation.interfaces import IPrincipalAnnotationService
from zope.app.publication.zopepublication import ZopePublication
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.servicenames import ErrorLogging, Utilities
from zope.app.errorservice import ErrorReportingService
from zope.app.traversing.api import traverse
from zope.app.site.service import ServiceManager

from zope.app.appsetup.bootstrap import bootStrapSubscriber
from zope.app.appsetup.bootstrap import addService, configureService, \
     ensureService, getInformationFromEvent, getServiceManager, ensureObject

class EventStub(object):

    def __init__(self, db):
        self.database = db

#
# XXX some methods from the boostap modue are not tested
#

class TestBootstrapSubscriber(PlacefulSetup, unittest.TestCase):

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
        get_transaction().commit()
        cx.close()

    def createRFAndSM(self):
        cx = self.db.open()
        root = cx.root()
        self.root_folder = rootFolder()
        root[ZopePublication.root_name] = self.root_folder
        self.service_manager = ServiceManager(self.root_folder)
        self.root_folder.setSiteManager(self.service_manager)
        get_transaction().commit()
        cx.close()

    def test_notify(self):
        for setup in (lambda: None), self.createRootFolder, self.createRFAndSM:
            setup()
        bootStrapSubscriber(EventStub(self.db))
        cx = self.db.open()
        root = cx.root()
        root_folder = root.get(ZopePublication.root_name, None)
        self.assert_(IRootFolder.providedBy(root_folder))
        package_name = '/++etc++site/default'
        package = traverse(root_folder, package_name)
        cx.close()

    def test_ensureService(self):
        self.createRFAndSM()
        self.createRootFolder()

        db, connection ,root, root_folder = getInformationFromEvent(
            EventStub(self.db))

        # XXX check EventSub
        root_folder = self.root_folder
        service_manager = getServiceManager(root_folder)
        for i in range(2):
            cx = self.db.open()
            name = ensureService(service_manager, root_folder,
                                 ErrorLogging,
                                 ErrorReportingService)
            if i == 0:
                self.assertEqual(name, 'ErrorLogging')
            else:
                self.assertEqual(name, None)

            root = cx.root()
            root_folder = root[ZopePublication.root_name]

            package_name = '/++etc++site/default'
            package = traverse(self.root_folder, package_name)

            self.assert_(IErrorReportingService.providedBy(
                traverse(package, 'ErrorLogging')))
            get_transaction().commit()
            cx.close()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBootstrapSubscriber))
    return suite

if __name__ == '__main__':
    unittest.main()
