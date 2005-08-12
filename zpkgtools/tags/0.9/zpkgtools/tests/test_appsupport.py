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
"""Tests of the 'application' installation support."""

import os
import shutil
import sys
import unittest

from zpkgsetup.tests import tempfileapi as tempfile

from zpkgtools import app


class Component:

    def __init__(self, component_name, pubinfo_name):
        self.name = component_name
        self.pubinfo = PublicationInfo(pubinfo_name)

    def get_publication_info(self):
        return self.pubinfo

class PublicationInfo:

    def __init__(self, pubinfo_name):
        self.name = pubinfo_name


class AppsupportTestBase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test-appsupport-")
        resource_map = os.path.join(self.tmpdir, "resource.map")
        f = open(resource_map, "w")
        f.write("TestThing  file:///dev/null\n")
        f.close()
        self.old_tempdir = tempfile.gettempdir()
        self.options = app.parse_args(["foo/bar.py", "-f", "-m", resource_map,
                                       "-v", "0.1.0test1", "TestThing"])
        self.app = app.BuilderApplication(self.options)

    def tearDown(self):
        self.app.cleanup()
        shutil.rmtree(self.tmpdir)
        # This assumes tempfile is really tempfileapi:
        tempfile.tempfile.tempdir = self.old_tempdir

    def make_component(self):
        return Component("TestThing", self.publication_name)

    def test_Makefile_targets(self):
        component = self.make_component()
        self.app.write_application_support(component)
        # make sure the expected files are generated
        for fn in ("configure", "Makefile.in", "README.txt"):
            fn = os.path.join(self.app.destination, fn)
            self.assert_(os.path.isfile(fn))
        if sys.platform[:3].lower() == "win":
            return
        # the rest of this can only run on Unixish platforms
        pwd = os.getcwd()
        os.chdir(self.app.destination)
        try:
            self.assert_(os.path.isfile("configure"))
            rc = os.system("./configure -q --with-python '%s'"
                           % sys.executable)
            self.assertEqual(rc, 0)
            self.assert_(os.path.isfile("Makefile"))
            # be sure the Makefile has the expected targets:
            rc = os.system("make -n >/dev/null")
            self.assertEqual(rc, 0)
            rc = os.system("make -n build >/dev/null")
            self.assertEqual(rc, 0)
            rc = os.system("make -n install >/dev/null")
            self.assertEqual(rc, 0)
            rc = os.system("make -n check >/dev/null")
            self.assertEqual(rc, 0)
            rc = os.system("make -n test >/dev/null")
            self.assertEqual(rc, 0)
        finally:
            os.chdir(pwd)

    def test_configure_rejects_bogus_args(self):
        # this test only makes sense on Unixish platforms
        if sys.platform[:3].lower() == "win":
            return
        component = self.make_component()
        self.app.write_application_support(component)
        pwd = os.getcwd()
        os.chdir(self.app.destination)
        try:
            self.assert_(os.path.isfile("configure"))
            rc = os.system("./configure junk")
            # make sure it exited normally with error code 2:
            self.assert_(os.WIFEXITED(rc))
            self.assertEqual(os.WEXITSTATUS(rc), 2)
        finally:
            os.chdir(pwd)


class AppsupportTestCaseWithName(AppsupportTestBase):

    publication_name = "Test Thingy from Fredericksburg"


class AppsupportTestCaseWithoutName(AppsupportTestBase):

    publication_name = None


def test_suite():
    suite = unittest.makeSuite(AppsupportTestCaseWithName)
    suite.addTest(unittest.makeSuite(AppsupportTestCaseWithoutName))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
