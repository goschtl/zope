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
"""Tests of the %import mechanism.

$Id: test_cfgimports.py,v 1.1 2003/10/03 20:01:57 fdrake Exp $
"""

import unittest

from StringIO import StringIO

import ZConfigParser
import ZConfigParser.tests.support


class TestImportFromConfiguration(ZConfigParser.tests.support.TestBase):

    def test_simple_import(self):
        schema = self.load_schema_text("<schema/>")
        loader = self.create_config_loader(schema)
        config, _ = loader.loadFile(
            StringIO("%import ZConfigParser.tests.library.widget\n"))
        # make sure we now have a "private" schema object; the only
        # way to get it is from the loader itself
        self.assert_(schema is not loader.schema)
        # make sure component types are only found on the private schema:
        loader.schema.gettype("widget-b")
        self.assertRaises(ZConfigParser.SchemaError, schema.gettype, "widget-b")

    def test_repeated_import(self):
        schema = self.load_schema_text("<schema/>")
        loader = self.create_config_loader(schema)
        config, _ = loader.loadFile(
            StringIO("%import ZConfigParser.tests.library.widget\n"
                     "%import ZConfigParser.tests.library.widget\n"))

    def test_missing_import(self):
        schema = self.load_schema_text("<schema/>")
        loader = self.create_config_loader(schema)
        self.assertRaises(ZConfigParser.SchemaError, loader.loadFile,
                          StringIO("%import ZConfigParser.tests.missing\n"))


def test_suite():
    return unittest.makeSuite(TestImportFromConfiguration)
