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
"""Tests for zpkgtools.cvsmap."""

import os.path
import unittest

from StringIO import StringIO

from zpkgtools import cvsmap
from zpkgtools.tests.test_cvsloader import CvsWorkingDirectoryBase


PREFIX = "cvs://cvs.example.org:ext/cvsroot:"

SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS = """
    # This is a comment.

    zope         %sZope3/src/zope
    zope.app     %sZope3/src/zope/app
    ZConfig      %sPackages/ZConfig
    NotReal      %smodule/something/relative:TAG
    README.txt   http://www.example.com/README.txt

    """ % (PREFIX, PREFIX, PREFIX, PREFIX)

SAMPLE_INPUT_WITH_REPOSITORY_URLS = """
    # This is a comment.

    zope         repository:/Zope3/src/zope
    zope.app     repository:/Zope3/src/zope/app
    ZConfig      repository:/Packages/ZConfig
    NotReal      repository:something/relative:TAG
    README.txt   http://www.example.com/README.txt

    """

EXPECTED_OUTPUT = {
    "zope":      PREFIX + "Zope3/src/zope",
    "zope.app":  PREFIX + "Zope3/src/zope/app",
    "ZConfig":   PREFIX + "Packages/ZConfig",
    "NotReal":   PREFIX + "module/something/relative:TAG",
    "README.txt":"http://www.example.com/README.txt",
    }

class CvsMapTestCase(unittest.TestCase):

    def test_load_without_base(self):
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        mapping = cvsmap.load(sio)
        self.check_sample_results(mapping)

    def test_load_without_base_update(self):
        # Make sure that an existing mapping is updated, not ignored,
        # and that existing entries are not overridden.
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        d = {"other":   "over-there",
             "ZConfig": "http://www.example.org/"}
        mapping = cvsmap.load(sio, mapping=d)
        self.assertEqual(d.pop("other"), "over-there")
        self.assertEqual(d["ZConfig"], "http://www.example.org/")
        # Slam in the expected result, now that we've checked the
        # precedence of the existing entry:
        d["ZConfig"] = EXPECTED_OUTPUT["ZConfig"]
        self.check_sample_results(d)

    def test_load_with_cvs_base(self):
        sio = StringIO(SAMPLE_INPUT_WITH_REPOSITORY_URLS)
        mapping = cvsmap.load(sio, "cvs://cvs.example.org:ext/cvsroot:module")
        self.check_sample_results(mapping)

    def check_sample_results(self, mapping):
        d = {}
        d.update(mapping)
        self.assertEqual(d, EXPECTED_OUTPUT)
        self.assert_("NotThere" not in mapping)

    def test_repository_without_cvsbase(self):
        self.check_error("package.module  repository:yeah/right")

    def test_malformed_lines(self):
        self.check_error("package-without-location")
        self.check_error("package location junk")

    def check_error(self, input):
        sio = StringIO(input)
        try:
            cvsmap.load(sio)
        except cvsmap.CvsMapLoadingError, e:
            self.assertEqual(e.lineno, 1)
        else:
            self.fail("expected CvsMapLoadingError")


class CvsWorkingDirectoryTestCase(CvsWorkingDirectoryBase):
    """Tests that rely on a CVS working directory."""

    def setUp(self):
        super(CvsWorkingDirectoryTestCase, self).setUp()
        self.initialize(":ext:cvs.example.org:/cvsroot", "module")
        self.packages_txt = os.path.join(self.workingdir, "PACKAGES.txt")
        f = open(self.packages_txt, "w")
        f.write(SAMPLE_INPUT_WITH_REPOSITORY_URLS)
        f.close()

    def test_fromPathOrUrl_from_cvs_workdir(self):
        mapping = cvsmap.fromPathOrUrl(self.packages_txt)
        self.assertEqual(mapping, EXPECTED_OUTPUT)

    def test_fromPathOrUrl_passes_mapping(self):
        d = {"other": "over-there"}
        mapping = cvsmap.fromPathOrUrl(self.packages_txt, mapping=d)
        self.assertEqual(d.pop("other"), "over-there")
        self.assertEqual(d, EXPECTED_OUTPUT)


def test_suite():
    suite = unittest.makeSuite(CvsMapTestCase)
    suite.addTest(unittest.makeSuite(CvsWorkingDirectoryTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
