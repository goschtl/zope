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
"""Tests for the inclusion processor."""

import filecmp
import os
import shutil
import tempfile
import unittest
import urllib2

from os.path import join
from StringIO import StringIO

from zpkgtools import include
from zpkgtools import loader


class InclusionProcessorTestCase(unittest.TestCase):

    def setUp(self):
        self.source = os.path.dirname(__file__)
        self.destination = tempfile.mkdtemp(prefix="test_include_")
        self.loader = loader.Loader()
        self.processor = include.InclusionProcessor(self.source, self.loader)
        self.source = os.path.abspath(self.source)
        self.files_written = []

    def tearDown(self):
        shutil.rmtree(self.destination)
        for path in self.files_written:
            if os.path.exists(path):
                os.unlink(path)

    def write_file(self, name, text):
        path = join(self.source, name)
        if text and not text[-1:] == "\n":
            text += "\n"
        f = open(path, "w")
        f.write(text)
        f.close()
        self.files_written.append(path)

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
        includes = specs.collection.includes
        self.assertEqual(len(includes), 3)
        self.assert_("newname1.txt" in includes)
        self.assert_("newname2.txt" in includes)
        self.assert_("runtests.py" in includes)
        self.assertEqual(specs.collection.includes["newname1.txt"],
                         "ignorethis.txt")
        self.assertEqual(specs.loads.includes["repository:doc/whatzit.txt"],
                         join("doc", "whatzit.txt"))

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
        self.assertEqual(len(specs.collection.includes), 1)
        self.assert_("ignorethis.txt" in specs.collection.includes)

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
        INCLUDES = "INCLUDES.txt"
        self.assertEqual(normalize("README.txt", "t", "group"),
                         "README.txt")
        self.assertEqual(normalize("doc/README.txt", "t", "group"),
                         join("doc", "README.txt"))
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
        INCLUDES = "INCLUDES.txt"
        for url in ("http://www.example.com/index.html",
                    "repository:/Zope3/doc",
                    "cvs://cvs.zope.com/cvs-repository:/Zope3/doc:HEAD"):
            self.assertEqual(normalize(url, "t", "group"), url)

    def test_createDistributionTree_creates_destination(self):
        os.rmdir(self.destination)
        self.processor.createDistributionTree(self.destination)
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
        self.processor.addSingleInclude("somedir", URL, self.destination)
        url, = self.args[0]
        self.assertEqual(url, URL)
        path, dest = self.args[1]
        self.assertEqual(path, self.return_path)

    def test_including_from_cvs_url_without_base(self):
        self.start_including_from_cvs_url()
        URL = "cvs://anonymous@cvs.zope.org:pserver/cvs-repository:Zope3"
        self.processor.addSingleInclude("somedir", URL, self.destination)
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
                          self.destination)

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
                                            self.destination)
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
                                        self.destination)
        sourcefile = join(self.source, FILENAME)
        resultfile = join(self.destination, "foo", "splat.txt")
        self.assert_(os.path.isfile(resultfile))
        self.assert_(filecmp.cmp(resultfile, sourcefile, shallow=False))


def test_suite():
    return unittest.makeSuite(InclusionProcessorTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
