##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
Basic tests for Page Templates used in content-space.

$Id: test_xmldocument.py,v 1.1 2003/04/09 11:47:52 philikon Exp $
"""

import unittest
from zope.schema.interfaces import ValidationError
from zope.app.content.xmldocument import XMLDocument

class XMLDocumentTests(unittest.TestCase):

    def test_create(self):
        doc = XMLDocument()
        doc = XMLDocument('<mydoc/>')
        self.assertRaises(ValidationError, XMLDocument, 'foo')

    def test_set(self):
        src = '<mydoc/>'
        doc = XMLDocument(src)
        self.assertEqual(src, doc.source)
        new_src = '<newdoc/>'
        doc.source = new_src
        self.assertEqual(new_src, doc.source)

def test_suite():
    return unittest.makeSuite(XMLDocumentTests)
