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

$Id: testStartupDirectives.py,v 1.6 2002/12/20 19:52:57 jeremy Exp $
"""

import unittest, sys, tempfile, os
import logging

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
     PlacefulSetup
from Zope.App.StartUp.metaConfigure import SiteDefinition
from Zope.Configuration.name import resolve
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

_fsname = tempfile.mktemp()+'.fs'

class ContextStub:

    def resolve(self, dottedname):
        return resolve(dottedname)


class Test(PlacefulSetup, unittest.TestCase):

    def tearDown(self):

        PlacefulSetup.tearDown(self)

        for ext in '', '.lock', '.index', '.tmp':
            try: os.remove(_fsname + ext)
            except: pass


    def _createBlankSiteDefinition(self):
        return SiteDefinition('', 'Example Site', 4)


    def testStorageMethods(self):
        sd = self._createBlankSiteDefinition()

        self.assertEqual(sd.useFileStorage(ContextStub(), file=_fsname), [])
        self.assertEqual(sd._zodb._storage.__class__.__name__, 'FileStorage')
        self.assertEqual(sd._zodb._storage._file_name, _fsname)
        sd.close()

        self.assertEqual(sd.useMappingStorage(ContextStub()), [])
        self.assertEqual(sd._zodb._storage.__class__.__name__,
                         'MappingStorage')
        sd.close()


    def testUseLog(self):
        sd = self._createBlankSiteDefinition()

        self.assertEqual(sd.useLog(ContextStub()), [])
        for h in logging.root.handlers:
            if isinstance(h, logging.StreamHandler):
                if h.stream is sys.stderr:
                    break
        else:
            self.fail("Not logging to sys.stderr")

        self.assertEqual(sd.useLog(ContextStub(), _fsname), [])
        for h in logging.root.handlers:
            if isinstance(h, logging.FileHandler):
                if h.baseFilename == _fsname:
                    break
        else:
            self.fail("Not logging to _fsname")


    def testAddServer(self):
        sd = self._createBlankSiteDefinition()

        from Zope.Configuration.Action import Action

        self.assertEqual(sd.addServer(ContextStub(), 'Browser',
                                      '8081', 'true'), [])
        self.assertEqual(len(sd._servers), 1)
        self.assertEqual(sd._servers.keys(), ['Browser'])

        server_info = sd._servers['Browser']
        self.assertEqual(server_info['port'], 8081)
        self.assertEqual(server_info['verbose'], 1)

    def testInitDB(self):
        sd = self._createBlankSiteDefinition()

        from Zope.App.OFS.Content.Folder.RootFolder import IRootFolder
        from Zope.App.ZopePublication.ZopePublication import ZopePublication

        sd.useFileStorage(ContextStub(), file=_fsname)

        connection = sd._zodb.open()
        root = connection.root()
        app = root.get(ZopePublication.root_name, None)
        connection.close()
        self.assertEqual(app, None)

        sd._initDB()

        try:
            connection = sd._zodb.open()
            root = connection.root()
            app = root.get(ZopePublication.root_name, None)
            connection.close()
            self.failUnless(IRootFolder.isImplementedBy(app))
        finally:
            sd.close()

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
