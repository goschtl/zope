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
"""Tests for zope.dependencytool.importfinder.

$Id$
"""
import os
import unittest

from zope.dependencytool import importfinder


here = os.path.dirname(__file__)

THIS_PACKAGE = __name__[:__name__.rfind(".")]


class ImportFinderTestCase(unittest.TestCase):

    def test_relative_imports(self):
        finder = importfinder.ImportFinder()
        path = os.path.join(here, "sample.py")
        f = open(path, "rU")
        try:
            finder.find_imports(f, path, THIS_PACKAGE)
        finally:
            f.close()
        imports = finder.get_imports()
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].name, "%s.pkg.module" % THIS_PACKAGE)

    def test_relative_imports_for_packages(self):
        finder = importfinder.ImportFinder(packages=True)
        path = os.path.join(here, "sample.py")
        f = open(path, "rU")
        try:
            finder.find_imports(f, path, THIS_PACKAGE)
        finally:
            f.close()
        imports = finder.get_imports()
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].name, "%s.pkg" % THIS_PACKAGE)

    def test_package_for_module(self):
        self.assertEqual(
            importfinder.package_for_module(__name__),
            THIS_PACKAGE)
        self.assertEqual(
            importfinder.package_for_module("os"),
            None)
        self.assertEqual(
            importfinder.package_for_module("distutils.sysconfig"),
            "distutils")

    def test_module_for_importable(self):
        clsname = __name__ + ".ImportFinderTestCase"
        self.assertEqual(
            importfinder.module_for_importable(clsname), __name__)
        self.assertEqual(
            importfinder.module_for_importable("os.path.isdir"), "os.path")
        # check when we ask about a module:
        self.assertEqual(
            importfinder.module_for_importable(__name__), __name__)
        # and a method of a class:
        methodname = clsname + ".test_module_for_importable"
        self.assertEqual(
            importfinder.module_for_importable(methodname), __name__)


def test_suite():
    return unittest.makeSuite(ImportFinderTestCase)
