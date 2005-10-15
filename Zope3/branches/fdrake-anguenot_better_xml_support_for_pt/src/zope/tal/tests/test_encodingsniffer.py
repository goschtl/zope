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
"""Test the HTML fragement encoding sniffer

$Id$
"""

import sys
import unittest

from zope.tal.encodingsniffer import sniff_encoding

class EncodingSnifferTestCase(unittest.TestCase):

    def test_ascii_html_fragment_no_encoding(self):
        str_ = """<p tal:content="python:u'déjà-vu'">para</p>"""
        self.failIf(sniff_encoding(str_))

    def test_ascii_html_fragment_with_encoding(self):
        str_ = """<meta http-equiv='Content-type' content='text/html; charset=ISO-8859-15'><p tal:content="python:u'déjà-vu'">para</p>"""
        self.assertEqual(sniff_encoding(str_), 'ISO-8859-15')

    def test_ascii_html_fragment_with_encoding_and_whispace(self):
        str_ = """<meta http-equiv='Content-type' content='text/html; charset= ISO-8859-15 '><p tal:content="python:u'déjà-vu'">para</p>"""
        self.assertEqual(sniff_encoding(str_), 'ISO-8859-15')

    def test_ascii_html_fragment_with_encoding_and_ligne_break(self):
        str_ = """<meta http-equiv='Content-type' content='text/html;\n charset= ISO-8859-15 '><p tal:content="python:u'déjà-vu'">para</p>"""
        self.assertEqual(sniff_encoding(str_), 'ISO-8859-15')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(EncodingSnifferTestCase),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
