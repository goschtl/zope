##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Tests of ZConfig.loader classes and helper functions."""

import os.path
import sys
import tempfile
import unittest
import urllib2

from StringIO import StringIO

import ZConfig
import ZConfig.loader
import ZConfig.url

from ZConfig.tests.test_config import CONFIG_BASE


try:
    myfile = __file__
except NameError:
    myfile = sys.argv[0]

myfile = os.path.abspath(myfile)
LIBRARY_DIR = os.path.join(os.path.dirname(myfile), "library")


class LoaderTestCase(unittest.TestCase):

    def test_schema_caching(self):
        loader = ZConfig.loader.SchemaLoader()
        url = ZConfig.url.urljoin(CONFIG_BASE, "simple.xml")
        schema1 = loader.loadURL(url)
        schema2 = loader.loadURL(url)
        self.assert_(schema1 is schema2)

    def test_simple_import_with_cache(self):
        loader = ZConfig.loader.SchemaLoader()
        url1 = ZConfig.url.urljoin(CONFIG_BASE, "library.xml")
        schema1 = loader.loadURL(url1)
        sio = StringIO("<schema>"
                       "  <import src='library.xml'/>"
                       "  <section type='type-a' name='section'/>"
                       "</schema>")
        url2 = ZConfig.url.urljoin(CONFIG_BASE, "stringio")
        schema2 = loader.loadFile(sio, url2)
        self.assert_(schema1.gettype("type-a") is schema2.gettype("type-a"))

    def test_import_errors(self):
        # must specify exactly one of package or src
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema><import/></schema>"))
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema>"
                                   "  <import src='library.xml'"
                                   "          package='ZConfig'/>"
                                   "</schema>"))

    def test_import_from_package(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget'/>"
                       "</schema>")
        schema = loader.loadFile(sio)
        self.assert_(schema.gettype("widget-a") is not None)

    def test_import_from_package_extended(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.thing'/>"
                       "  <section name='*' type='thing' attribute='thing'/>"
                       "</schema>")
        schema = loader.loadFile(sio)
        schema.gettype("thing")
        schema.gettype("thing-a")
        schema.gettype("thing-b")
        schema.gettype("thing-ext")

        # Make sure the extension is wired in properly:
        sio = StringIO("<thing-ext thing/>")
        conf, handlers = ZConfig.loadConfigFile(schema, sio)
        self.assertEqual(conf.thing.thing_ext_key, "thing-ext-default")

    def test_urlsplit_urlunsplit(self):
        # Extracted from Python's test.test_urlparse module:
        for url, parsed, split in [
            ('http://www.python.org',
             ('http', 'www.python.org', '', '', '', ''),
             ('http', 'www.python.org', '', '', '')),
            ('http://www.python.org#abc',
             ('http', 'www.python.org', '', '', '', 'abc'),
             ('http', 'www.python.org', '', '', 'abc')),
            ('http://www.python.org/#abc',
             ('http', 'www.python.org', '/', '', '', 'abc'),
             ('http', 'www.python.org', '/', '', 'abc')),
            ("http://a/b/c/d;p?q#f",
             ('http', 'a', '/b/c/d', 'p', 'q', 'f'),
             ('http', 'a', '/b/c/d;p', 'q', 'f')),
            ('file:///tmp/junk.txt',
             ('file', '', '/tmp/junk.txt', '', '', ''),
             ('file', '', '/tmp/junk.txt', '', '')),
            ]:
            result = ZConfig.url.urlsplit(url)
            self.assertEqual(result, split)
            result2 = ZConfig.url.urlunsplit(result)
            self.assertEqual(result2, url)

    def test_file_url_normalization(self):
        self.assertEqual(
            ZConfig.url.urlnormalize("file:/abc/def"),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urlunsplit(("file", "", "/abc/def", "", "")),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urljoin("file:/abc/", "def"),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urldefrag("file:/abc/def#frag"),
            ("file:///abc/def", "frag"))

class TestNonExistentResources(unittest.TestCase):

    # XXX Not sure if this is the best approach for these.  These
    # tests make sure that the error reported by ZConfig for missing
    # resources is handled in a consistent way.  Since ZConfig uses
    # urllib2.urlopen() for opening all resources, what we do is
    # replace that function with one that always raises an exception.
    # Since urllib2.urlopen() can raise either IOError or OSError
    # (depending on the version of Python), we run test for each
    # exception.  urllib2.urlopen() is restored after running the
    # test.

    def setUp(self):
        self.urllib2_urlopen = urllib2.urlopen
        urllib2.urlopen = self.fake_urlopen

    def tearDown(self):
        urllib2.urlopen = self.urllib2_urlopen

    def fake_urlopen(self, url):
        raise self.error()

    def test_nonexistent_file_ioerror(self):
        self.error = IOError
        self.check_nonexistent_file()

    def test_nonexistent_file_oserror(self):
        self.error = OSError
        self.check_nonexistent_file()

    def check_nonexistent_file(self):
        fn = tempfile.mktemp()
        schema = ZConfig.loadSchemaFile(StringIO("<schema/>"))
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadSchema, fn)
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfig, schema, fn)
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfigFile, schema,
                          StringIO("%include " + fn))
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadSchema,
                          "http://www.zope.org/no-such-document/")
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfig, schema,
                          "http://www.zope.org/no-such-document/")


def test_suite():
    suite = unittest.makeSuite(LoaderTestCase)
    suite.addTest(unittest.makeSuite(TestNonExistentResources))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
