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
"""Tests for the zpkgtools.loader module."""

import os
import shutil
import tempfile
import unittest

from zpkgtools import loader


class LoaderTestBase(unittest.TestCase):

    def setUp(self):
        self.workingdir = tempfile.mkdtemp(prefix="test-workdir-")
        self.cvsdir = os.path.join(self.workingdir, "CVS")
        os.mkdir(self.cvsdir)

    def tearDown(self):
        shutil.rmtree(self.workingdir)


class DummyLoader:

    cleanup_called = False

    def cleanup(self):
        self.cleanup_called += 1


class FileProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = DummyLoader()
        self.mode = "rU"
        self.fp = loader.FileProxy(__file__, self.mode, self.loader)

    def tearDown(self):
        self.fp.close()

    def test_close(self):
        self.fp.close()
        self.assertEqual(self.loader.cleanup_called, 1)
        self.assert_(self.fp.closed)
        self.fp.close()
        self.assertEqual(self.loader.cleanup_called, 1)
        self.assert_(self.fp.closed)

    def test_softspace(self):
        self.failIf(self.fp.softspace)
        self.fp.softspace = 1
        self.assertEqual(self.fp.softspace, 1)
        self.fp.softspace = 2
        self.assertEqual(self.fp.softspace, 2)
        self.assertRaises(TypeError, setattr, self.fp, "softspace", "12")
        # XXX a little white box, to make sure softspace is passed to
        # the underlying file object:
        self.assertEqual(self.fp._file.softspace, 2)

    def test_read(self):
        text = self.fp.read()
        expected = open(__file__, self.mode).read()
        self.assertEqual(text, expected)

    def test_url_as_name(self):
        # make sure the path is used by default:
        self.assertEqual(self.fp.name, __file__)
        # now 
        fp = loader.FileProxy(__file__, self.mode, self.loader, "fake:url")
        try:
            self.assertEqual(fp.name, "fake:url")
        finally:
            fp.close()


def test_suite():
    suite = unittest.makeSuite(FileProxyTestCase)
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
