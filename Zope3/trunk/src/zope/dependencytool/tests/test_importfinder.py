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
"""Tests for zope.dependencytool.importfinder.

$Id$
"""
import os
import unittest

from zope.dependencytool.importfinder import ImportFinder


here = os.path.dirname(__file__)

THIS_PACKAGE = __name__[:__name__.rfind(".")]


class ImportFinderTestCase(unittest.TestCase):

    def test_relative_imports(self):
        finder = ImportFinder()
        path = os.path.join(here, "sample.py")
        f = open(path, "rU")
        try:
            finder.find_imports(f, path, THIS_PACKAGE)
        finally:
            f.close()
        imports = finder.get_imports()
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].name,
                         "%s.pkg.module" % THIS_PACKAGE)


def test_suite():
    return unittest.makeSuite(ImportFinderTestCase)
