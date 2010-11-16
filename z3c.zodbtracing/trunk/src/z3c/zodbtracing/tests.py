##############################################################################
#
# Copyright (c) 2005-2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import os, unittest
import ZODB.FileStorage


from ZODB.tests.testFileStorage import FileStorageTests
from z3c.zodbtracing.TracingStorage import TracingStorage

class TracingFileStorageTests(FileStorageTests):
    def open(self, **kwargs):
        #self._storage = ZODB.FileStorage.FileStorage('FileStorageTests.fs',
        #                                             **kwargs)
        self._storage = TracingStorage(
            ZODB.FileStorage.FileStorage('FileStorageTests.fs',
                                                     **kwargs))

#class BaseFileStorageTests(StorageTestBase.StorageTestBase):
#
#    def open(self, **kwargs):
#        self._storage = ZODB.FileStorage.FileStorage('FileStorageTests.fs',
#                                                     **kwargs)
#
#    def setUp(self):
#        self.open(create=1)
#
#    def tearDown(self):
#        self._storage.close()
#        self._storage.cleanup()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TracingFileStorageTests,
                                     prefix="check"))
    return suite

if __name__=='__main__':
    #unittest.main()
    unittest.main(defaultTest='test_suite')
