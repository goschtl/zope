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

$Id: testStartupDirectives.py,v 1.3 2002/10/17 13:31:58 jim Exp $
"""

import unittest, sys, tempfile, os
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from Zope.StartUp.metaConfigure import SiteDefinition
from Zope.Configuration.name import resolve

_fsname = tempfile.mktemp()+'.fs'

class ContextStub:

    def resolve(self, dottedname):
        return resolve(dottedname)


class Test(CleanUp, unittest.TestCase):

    def tearDown(self):

        CleanUp.tearDown(self)

        for ext in '', '.lock', '.index', '.tmp':
            try: os.remove(_fsname + ext)
            except: pass
        

    def _createBlankSiteDefinition(self):
        """ """
        return SiteDefinition('', 'Example Site', 4)
    

    def testStorageMethods(self):
        """ """
        sd = self._createBlankSiteDefinition()
        
        self.assertEqual(sd.useFileStorage(ContextStub(), file=_fsname), [])
        self.assertEqual(sd._zodb._storage.__class__.__name__, 'FileStorage')
        self.assertEqual(sd._zodb._storage._file_name, _fsname)
        sd._zodb.close()

        self.assertEqual(sd.useMappingStorage(ContextStub()), [])
        self.assertEqual(sd._zodb._storage.__class__.__name__,
                         'MappingStorage')


    def testUseLog(self):
        """ """

        sd = self._createBlankSiteDefinition()

        from zLOG.MinimalLogger import _log_dest

        self.assertEqual(sd.useLog(ContextStub()), [])
        self.assertEqual(_log_dest, sys.stderr)

        self.assertEqual(sd.useLog(ContextStub(), _fsname), [])
        from zLOG.MinimalLogger import _log_dest
        self.assertEqual(_log_dest.name, open(_fsname, 'w').name)


    def testAddServer(self):
        """ """

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
        """ """

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

        connection = sd._zodb.open()
        root = connection.root()
        app = root.get(ZopePublication.root_name, None)
        connection.close()
        self.failUnless(IRootFolder.isImplementedBy(app))
        

    
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
