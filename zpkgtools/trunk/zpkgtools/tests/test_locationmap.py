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
    "package:zope":     PREFIX + "Zope3/src/zope",
    "package:zope.app": PREFIX + "Zope3/src/zope/app",
    "package:ZConfig":  PREFIX + "Packages/ZConfig",
    "package:NotReal":  PREFIX + "module/something/relative:TAG",
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
        d = {"package:other":   "over-there",
             "package:ZConfig": "http://www.example.org/"}
        mapping = locationmap.load(sio, mapping=d)
        self.assertEqual(d.pop("package:other"), "over-there")
        self.assertEqual(d["package:ZConfig"], "http://www.example.org/")
        # Slam in the expected result, now that we've checked the
        # precedence of the existing entry:
        d["package:ZConfig"] = EXPECTED_OUTPUT["package:ZConfig"]
        self.check_sample_results(d)

    def test_load_with_cvs_base(self):
        sio = StringIO(SAMPLE_INPUT_WITH_REPOSITORY_URLS)
        mapping = locationmap.load(
            sio, "cvs://cvs.example.org:ext/cvsroot:module")
        self.check_sample_results(mapping)

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
        d = {"package:other": "over-there"}
        mapping = locationmap.fromPathOrUrl(self.packages_txt, mapping=d)
        self.assertEqual(d.pop("package:other"), "over-there")
        self.assertEqual(d, EXPECTED_OUTPUT)


class LocationMapTestCase(unittest.TestCase):
    """Tests of the convenience mapping used as the CVS mapping storage.

    This doesn't try to test everything about the mapping interface,
    since the class inherits from UserDict; only the aspects that are
    specific to the LocationMap.

    """

    def test_basic_operations(self):
        m = locationmap.LocationMap()
        self.assertEqual(len(m), 0)
        m["package:foo"] = "value"
        self.assert_("package:foo" in m)
        self.assert_("foo" in m)
        self.assert_(m.has_key("package:foo"))
        self.assert_(m.has_key("foo"))
        self.assertEqual(m["package:foo"], "value")
        self.assertEqual(m["foo"], "value")
        self.assertEqual(len(m), 1)
        m["bar"] = "value"
        self.assert_("package:bar" in m)
        self.assert_("bar" in m)
        self.assert_(m.has_key("package:bar"))
        self.assert_(m.has_key("bar"))
        self.assertEqual(m["package:bar"], "value")
        self.assertEqual(m["bar"], "value")
        self.assertEqual(len(m), 2)
        keys = m.keys()
        keys.sort()
        self.assertEqual(keys, ["package:bar", "package:foo"])

    def test_deletions(self):
        m = locationmap.LocationMap()
        m["foo"] = "value"
        m["bar"] = "value"
        del m["package:bar"]
        self.failIf("bar" in m)
        self.failIf("package:bar" in m)
        del m["foo"]
        self.failIf("foo" in m)
        self.failIf("package:foo" in m)
        self.assertEqual(len(m), 0)

    def test_pop(self):
        m = locationmap.LocationMap()
        m["foo"] = "value-foo"
        m["bar"] = "value-bar"
        self.assertEqual(m.pop("foo"), "value-foo")
        self.failIf("foo" in m)
        self.failIf("package:foo" in m)
        self.assertEqual(m.pop("package:bar"), "value-bar")
        self.failIf("bar" in m)
        self.failIf("package:bar" in m)
        self.assertEqual(m.pop("bar", 42), 42)
        self.assertEqual(m.pop("package:bar", 42), 42)
        self.failIf("bar" in m)
        self.failIf("package:bar" in m)
        self.assertRaises(KeyError, m.pop, "foo")
        self.assertRaises(KeyError, m.pop, "package:foo")

    def test_update(self):
        m = locationmap.LocationMap()
        m.update({"foo": "value-foo", "package:bar": "value-bar"})
        self.assertEqual(m["package:bar"], "value-bar")
        self.assertEqual(m["package:foo"], "value-foo")
        self.assertEqual(m["bar"], "value-bar")
        self.assertEqual(m["foo"], "value-foo")
        m.update(bat="value-bat")
        self.assertEqual(m["package:bat"], "value-bat")
        self.assertEqual(m["bat"], "value-bat")
        self.assertEqual(len(m), 3)

    def test_constructor_dict_kwargs(self):
        # construct using both a dict and keywords
        m = locationmap.LocationMap({"foo": 1, "package:bar": 2}, bat=3)
        self.check_constructor_results(m)

    def test_constructor_dict(self):
        # construct using only a dict
        m = locationmap.LocationMap({"foo": 1,
                                     "package:bar": 2,
                                     "bat": 3})
        self.check_constructor_results(m)

    def test_constructor_kwargs(self):
        # construct using only keywords
        m = locationmap.LocationMap(foo=1, bar=2, bat=3)
        self.check_constructor_results(m)

    def check_constructor_results(self, m):
        self.assertEqual(len(m), 3)

        self.assert_("package:foo" in m)
        self.assert_("foo" in m)
        self.assert_(m.has_key("package:foo"))
        self.assert_(m.has_key("foo"))
        self.assertEqual(m["package:foo"], 1)
        self.assertEqual(m["foo"], 1)

        self.assert_("package:bar" in m)
        self.assert_("bar" in m)
        self.assert_(m.has_key("package:bar"))
        self.assert_(m.has_key("bar"))
        self.assertEqual(m["package:bar"], 2)
        self.assertEqual(m["bar"], 2)

        self.assert_("package:bat" in m)
        self.assert_("bat" in m)
        self.assert_(m.has_key("package:bat"))
        self.assert_(m.has_key("bat"))
        self.assertEqual(m["package:bat"], 3)
        self.assertEqual(m["bat"], 3)


def test_normalizeResourceId():
    """The normalizeResourceId() function ensures the default resource
    type is handled consistently.

    >>> locationmap.normalizeResourceId('package:foo')
    'package:foo'
    >>> locationmap.normalizeResourceId('foo')
    'package:foo'
    >>> locationmap.normalizeResourceId('collection:foo')
    'collection:foo'

    There's a weird case when the type prefix is empty:

    >>> locationmap.normalizeResourceId(':foo')
    ':foo'
    """


def test_suite():
    suite = unittest.makeSuite(LoadTestCase)
    suite.addTest(unittest.makeSuite(CvsWorkingDirectoryTestCase))
    suite.addTest(unittest.makeSuite(LocationMapTestCase))
    suite.addTest(doctest.DocTestSuite())
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
