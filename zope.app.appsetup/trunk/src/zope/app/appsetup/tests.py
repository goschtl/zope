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
import ZConfig
import os
import sys
import unittest
import urllib
import transaction

import zope.component

from ZODB.tests.util import DB
from zope.testing import doctest
from zope.traversing.api import traverse, getPath
from zope.error.interfaces import IErrorReportingUtility
from zope.error.error import ErrorReportingUtility

from zope.app.component import hooks
from zope.app.component.testing import PlacefulSetup
from zope.app.folder import rootFolder, Folder
from zope.app.folder.interfaces import IRootFolder
from zope.app.publication.zopepublication import ZopePublication
from zope.app.component.site import LocalSiteManager

from zope.app.appsetup.bootstrap import bootStrapSubscriber
from zope.app.appsetup.bootstrap import getInformationFromEvent, \
     ensureObject, ensureUtility

from zope.app.testing import placelesssetup

class EventStub(object):

    def __init__(self, db):
        self.database = db

#
# TODO: some methods from the boostap module are not tested
#

class TestBootstrapSubscriber(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.db = DB()

    def tearDown(self):
        transaction.abort()
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
        self.site_manager = LocalSiteManager(self.root_folder)
        self.root_folder.setSiteManager(self.site_manager)

        sub_folder = Folder()
        self.root_folder["sub_folder"] = sub_folder
        sub_site_manager = LocalSiteManager(sub_folder)
        sub_folder.setSiteManager(sub_site_manager)

        transaction.commit()
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

    def test_ensureUtilityForSubSite(self):
        self.createRFAndSM()

        db, connection, root, root_folder = getInformationFromEvent(
            EventStub(self.db))

        sub_folder = root_folder['sub_folder']
        ensureUtility(sub_folder, IErrorReportingUtility,
                     'ErrorReporting', ErrorReportingUtility,
                     'ErrorReporting', asObject=True)

        # Make sure it was created on the sub folder, not the root folder
        got_utility = zope.component.getUtility(IErrorReportingUtility,
                                                name='ErrorReporting',
                                                context=sub_folder)
        got_path = getPath(got_utility)
        self.assertEquals("/sub_folder/++etc++site/default/ErrorReporting", got_path)

    def test_ensureUtility(self):
        self.createRFAndSM()

        db, connection, root, root_folder = getInformationFromEvent(
            EventStub(self.db))

        # TODO: check EventSub
        root_folder = self.root_folder
        for i in range(2):
            cx = self.db.open()
            utility = ensureUtility(root_folder, IErrorReportingUtility,
                                    'ErrorReporting', ErrorReportingUtility,
                                    'ErrorReporting', asObject=True)
            utility2 = ensureUtility(root_folder, IErrorReportingUtility,
                                     'ErrorReporting2', ErrorReportingUtility,
                                     'ErrorReporting2', asObject=True)
            if utility != None:
                name = utility.__name__
                name2 = utility2.__name__
            else:
                name = None
                name2 = None
            if i == 0:
                self.assertEqual(name, 'ErrorReporting')
                self.assertEqual(name2, 'ErrorReporting2')
            else:
                self.assertEqual(name, None)
                self.assertEqual(name2, None)

            root = cx.root()
            root_folder = root[ZopePublication.root_name]

            package_name = '/++etc++site/default'
            package = traverse(self.root_folder, package_name)

            self.assert_(IErrorReportingUtility.providedBy(
                traverse(package, 'ErrorReporting')))
            self.assert_(IErrorReportingUtility.providedBy(
                traverse(package, 'ErrorReporting2')))
            transaction.commit()

        cx.close()


class TestConfigurationSchema(unittest.TestCase):

    def setUp(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.schema_dir = os.path.join(self.here, "schema")

    def path2url(self, path):
        urlpath = urllib.pathname2url(path)
        while urlpath.startswith("/"):
            urlpath = urlpath[1:]
        return "file:///" + urlpath

    def test_productconfig_xml(self):
        path = os.path.join(self.schema_dir, "productconfig.xml")
        url = self.path2url(path)
        schema = ZConfig.loadSchema(url)

    def test_schema_xml(self):
        path = os.path.join(self.schema_dir, "schema.xml")
        url = self.path2url(path)
        schema = ZConfig.loadSchema(url)


def bootstraptearDown(test):
    test.globs['db'].close()


def setUpDebug(test):
    placelesssetup.setUp(test)
    test.real_stderr = sys.stderr
    test.real_argv = list(sys.argv)
    test.olddir = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), 'testdata'))
    from zope.security.management import endInteraction
    endInteraction()


def tearDownDebug(test):
    sys.stderr = test.real_stderr
    sys.argv[:] = test.real_argv
    if hasattr(sys, 'ps1'):
        del sys.ps1
    os.chdir(test.olddir)
    # make sure we don't leave environment variables that would cause
    # Python to open an interactive console
    if 'PYTHONINSPECT' in os.environ:
        del os.environ['PYTHONINSPECT']
    from zope.security.management import endInteraction
    endInteraction()
    placelesssetup.tearDown(test)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBootstrapSubscriber))
    suite.addTest(unittest.makeSuite(TestConfigurationSchema))
    suite.addTest(doctest.DocTestSuite(
        'zope.app.appsetup.appsetup',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown))
    suite.addTest(doctest.DocFileSuite(
        'bootstrap.txt', 'product.txt',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        ))
    suite.addTest(doctest.DocFileSuite(
        'debug.txt',
        setUp=setUpDebug, tearDown=tearDownDebug,
        ))
    return suite

if __name__ == '__main__':
    unittest.main()
