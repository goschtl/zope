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
"""Tests for zpkgtools.config."""

import os
import unittest

from zpkgtools import cfgparser
from zpkgtools import config


here = os.path.dirname(os.path.abspath(__file__))


class ConfigTestCase(unittest.TestCase):

    def test_defaultConfigurationPath(self):
        # Not really sure what makes sense to check here, but at least
        # make sure it returns a string:
        path = config.defaultConfigurationPath()
        self.assert_(isinstance(path, basestring))

    def test_constructor(self):
        path = os.path.join(here, "zpkg-ok.conf")
        cf = config.Configuration(path)
        self.assertEqual(
            cf.location_maps,
            ["cvs://cvs.example.org/cvsroot:module/package/PACKAGES.txt",
             os.path.join(here, "relative/path.txt")])

    def test_constructor_bad_config_setting(self):
        # unknown option:
        path = os.path.join(here, "zpkg-error-1.conf")
        self.assertRaises(cfgparser.ConfigurationError,
                          config.Configuration, path)

        # repository-map without path
        path = os.path.join(here, "zpkg-error-2.conf")
        self.assertRaises(cfgparser.ConfigurationError,
                          config.Configuration, path)

    def test_constructor_no_such_file(self):
        path = os.path.join(here, "no-such-file")
        self.assertRaises(IOError, config.Configuration, path)


def test_suite():
    return unittest.makeSuite(ConfigTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
