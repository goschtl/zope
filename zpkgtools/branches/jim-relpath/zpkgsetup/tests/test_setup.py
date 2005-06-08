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
"""Tests of zpkgtools.setup."""

import os
import unittest

from zpkgsetup import publication
from zpkgsetup import setup


here = os.path.dirname(os.path.abspath(__file__))


class SetupContextTestCase(unittest.TestCase):

    def test_python_files_as_data(self):
        packagedir = os.path.join(here, "input", "package")
        publicationcfg = os.path.join(packagedir, publication.PUBLICATION_CONF)
        setupfile = os.path.join(here, "input", "setup.py")
        f = open(publicationcfg, "w")
        f.write("Metadata-version: 1.0\n"
                "Name: foo\n")
        f.close()
        try:
            context = setup.SetupContext("package", "0.1.234", setupfile)
            context.initialize()
            context.package_data["package"].sort()
            self.assertEqual(context.package_data,
                             {"package": ["PUBLICATION.cfg",
                                          "datadir/justdata.py"]})
        finally:
            os.unlink(publicationcfg)

    def test_extension_sources_are_not_package_data(self):
        packagedir = os.path.join(here, "input", "package2")
        setupfile = os.path.join(here, "input", "setup.py")
        context = setup.SetupContext("package2", "0.1.234", setupfile)
        context.initialize()
        context.package_data["package2"].sort()
        self.assertEqual(context.package_data,
                         {"package2": ["PUBLICATION.cfg", "SETUP.cfg"]})


def test_suite():
    return unittest.makeSuite(SetupContextTestCase)
