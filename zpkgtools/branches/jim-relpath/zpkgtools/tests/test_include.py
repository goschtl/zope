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
"""Tests for the inclusion processor."""

import filecmp
import os
import shutil
import unittest
import urllib2

from os.path import join
from StringIO import StringIO

from zpkgsetup import cfgparser
from zpkgsetup.tests import tempfileapi as tempfile

from zpkgtools import include
from zpkgtools import loader


class InclusionProcessorTestCase(unittest.TestCase):

    def setUp(self):
        self.source = os.path.dirname(__file__)
        self.destination = tempfile.mkdtemp(prefix="test_include_")
        self.loader = loader.Loader()
        self.processor = include.InclusionProcessor(self.loader)
        self.source = os.path.abspath(self.source)
        self.files_written = []
        self.dirs_created = []
        # now create from various revision control systems
        self.create_dir("{arch}")
        self.create_dir("CVS")
        self.create_dir("_darcs")
        self.create_dir(".svn")

    def tearDown(self):
        shutil.rmtree(self.destination)
        for path in self.files_written:
            if os.path.exists(path):
                os.unlink(path)
        for path in self.dirs_created:
            if os.path.exists(path):
                os.rmdir(path)

    def write_file(self, name, text):
        path = join(self.source, name)
        if text and not text[-1:] == "\n":
            text += "\n"
        f = open(path, "w")
        f.write(text)
        f.close()
        self.files_written.append(path)

    def create_dir(self, name, *rest):
        path = join(self.source, name, *rest)
        if not os.path.isdir(path):
            self.dirs_created.insert(0, path)
            os.mkdir(path)

    def test_simple_includespec(self):
        self.write_file(include.PACKAGE_CONF, """\
          <load>
            # Load files from external sources into the collection space:

            foo.html         http://www.python.org/index.html
            doc/whatzit.txt  repository:doc/whatzit.txt
          </load>
          <collection>
            # This is a comment.  It should be ignored.

            # Include ignorethis.txt as newname1.txt and newname2.txt
            # in the distributed collection:
            ignorethis.txt   newname1.txt
            ignorethis.txt   newname2.txt

            runtests.py

            # Another comment.
          </collection>
          <distribution>
            # A comment.

            # Copy the collection's source.txt to the distribution's
            # destination.txt; source.txt will still be included in
            # the distributed collection.
            destination.txt  source.txt
          </distribution>
          """)
        specs = include.load(self.source)
        specs.collection.cook()
        specs.distribution.cook()
        includes = specs.collection.includes
        self.assertEqual(len(includes), 3)
        self.assert_("newname1.txt" in includes)
        self.assert_("newname2.txt" in includes)
        self.assert_("runtests.py" in includes)
        self.assert_(specs.loads)
        self.assert_(specs.collection)
        self.assert_(specs.distribution)
        self.assertEqual(specs.collection.includes["newname1.txt"],
                         "ignorethis.txt")
        self.assertEqual(specs.loads.includes["repository:doc/whatzit.txt"],
                         join("doc", "whatzit.txt"))

    def test_load_disallows_exclusion(self):
        self.write_file(include.PACKAGE_CONF, """\
            <load>
              foobar.txt -
            </load>
            """)
        self.assertRaises(cfgparser.ConfigurationError,
                          include.load, self.source)

    def test_collection_disallows_exclusion_with_inclusion(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              foobar.txt -
              file.txt
            </collection>
            """)
        self.assertRaises(cfgparser.ConfigurationError,
                          include.load, self.source)

    def test_distribution_disallows_exclusion(self):
        self.write_file(include.PACKAGE_CONF, """\
            <distribution>
              foobar.txt -
            </distribution>
            """)
        self.assertRaises(cfgparser.ConfigurationError,
                          include.load, self.source)

    def test_exclusions_saved_in_excludes(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              foobar.txt -
              doc/todo-*.txt -
            </collection>
            """)
        specs = include.load(self.source)
        # These are "uncooked", so wildcards haven't been expanded.
        self.assertEqual(len(specs.collection.excludes), 3)
        self.assert_("foobar.txt" in specs.collection.excludes)
        self.assert_(join("doc", "todo-*.txt") in specs.collection.excludes)
        self.assert_(include.PACKAGE_CONF in specs.collection.excludes)
        # Now populate the source dir:
        self.write_file("foobar.txt", "some text\n")
        docdir = join(self.source, "doc")
        os.mkdir(docdir)
        try:
            self.write_file(join("doc", "todo-1.txt"), "something to do\n")
            self.write_file(join("doc", "todo-2.txt"), "something else\n")
            # And check that cooking finds produces the right thing:
            specs.collection.cook()
            self.assertEqual(len(specs.collection.excludes), 4)
            self.assert_("foobar.txt" in specs.collection.excludes)
            self.assert_("doc/todo-1.txt" in specs.collection.excludes)
            self.assert_("doc/todo-2.txt" in specs.collection.excludes)
            self.assert_(include.PACKAGE_CONF in specs.collection.excludes)
        finally:
            shutil.rmtree(docdir)

    def test_exclusions_with_explicit_package_conf(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              %s -
            </collection>
            """ % include.PACKAGE_CONF)
        specs = include.load(self.source)
        self.assertEqual(len(specs.collection.excludes), 2)
        self.assert_(include.PACKAGE_CONF in specs.collection.excludes)

        # Check the cooked collection:
        specs.collection.cook()
        self.assertEqual(len(specs.collection.excludes), 1)
        self.assert_(include.PACKAGE_CONF in specs.collection.excludes)

    def test_unmatched_wildcards_in_exclusions(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              doc/todo-*.txt -
            </collection>
            """)
        specs = include.load(self.source)
        self.assertRaises(include.InclusionSpecificationError,
                          specs.collection.cook)

    def test_omitted_destination_keeps_name(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              whatzit.txt
            </collection>
            """)
        specs = include.load(self.source)
        self.assert_("whatzit.txt" in specs.collection.includes[None])

    def test_globbing_on_include(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              *.txt
            </collection>
            """)
        specs = include.load(self.source)
        specs.collection.cook()
        specs.distribution.cook()
        self.assertEqual(len(specs.collection.includes), 1)
        self.assert_("ignorethis.txt" in specs.collection.includes)
        self.assert_(not specs.loads)
        self.assert_(specs.collection)
        self.assert_(not specs.distribution)

    def test_disallow_external_reference_in_collection_spec(self):
        self.check_disallow_external_reference_in_spec("collection")

    def test_disallow_external_reference_in_distribution_spec(self):
        self.check_disallow_external_reference_in_spec("distribution")

    def check_disallow_external_reference_in_spec(self, sectionname):
        text = """\
            <%s>
              external.txt  http://example.net/some/where/else.txt
            </%s>
            """ % (sectionname, sectionname)
        self.write_file(include.PACKAGE_CONF, text)
        self.assertRaises(include.InclusionSpecificationError,
                          include.load, self.source)

    # These two tests are really checking internal helpers, but
    # they're a lot more reasonable to express separately from the
    # public API.

    def test_normalize_path(self):
        normalize = include.normalize_path
        self.check_normalize_paths(normalize)

    def test_normalize_path_or_url(self):
        normalize = include.normalize_path_or_url
        self.check_normalize_paths(normalize)
        self.check_normalize_urls(normalize)

    def check_normalize_paths(self, normalize):
        self.assertEqual(normalize("README.txt", "t", "group"),
                         "README.txt")
        self.assertEqual(normalize("doc/README.txt", "t", "group"),
                         join("doc", "README.txt"))
        self.assertEqual(normalize(".", "t", "group"),
                         os.curdir)
        # Ignore this because it looks like a Windows drive letter:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "c:foo/bar", "t", "group")
        # Absolute paths are an error as well:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "/absolute/path", "t", "group")
        # Relative paths that point up the hierarchy are also disallowed:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "abc/../../def.txt", "t", "group")
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "../def.txt", "t", "group")

    def check_normalize_urls(self, normalize):
        for url in ("http://www.example.com/index.html",
                    "repository:/Zope3/doc",
                    "cvs://cvs.zope.com/cvs-repository:/Zope3/doc:HEAD"):
            self.assertEqual(normalize(url, "t", "group"), url)

    def test_createDistributionTree_creates_destination(self):
        os.rmdir(self.destination)
        spec = include.Specification(self.source, "<fake>", "test")
        self.processor.createDistributionTree(self.destination, spec)
        self.assert_(os.path.isdir(self.destination))
        self.assert_(os.path.isfile(join(self.destination, "ignorethis.txt")))

    def test_createDistributionTree(self):
        specs = include.load(self.source)
        specs.collection.cook()
        self.processor.createDistributionTree(self.destination,
                                              specs.collection)
        self.check_file("ignorethis.txt")
        self.check_file("somescript.py")
        self.assert_(not os.path.exists(join(self.destination, "CVS")))
        self.assert_(not os.path.exists(join(self.destination, ".cvsignore")))
        self.assert_(not os.path.exists(join(self.destination, "{arch}")))
        self.assert_(not os.path.exists(join(self.destination, "_darcs")))
        self.assert_(not os.path.exists(join(self.destination, ".svn")))

    def test_createDistributionTree_excludes_file(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              ignorethis.txt  -
            </collection>
            """)
        specs = include.load(self.source)
        specs.collection.cook()
        self.processor.createDistributionTree(self.destination,
                                              specs.collection)
        self.check_file("somescript.py")
        ignorethis_txt = join(self.destination, "ignorethis.txt")
        self.assert_(not os.path.exists(ignorethis_txt))

    def test_createDistributionTree_excludes_directory(self):
        self.write_file(include.PACKAGE_CONF, """\
            <collection>
              foo/bar -
            </collection>
            """)
        specs = include.load(self.source)
        foodir = join(self.source, "foo")
        os.mkdir(foodir)
        try:
            os.mkdir(join(foodir, "bar"))
            self.write_file(join("foo", "bar.txt"), "some text\n")
            specs.collection.cook()
            self.processor.createDistributionTree(self.destination,
                                                  specs.collection)
            self.assert_(os.path.isdir(join(self.destination, "foo")))
            self.assert_(
                not os.path.isdir(join(self.destination, "foo", "bar")))
            self.assert_(
                os.path.isfile(join(self.destination, "foo", "bar.txt")))
        finally:
            shutil.rmtree(foodir)

    def test_createDistributionTree_nested_excludes(self):
        self.source = os.path.join(self.source, "input", "collection-1")
        specs = include.load(self.source)
        specs.collection.cook()
        self.processor.createDistributionTree(self.destination,
                                              specs.collection)
        implied = os.path.join(self.destination, "implied")
        self.assert_(os.path.isdir(implied))
        self.failIf(os.path.exists(os.path.join(implied, "dropped.txt")))

    def test_createDistributionTree_nested_includes(self):
        self.write_file(os.path.join("input", "package", include.PACKAGE_CONF),
                        "<collection>\n"
                        "  something.py __init__.py\n"
                        "</collection>\n")
        specs = include.load(self.source)
        specs.collection.cook()
        self.processor.createDistributionTree(self.destination,
                                              specs.collection)
        destdir = os.path.join(self.destination, "input", "package")
        self.assert_(os.path.isfile(os.path.join(destdir, "something.py")))
        self.failIf(os.path.exists(os.path.join(destdir, "__init__.py")))

    def test_nested_loads_disallowed(self):
        self.write_file(os.path.join("input", "package", include.PACKAGE_CONF),
                        "<load>\n"
                        "  something.py http://www.example.org/\n"
                        "</load>\n")
        specs = include.load(self.source)
        specs.collection.cook()
        self.assertRaises(include.InclusionSpecificationError,
                          self.processor.createDistributionTree,
                          self.destination, specs.collection)

    def test_package_conf_processed_in_inclusion(self):
        # There's an edge case when a directory is included explicity
        # by a parent, but includes a PACKAGE_CONF file itself; at one
        # point, the nested PACKAGE_CONF wasn't being processed.  This
        # test guards against a regression for that case.
        self.source = os.path.join(self.source, "input", "collection-2")
        specs = include.load(self.source)
        specs.collection.cook()
        self.processor.createDistributionTree(self.destination,
                                              specs.collection)
        included = os.path.join(self.destination, "included")
        self.assert_(os.path.isdir(included))
        self.failIf(os.path.exists(os.path.join(included, "dropped.txt")))

    def check_file(self, name):
        srcname = join(self.source, name)
        destname = join(self.destination, name)
        self.assert_(os.path.isfile(destname))
        srcstat = os.stat(srcname)
        deststat = os.stat(destname)
        self.assertEqual(srcstat.st_mode, deststat.st_mode)
        self.assertEqual(srcstat.st_mtime, deststat.st_mtime)
        self.assertEqual(srcstat.st_atime, deststat.st_atime)

    def test_including_from_cvs_url(self):
        self.start_including_from_cvs_url()
        URL = "cvs://anonymous@cvs.zope.org:pserver/cvs-repository:Zope3"
        self.processor.addSingleInclude("somedir", URL, self.destination,
                                        self.source)
        url, = self.args[0]
        self.assertEqual(url, URL)
        path, dest = self.args[1]
        self.assertEqual(path, self.return_path)

    def test_including_from_cvs_url_without_base(self):
        self.start_including_from_cvs_url()
        URL = "cvs://anonymous@cvs.zope.org:pserver/cvs-repository:Zope3"
        self.processor.addSingleInclude("somedir", URL, self.destination,
                                        self.source)
        url, = self.args[0]
        self.assertEqual(url, URL)
        path, dest = self.args[1]
        self.assertEqual(path, self.return_path)

    def start_including_from_cvs_url(self):
        # We just want to make sure the loader and processor get
        # called with the right stuff:
        self.loader.load_cvs = self.save_args
        self.processor.includeFromLocalTree = self.save_args
        self.args = []

    return_path = "/tmp/junk-42"

    def save_args(self, *args):
        self.args.append(args)
        self.loader.add_working_dir(args[0], None, self.return_path, False)
        return self.return_path

    def test_including_from_repository_url_without_base(self):
        # When using a repository: URL, there must be a base cvs: URL
        # for the InclusionProcessor.
        self.assertRaises(include.InclusionError,
                          self.processor.addSingleInclude,
                          "somedir",
                          "repository:somedir:TAG",
                          self.destination,
                          self.source)

    def test_including_from_url(self):
        URL = "http://www.example.org/"
        old_urlopen = urllib2.urlopen
        self.called = False
        def my_urlopen(url):
            self.assertEqual(url, URL)
            self.called = True
            return StringIO("my_urlopen_data\n")
        urllib2.urlopen = my_urlopen
        try:
            self.processor.addSingleInclude("somefile.txt",
                                            URL,
                                            self.destination,
                                            self.source)
        finally:
            urllib2.urlopen = old_urlopen
        self.assert_(self.called)
        resultfile = join(self.destination, "somefile.txt")
        self.assert_(os.path.isfile(resultfile))
        f = open(resultfile, "rU")
        text = f.read()
        f.close()
        self.assertEqual(text, "my_urlopen_data\n")

    def test_including_from_file(self):
        # This also tests the automatic creation of a required output
        # directory.
        FILENAME = "ignorethis.txt"
        self.processor.addSingleInclude("foo/splat.txt",
                                        FILENAME,
                                        self.destination,
                                        self.source)
        sourcefile = join(self.source, FILENAME)
        resultfile = join(self.destination, "foo", "splat.txt")
        self.assert_(os.path.isfile(resultfile))
        self.assert_(filecmp.cmp(resultfile, sourcefile, shallow=False))


def test_suite():
    return unittest.makeSuite(InclusionProcessorTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
