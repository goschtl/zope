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
"""Tests of zpkgsetup.build_scripts.

$Id$
"""
import os.path
import shutil
import unittest

from distutils.dist import Distribution

from zpkgsetup.build_scripts import build_scripts
from zpkgsetup.tests.tempfileapi import mkdtemp


class BuildScriptsTestCase(unittest.TestCase):

    def setUp(self):
        self.srcdir = mkdtemp(prefix="src-")
        self.destdir = mkdtemp(prefix="dest-")
        self.script_sources = []
        self.add_script("script1")
        self.add_script("script2.py")
        self.add_script("script3.PY")

    def add_script(self, name):
        path = os.path.join(self.srcdir, name)
        self.script_sources.append(path)
        f = open(path, "w")
        f.write("#!/usr/bin/env python2.3\n")
        f.write("pass")
        f.close()

    def tearDown(self):
        shutil.rmtree(self.srcdir)
        shutil.rmtree(self.destdir)

    def test_not_on_windows(self):
        self.check_scripts(0, ["script1", "script2.py", "script3.PY"])

    def test_on_windows(self):
        self.check_scripts(1, ["script1.py", "script2.py", "script3.PY"])

    def check_scripts(self, on_windows, scripts):
        dist = Distribution()
        dist.scripts = self.script_sources
        cmd = build_scripts(dist)
        cmd.build_dir = self.destdir
        cmd.on_windows = on_windows
        cmd.ensure_finalized()
        cmd.run()
        for fn in scripts:
            path = os.path.join(self.destdir, fn)
            self.assert_(os.path.isfile(path),
                         "missing script " + fn)


def test_suite():
    return unittest.makeSuite(BuildScriptsTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
