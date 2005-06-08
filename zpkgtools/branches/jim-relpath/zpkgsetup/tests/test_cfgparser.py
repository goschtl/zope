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
"""Tests for zpkgtools.cfgparser."""

import unittest

from StringIO import StringIO

from zpkgsetup import cfgparser


class SimpleSection:

    finished = False
    ending_parent = None
    ending_typename = None
    ending_name = None

    def __init__(self, parent=None, typename=None, name=None):
        self.parent = parent
        self.typename = typename
        self.name = name


class AnythingGoesSchema:

    def getConfiguration(self):
        return SimpleSection()

    def startSection(self, parent, typename, name):
        return SimpleSection(parent, typename, name)

    def finishSection(self, section):
        section.finished = True
        return section

    def endSection(self, parent, typename, name, child):
        child.ending_parent = parent
        child.ending_typename = typename
        child.ending_name = name
        if not hasattr(parent, typename):
            setattr(parent, typename, [])
        getattr(parent, typename).append(child)
        self.finishSection(child)

    def addValue(self, section, key, value):
        key = key.lower().replace("-", "_")
        if not hasattr(section, key):
            setattr(section, key, [])
        getattr(section, key).append(value)


class ParserTestCase(unittest.TestCase):

    schema = AnythingGoesSchema()

    def createParser(self, text=""):
        sio = StringIO(text)
        self.parser = cfgparser.Parser(sio, "<some-url>", self.schema)
        return self.parser

    def test_replace(self):
        # "legal" values are those that are legal in ZConfig
        eq = self.assertEqual
        raises = self.assertRaises
        replace = self.createParser().replace

        # some legal values that don't have '$':
        eq(replace(""), "")
        eq(replace(" foo bar "), " foo bar ")
        eq(replace("x"), "x")

        # legal, supported values with '$':
        eq(replace("$$"), "$")
        eq(replace("$$$$"), "$$")
        eq(replace("$$xyz$$"), "$xyz$")

        # legal, unsupported values (all have '$'):
        raises(cfgparser.ConfigurationError, replace, "$foo")
        raises(cfgparser.ConfigurationError, replace, "${foo-bar}")

        # illegal values:
        raises(cfgparser.ConfigurationError, replace, "$")
        raises(cfgparser.ConfigurationError, replace, "foo$")

    def test_schema_use(self):
        eq = self.assertEqual
        p = self.createParser("""
            # This is a comment.

            key value 1
            key value 2
            <section/>
            <section foo/>
            <section>
              key  value 3
            </section>
            <section splat>
              <inner>
                key value 5
              </inner>
              key value 4
            </section>
            """)
        cf = p.load()
        self.check_section(cf, None, None, None, key=["value 1", "value 2"])
        s1, s2, s3, s4 = cf.section
        self.check_section(s1, cf, None, "section")
        self.check_section(s2, cf, "foo", "section")
        self.check_section(s3, cf, None, "section", key=["value 3"])
        self.check_section(s4, cf, "splat", "section", key=["value 4"])
        inner, = s4.inner
        self.check_section(inner, s4, None, "inner", key=["value 5"])

    def check_section(self, section, parent, name, typename, **attrs):
        self.assert_(section.finished)
        self.assert_(section.parent is parent)
        self.assert_(section.parent is section.ending_parent)
        self.assertEqual(section.name, name)
        self.assertEqual(section.name, section.ending_name)
        self.assertEqual(section.typename, typename)
        self.assertEqual(section.typename, section.ending_typename)
        for name, value in attrs.iteritems():
            v = getattr(section, name)
            self.assertEqual(v, value)


class SchemaTestCase(unittest.TestCase):

    top_level_converted = False

    def setUp(self):
        self.schema = cfgparser.Schema(
            ({}, [], self.top_level_conversion))

    def top_level_conversion(self, section):
        self.top_level_converted = True
        return section

    def test_getConfiguration(self):
        cf = self.schema.getConfiguration()
        self.failIf(self.top_level_converted)


def test_suite():
    suite = unittest.makeSuite(ParserTestCase)
    suite.addTest(unittest.makeSuite(SchemaTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
