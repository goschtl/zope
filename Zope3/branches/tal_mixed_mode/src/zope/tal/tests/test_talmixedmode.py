##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Tests mixing macros processed with noth xml and html modes

$Id$
"""

import os
import StringIO
import unittest

from zope.tal.htmltalparser import HTMLTALParser
from zope.tal.talparser import TALParser
from zope.tal.talinterpreter import TALInterpreter
from zope.tal.dummyengine import DummyEngine
from zope.tal.tests import utils

class BaseMixedModeTestCase(unittest.TestCase):

    def _read(self, path):
        dir = os.path.dirname(__file__)
        fn = os.path.join(dir, *path)
        f = open(fn)
        data = f.read()
        f.close()
        return data

    def _compileHTML(self, source):
        parser = HTMLTALParser()
        parser.parseString(source)
        program, macros = parser.getCode()
        return program, macros

    def _compileXML(self, source):
        parser = TALParser()
        parser.parseString(source)
        bytecode, macros = parser.getCode()
        return bytecode, macros

class HTMLIncludesXMLTestCase(BaseMixedModeTestCase):

    def setUp(self):

        xml = self._read(('input', 'xmlmode_macros.pt'))
        dummy, macros = self._compileXML(xml)
        self.macro = macros['M']
        self.engine = DummyEngine(macros)

        html = self._read(('input', 'htmlmode_template.pt'))
        program, dummy = self._compileHTML(html)
        self.interpreter = TALInterpreter(program, {}, self.engine)

    def test_html_includes_xml(self):
        self.interpreter()

class XMLIncludesHTMLTestCase(BaseMixedModeTestCase):

    def setUp(self):

        html = self._read(('input', 'htmlmode_macros.pt'))
        dummy, macros = self._compileHTML(html)
        self.macro = macros['M']
        self.engine = DummyEngine(macros)

        xml = self._read(('input', 'xmlmode_template.pt'))
        program, dummy = self._compileXML(xml)
        self.interpreter = TALInterpreter(program, {}, self.engine)

    def test_xml_includes_html(self):
        self.interpreter()

def test_suite():
    suite = unittest.makeSuite(HTMLIncludesXMLTestCase)
    suite.addTest(unittest.makeSuite(XMLIncludesHTMLTestCase))
    return suite

if __name__ == "__main__":
    errs = utils.run_suite(test_suite())
    sys.exit(errs and 1 or 0)
