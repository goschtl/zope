##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests of the filesystem side of the bundle management code.

$Id$
"""

import os
import shutil
import sys
import unittest

from cStringIO import StringIO

from zope.fssync.fsutil import Error
from zope.app.fssync.fsbundle import FSBundle, parseBundleVersion


try:
    from tempfile import mkdtemp
except ImportError:
    # Define a (limited) version of mkdtemp() for compatibility:
    import tempfile
    def mkdtemp(suffix=""):
        fn = tempfile.mktemp(suffix)
        fn = os.path.realpath(fn)
        os.mkdir(fn, 0700)
        return fn


class FSBundleTestCase(unittest.TestCase):

    def setUp(self):
        self.fsbundle = FSBundle()
        self.metadata = self.fsbundle.metadata
        self.sync = self.fsbundle.sync
        self.tmpdir = mkdtemp("-fssync")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # helper functions

    def create_site(self):
        for dirparts in [("@@Zope",),
                         ("++etc++site",),
                         ("++etc++site", "site-folder"),
                         ]:
            dn = os.path.join(self.tmpdir, *dirparts)
            os.mkdir(dn)
        self.etcdir = os.path.join(self.tmpdir, "++etc++site")
        self.write_text(
            "http://gandalf@localhost:8080/++etc++site\n",
            "@@Zope", "Root")
        self.add_metadata(
            self.etcdir,
            path="/++etc++site",
            type="zope.app.component.site.LocalSiteManager",
            factory="zope.app.component.site.LocalSiteManager")
        self.add_metadata(
            os.path.join(self.etcdir, "site-folder"),
            path="/++etc++site/site-folder",
            type="zope.app.component.site.SiteManagementFolder",
            factory="zope.app.component.site.SiteManagementFolder")
        self.metadata.flush()

    def add_metadata(self, name, **kw):
        d = self.metadata.getentry(name)
        d.update(kw)

    def write_text(self, text, *nameparts):
        fn = os.path.join(self.tmpdir, *nameparts)
        f = open(fn, "w")
        try:
            f.write(text)
        finally:
            f.close()

    def quiet_call(self, func, *args, **kw):
        """Call a function, dropping stdout to avoid console spewage."""
        sio = StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = sio
            return func(*args, **kw)
        finally:
            sys.stdout = old_stdout

    def make_bundle(self, type=None, factory=None):
        source = os.path.join(self.etcdir, "site-folder")
        target = os.path.join(self.etcdir, "bundle-1.0.0")
        self.quiet_call(self.fsbundle.create, target, type, factory, source)
        return source, target

    # tests

    def test_simple_create(self):
        self.create_site()
        source, target = self.make_bundle()
        # Now poke at the new bundle and make sure we got everything
        # right:
        sm = self.metadata.getentry(source)
        tm = self.metadata.getentry(target)
        self.assertEqual(tm["path"], "/++etc++site/bundle-1.0.0")
        bundle_type = tm["type"]
        bundle_factory = tm["factory"]
        self.assert_(bundle_type != sm["type"])
        self.assert_(bundle_factory != sm["factory"])
        self.assertEqual(self.metadata.getnames(target), [])
        # Make sure a second call won't clobber the existing bundle:
        # add content to original so we can check that it didn't get copied:
        self.write_text("# Dummy Python module.\n"
                        "1/0\n",
                        "++etc++site", "site-folder", "dummy.py")
        self.add_metadata(os.path.join(self.etcdir, "site-folder", "dummy.py"),
                          path="/++etc++site/default/sample",
                          type="zope.app.module.manager.ModuleManager",
                          factory="zope.app.module.manager.ModuleManager")
        self.metadata.flush()
        self.assertRaises(Error, self.fsbundle.create,
                          target, "foo", "bar", source)
        tm = self.metadata.getentry(target)
        self.assert_(bundle_type == tm["type"])
        self.assert_(bundle_factory == tm["factory"])
        self.assertEqual(self.metadata.getnames(target), [])
        self.assert_(not os.path.exists(os.path.join(
            self.etcdir, "bundle-1.0.0", "dummy.py")))

    def test_create_with_factory(self):
        self.create_site()
        source, target = self.make_bundle(factory="foo")
        sm = self.metadata.getentry(source)
        tm = self.metadata.getentry(target)
        self.assert_(tm["type"] != sm["type"])
        self.assertEqual(tm["factory"], "foo")

    def test_create_with_type(self):
        self.create_site()
        source, target = self.make_bundle(type="bar")
        sm = self.metadata.getentry(source)
        tm = self.metadata.getentry(target)
        self.assertEqual(tm["type"], "bar")
        self.assert_(tm["factory"] != sm["factory"])

    def test_create_with_type_and_factory(self):
        self.create_site()
        source, target = self.make_bundle(type="bar", factory="foo")
        tm = self.metadata.getentry(target)
        self.assertEqual(tm["factory"], "foo")
        self.assertEqual(tm["type"], "bar")


class VersionParserTestCase(unittest.TestCase):
    """Tests of the parse_version() helper function."""

    # We use a separate class for this since there's no need for the
    # setUp() done by the FSBundle test class.

    def test_parse_version(self):
        self.assertEqual(parseBundleVersion("1.0.0"), (1, 0, 0, None))
        self.assertEqual(parseBundleVersion("2.3.4"), (2, 3, 4, None))
        self.assertEqual(parseBundleVersion("1.0.0.1"), (1, 0, 0, 1))
        self.assertEqual(parseBundleVersion("1.0.0.a1"), (1, 0, 0, "a1"))
        self.assertEqual(parseBundleVersion("1.0.0.a"), (1, 0, 0, "a"))
        # illegal bundle version numbers:
        for s in ("42", "42.43", "1.0.a2", "1.0.0a1", "0.0.0.0.0",
                  "a.1.2", "b", "1.c.0", "1.2.3.a4.5"):
            self.assertRaises(Error, parseBundleVersion, s)


def test_suite():
    suite = unittest.makeSuite(FSBundleTestCase)
    suite.addTest(unittest.makeSuite(VersionParserTestCase))
    return suite
