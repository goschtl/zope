# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Unittests for RenderPDF Parser

$Id$
"""

import unittest
from StringIO import StringIO
import xml.dom.minidom
import os.path
import urllib

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import toLength

from zope.testing import doctest

from z3c.pdftemplate.pml2pdf import Platypus
from z3c.pdftemplate.pml2pdf.Parser import TemplateParser, DocumentParser


test_template_xml_template = '''
<template filename="default.pdf"
            pagesize="A4"
            landscape="0"
            showboundary="0"
            leftmargin="1cm"
            rightmargin="1cm"
            topmargin="1cm"
            bottommargin="1cm"
            allowsplitting="1">
  <pagetemplate id="Page" >
   <frame  id="content"
           nextid="content"
           x="2cm"
           y="1.5cm"
           width="17cm"
           height="25.5cm"
           leftpadding="0.1cm"
           rightpadding="0.1cm"
           toppadding="0.5cm"
           bottompadding="0.5cm"
           showBoundary="0"/>
  </pagetemplate>
</template>
'''

document_xml_template = '''
<document filename="report01.pdf">
  <title>Test Document</title>
  <author>Ulrich Eck</author>
  <subject>only for testing ...</subject>
  <content>
  %s
  </content>
</document>
'''


class TestDocumentParser(unittest.TestCase):

    def setUp(self):
        template_dom = xml.dom.minidom.parseString(test_template_xml_template)
        self.template = TemplateParser(template_dom, 'utf-8')()

    def _parse(self, content=''):
        xml_data = document_xml_template % content
        xml_dom = xml.dom.minidom.parseString(xml_data)
        return DocumentParser(xml_dom, 'utf-8')(self.template)

    def xxx_test_paragraph(self):
        xml_fragment = '''<para style="test">Test</para>'''
        doc = self._parse(xml_fragment)
        el = doc.dom.content[0]
        self.assert_(isinstance(el, Platypus.xmlParagraph))
        self.assertEqual(el.style, 'test')
        self.assertEqual(el.rawtext, 'Test')

        xml_fragment = '''<para style="Bullet" bullettext="X">Test</para>'''
        doc = self._parse(xml_fragment)
        el = doc.dom.content[0]
        self.assert_(isinstance(el, Platypus.xmlParagraph))
        self.assertEqual(el.style, 'Bullet')
        self.assertEqual(el.bulletText, 'X')
        self.assertEqual(el.rawtext, 'Test')

    def xxx_test_prefmt(self):
        xml_fragment = '''<prefmt style="test" dedent="3">Test</prefmt>'''
        doc = self._parse(xml_fragment)
        el = doc.doc.content[0]
        self.assert_(isinstance(el, Platypus.xmlPreformattedText))
        self.assertEqual(el.style, 'test')
        self.assertEqual(el.dedent, 3)
        self.assertEqual(el.rawtext, 'Test')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDocumentParser),
        doctest.DocFileSuite('README.txt')
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
