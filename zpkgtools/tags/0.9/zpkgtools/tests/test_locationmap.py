##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for zpkgtools.cvsmap."""

import doctest
import os.path
import shutil
import tempfile
import unittest
import urllib

from StringIO import StringIO

from zpkgsetup import loggingapi as logging
from zpkgsetup import urlutils

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

EXPECTED_OUTPUT = {
    "zope":             PREFIX + "Zope3/src/zope",
    "zope.app":         PREFIX + "Zope3/src/zope/app",
    "ZConfig":          PREFIX + "Packages/ZConfig",
    "NotReal":          PREFIX + "module/something/relative:TAG",
    "file:README.txt":  "http://www.example.com/README.txt",
    }

class LoadTestCase(unittest.TestCase):

    def setUp(self):
        self.mapping = locationmap.LocationMap()

    def test_subversion_urls_dont_lose_templateness(self):
        url = "svn://svn.example.org/svnroot/proj/tags/*/file.txt"
        sio = StringIO("pkg %s \n" % url)
        locationmap.load(sio, "file:///does/not/exist.map", self.mapping)
        self.assertEqual(self.mapping["pkg"], url)

    def test_load_without_base(self):
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        locationmap.load(sio, "file:///does/not/exist.map", self.mapping)
        self.check_sample_results(self.mapping)

    def test_load_without_base_update(self):
        # Make sure that an existing mapping is updated, not ignored,
        # and that existing entries are not overridden.
        sio = StringIO(SAMPLE_INPUT_WITHOUT_REPOSITORY_URLS)
        d = {"other":   "over-there",
             "ZConfig": "http://www.example.org/"}
        locationmap.load(sio, "file:///does/not/exist.map", d)
        self.assertEqual(d.pop("other"), "over-there")
        self.assertEqual(d["ZConfig"], "http://www.example.org/")
        # Slam in the expected result, now that we've checked the
        # precedence of the existing entry:
        d["ZConfig"] = EXPECTED_OUTPUT["ZConfig"]
        self.check_sample_results(d)

    def test_fromPathOrUrl_with_url(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = os.path.join(dirname, "input")
        fn = os.path.join(dirname, "packages.map")
        url = urlutils.file_url(fn)
        map = locationmap.fromPathOrUrl(url)
        base = urlutils.file_url(dirname)
        self.assertEqual(map["collection:collection-1"],
                         base + "/collection-1/")
        self.assertEqual(map["collection:collection-2"],
                         base + "/collection-2/")

    def test_fromPathOrUrl_with_path(self):
        # create a directory that contains no revision control stuff:
        dirpath = tempfile.mkdtemp()
        # compute paths:
        here = os.path.dirname(os.path.abspath(__file__))
        input = os.path.join(here, "input", "packages.map")
        output = os.path.join(dirpath, "packages.map")
        try:
            # copy in our sample input:
            shutil.copy(input, output)
            # check the map:
            map = locationmap.fromPathOrUrl(output)
            base = urlutils.file_url(dirpath)
            self.assertEqual(map["collection:collection-1"],
                             base + "/collection-1/")
            self.assertEqual(map["collection:collection-2"],
                             base + "/collection-2/")
        finally:
            shutil.rmtree(dirpath)

    def check_sample_results(self, mapping):
        d = {}
        d.update(mapping)
        self.assertEqual(d, EXPECTED_OUTPUT)
        self.failIf("NotThere" in mapping)

    def test_malformed_lines(self):
        self.check_error("package-without-location")
        self.check_error("package location junk")

    def test_malformed_wildcards(self):
        self.check_error("foo* file:///not/really/")
        self.check_error(".* file:///not/really/")
        self.check_error("foo-bar.* file:///not/really/")

    def check_error(self, input):
        sio = StringIO(input)
        try:
            locationmap.load(sio, "file:///does/not/exist.map",
                             self.mapping)
        except locationmap.MapLoadingError, e:
            self.assertEqual(e.lineno, 1)
        else:
            self.fail("expected MapLoadingError")

    def test_duplicate_entry_generates_warning(self):
        self.check_duplicate_entry_generates_warning("r1")
        self.assertEqual(len(self.mapping), 1)

    def test_duplicate_wildcard_generates_warning(self):
        self.check_duplicate_entry_generates_warning("pkg.*")
        # len(self.mapping) == 0, but it's not clear we care at this point;
        # wildcards make the len() pretty questionable

    def check_duplicate_entry_generates_warning(self, resource_name):
        sio = StringIO("%s cvs://cvs.example.org/cvsroot:foo\n"
                       "%s cvs://cvs.example.org/cvsroot:foo\n"
                       % (resource_name, resource_name))
        self.collect_warnings(
            locationmap.load, sio, "file:///does/not/exist.map", self.mapping)
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

    def test_load_with_wildcards(self):
        sio = StringIO("foo.*  cvs://cvs.example.org/cvsroot:foo\n"
                       "bar.*  file:///some/path/\n"
                       "bat.*  some/path\n")

        old_getcwd = os.getcwd
        os.getcwd = lambda: "/home/dudette/python/project"

        try:
            locationmap.load(
                sio, "file:///home/dudette/python/project/", self.mapping)
        finally:
            os.getcwd = old_getcwd

        eq = self.assertEqual
        self.assert_("foo.bar" in self.mapping)
        self.assert_("bar.foo" in self.mapping)
        self.assert_("bat.splat.funk" in self.mapping)
        eq(self.mapping["foo.bar"], "cvs://cvs.example.org/cvsroot:foo/bar")
        eq(self.mapping["bar.foo"], "file:///some/path/foo")
        eq(self.mapping["bat.splat.funk"],
           "file:///home/dudette/python/project/some/path/splat/funk")

    def test_unmatched_wildcard(self):
        sio = StringIO("foo.bar.*  some/path\n")
        locationmap.load(sio, "file:///does/not/exist.map", self.mapping)
        eq = self.assertEqual
        self.assert_("foo" not in self.mapping)
        self.assert_("foo.bar" not in self.mapping)
        self.assert_("foo.bar.bat" in self.mapping)

    def test_invalid_wildcards(self):
        self.check_error("not-a-package.*           some/path \n")
        self.check_error("invalid.wildcard.suffix*  some/path \n")
        self.check_error("invalid.*.wildcard        some/path \n")
        self.check_error("invalid*wildcard          some/path \n")
        self.check_error("*                         some/path \n")
        self.check_error(".*                        some/path \n")

    def test_wildcards_with_subversion_tags(self):
        sio = StringIO("foo.* svn://svn.example.org/proj/tags/*/path\n")
        locationmap.load(sio, "file:///does/not/exist.map", self.mapping)
        self.assertEqual(self.mapping["foo.bar"],
                         "svn://svn.example.org/proj/tags/*/path/bar")

    def test_load_w_relative_paths(self):
        map_file = StringIO('''
          foo     svn+ssh://svn.zope.org/repos/main/Foo/trunk/src/foo
          bar     ../../bar
          baz     baz
          ''')

        old_getcwd = os.getcwd
        os.getcwd = lambda: '/home/dudette/python/project'
        try:
            locationmap.load(map_file, 'http://acme.com/xxx/yyy/',
                             self.mapping)
        finally:
            os.getcwd = old_getcwd

        self.assertEqual(
            self.mapping['foo'],
            'svn+ssh://svn.zope.org/repos/main/Foo/trunk/src/foo')
        self.assertEqual(self.mapping['bar'], 'http://acme.com/bar')
        self.assertEqual(self.mapping['baz'], 'http://acme.com/xxx/yyy/baz')


class CollectingHandler(logging.Handler):
    """Log handler that simply collects emitted warning records."""

    def __init__(self, list):
        self.list = list
        logging.Handler.__init__(self)

    def emit(self, record):
        self.list.append(record)


class LocationMapTestCase(unittest.TestCase):
    """Tests of the convenience mapping used as the CVS mapping storage.

    This doesn't try to test everything about the mapping interface,
    since the class inherits from UserDict; only the aspects that are
    specific to the LocationMap.

    """

    def test_basic_operations(self):
        m = locationmap.LocationMap()
        self.assertEqual(len(m), 0)
        m["foo"] = "value"
        self.assert_("foo" in m)
        self.assert_("foo" in m)
        self.assert_(m.has_key("foo"))
        self.assert_(m.has_key("foo"))
        self.assertEqual(m["foo"], "value")
        self.assertEqual(m["foo"], "value")
        self.assertEqual(len(m), 1)
        m["bar"] = "value"
        self.assert_("bar" in m)
        self.assert_("bar" in m)
        self.assert_(m.has_key("bar"))
        self.assert_(m.has_key("bar"))
        self.assertEqual(m["bar"], "value")
        self.assertEqual(m["bar"], "value")
        self.assertEqual(len(m), 2)
        keys = m.keys()
        keys.sort()
        self.assertEqual(keys, ["bar", "foo"])

    def test_deletions(self):
        m = locationmap.LocationMap()
        m["foo"] = "value"
        m["bar"] = "value"
        del m["bar"]
        self.failIf("bar" in m)
        del m["foo"]
        self.failIf("foo" in m)
        self.assertEqual(len(m), 0)

    def test_pop(self):
        m = locationmap.LocationMap()
        m["foo"] = "value-foo"
        m["bar"] = "value-bar"
        self.assertEqual(m.pop("foo"), "value-foo")
        self.failIf("foo" in m)
        self.assertEqual(m.pop("bar"), "value-bar")
        self.failIf("bar" in m)
        self.assertEqual(m.pop("bar", 42), 42)
        self.failIf("bar" in m)
        self.assertRaises(KeyError, m.pop, "foo")

    def test_update(self):
        m = locationmap.LocationMap()
        m.update({"foo": "value-foo", "bar": "value-bar"})
        self.assertEqual(m["bar"], "value-bar")
        self.assertEqual(m["foo"], "value-foo")
        m.update(bat="value-bat")
        self.assertEqual(m["bat"], "value-bat")
        self.assertEqual(len(m), 3)

    def test_constructor_dict_kwargs(self):
        # construct using both a dict and keywords
        m = locationmap.LocationMap({"foo": 1, "bar": 2}, bat=3)
        self.check_constructor_results(m)

    def test_constructor_dict(self):
        # construct using only a dict
        m = locationmap.LocationMap({"foo": 1,
                                     "bar": 2,
                                     "bat": 3})
        self.check_constructor_results(m)

    def test_constructor_kwargs(self):
        # construct using only keywords
        m = locationmap.LocationMap(foo=1, bar=2, bat=3)
        self.check_constructor_results(m)

    def check_constructor_results(self, m):
        self.assertEqual(len(m), 3)

        self.assert_("foo" in m)
        self.assert_("foo" in m)
        self.assert_(m.has_key("foo"))
        self.assertEqual(m["foo"], 1)

        self.assert_("bar" in m)
        self.assert_(m.has_key("bar"))
        self.assertEqual(m["bar"], 2)

        self.assert_("bat" in m)
        self.assert_(m.has_key("bat"))
        self.assertEqual(m["bat"], 3)


def test_suite():
    suite = unittest.makeSuite(LoadTestCase)
    suite.addTest(unittest.makeSuite(LocationMapTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
