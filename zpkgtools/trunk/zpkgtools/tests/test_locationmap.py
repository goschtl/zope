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

import doctest
import logging
import os.path
import unittest
import urllib

from StringIO import StringIO

from zpkgtools import locationmap
from zpkgtools.tests.test_cvsloader import CvsWorkingDirectoryBase


PREFIX = "cvs://cvs.example.org:ext/cvsroot:"

SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS = """
    # This is a comment.

    zope              %sZope3/src/zope
    zope.app          %sZope3/src/zope/app
    ZConfig           %sPackages/ZConfig
    NotReal           %smodule/something/relative:TAG
    file:README.txt   http://www.example.com/README.txt

    """ % (PREFIX, PREFIX, PREFIX, PREFIX)

SAMPLE_INPUT_WITH_REPOSITORY_URLS = """
    # This is a comment.

    zope             repository:/Zope3/src/zope
    zope.app         repository:/Zope3/src/zope/app
    ZConfig          repository:/Packages/ZConfig
    NotReal          repository:something/relative:TAG
    file:README.txt  http://www.example.com/README.txt

    """

EXPECTED_OUTPUT = {
    "zope":             PREFIX + "Zope3/src/zope",
    "zope.app":         PREFIX + "Zope3/src/zope/app",
    "ZConfig":          PREFIX + "Packages/ZConfig",
    "NotReal":          PREFIX + "module/something/relative:TAG",
    "file:README.txt":  "http://www.example.com/README.txt",
    }

class LoadTestCase(unittest.TestCase):

    def test_load_without_base(self):
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        mapping = locationmap.load(sio)
        self.check_sample_results(mapping)

    def test_load_without_base_update(self):
        # Make sure that an existing mapping is updated, not ignored,
        # and that existing entries are not overridden.
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        d = {"other":   "over-there",
             "ZConfig": "http://www.example.org/"}
        mapping = locationmap.load(sio, mapping=d)
        self.assertEqual(d.pop("other"), "over-there")
        self.assertEqual(d["ZConfig"], "http://www.example.org/")
        # Slam in the expected result, now that we've checked the
        # precedence of the existing entry:
        d["ZConfig"] = EXPECTED_OUTPUT["ZConfig"]
        self.check_sample_results(d)

    def test_load_with_cvs_base(self):
        sio = StringIO(SAMPLE_INPUT_WITH_REPOSITORY_URLS)
        mapping = locationmap.load(
            sio, "cvs://cvs.example.org:ext/cvsroot:module")
        self.check_sample_results(mapping)

    def test_load_with_file_base(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.join(dirname, "input")
        fn = os.path.join(dirname, "packages.map")
        url = "file://" + urllib.pathname2url(fn)
        map = locationmap.fromPathOrUrl(url)
        base = "file://" + urllib.pathname2url(dirname)
        self.assertEqual(map["collection:collection-1"],
                         base + "/collection-1/")
        self.assertEqual(map["collection:collection-2"],
                         base + "/collection-2/")

    def check_sample_results(self, mapping):
        d = {}
        d.update(mapping)
        self.assertEqual(d, EXPECTED_OUTPUT)
        self.failIf("NotThere" in mapping)

    def test_repository_without_cvsbase(self):
        self.check_error("package.module  repository:yeah/right")

    def test_malformed_lines(self):
        self.check_error("package-without-location")
        self.check_error("package location junk")

    def check_error(self, input):
        sio = StringIO(input)
        try:
            locationmap.load(sio)
        except locationmap.MapLoadingError, e:
            self.assertEqual(e.lineno, 1)
        else:
            self.fail("expected MapLoadingError")

    def test_duplicate_entry_generates_warning(self):
        sio = StringIO("r1 cvs://cvs.example.org/cvsroot:foo\n"
                       "r1 cvs://cvs.example.org/cvsroot:foo\n")
        map = self.collect_warnings(locationmap.load, sio)
        self.assertEqual(len(map), 1)
        self.assertEqual(len(self.warnings), 1)
        r = self.warnings[0]
        self.assertEqual(r.levelno, logging.WARNING)
        self.assertEqual(r.name, "zpkgtools.locationmap")

    def collect_warnings(self, callable, *args, **kw):
        self.warnings = []
        handler = CollectingHandler(self.warnings)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        try:
            return callable(*args, **kw)
        finally:
            root_logger.removeHandler(handler)


class CollectingHandler(logging.StreamHandler):
    """Log handler that simply collects emitted warning records."""

    def __init__(self, list):
        self.list = list
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        self.list.append(record)


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
        mapping = locationmap.fromPathOrUrl(self.packages_txt)
        self.assertEqual(mapping, EXPECTED_OUTPUT)

    def test_fromPathOrUrl_passes_mapping(self):
        d = {"other": "over-there"}
        mapping = locationmap.fromPathOrUrl(self.packages_txt, mapping=d)
        self.assertEqual(d.pop("other"), "over-there")
        self.assertEqual(d, EXPECTED_OUTPUT)



def test_suite():
    suite = unittest.makeSuite(LoadTestCase)
    suite.addTest(unittest.makeSuite(CvsWorkingDirectoryTestCase))
    suite.addTest(doctest.DocTestSuite('zpkgtools.locationmap'))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
