##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id: test_schemainterface.py,v 1.1 2003/04/10 16:07:46 philikon Exp $
"""
import unittest
from zope.app.xml.schemainterface import XMLSchemaInterfaceClass

class XMLSchemaInterfaceTests(unittest.TestCase):

    def setUp(self):
        schema1_uri = "http://schema.zope.org/hypothetical/schema1"
        schema2_uri = "http://schema.zope.org/hypothetical/schema2"
        self.schema1 = XMLSchemaInterfaceClass(schema1_uri)
        self.schema1b = XMLSchemaInterfaceClass(schema1_uri)
        self.schema2 = XMLSchemaInterfaceClass(schema2_uri)

    def test_compare(self):
        self.assert_(self.schema1 == self.schema1b)
        self.assert_(self.schema1 != self.schema2)

    def test_hash(self):
        mydict = {}
        marker = object()
        mydict[self.schema1] = marker
        mydict[self.schema2] = None
        self.assertEquals(mydict[self.schema1b], marker)
        self.failIfEqual(mydict[self.schema2], marker)

def test_suite():
    return unittest.makeSuite(XMLSchemaInterfaceTests)
