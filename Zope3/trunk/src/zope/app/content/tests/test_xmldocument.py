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
Basic tests for XML Document.

$Id: test_xmldocument.py,v 1.3 2003/04/11 10:52:16 philikon Exp $
"""

import unittest

from zope.schema.interfaces import ValidationError
from zope.app.content.xmldocument import XMLDocument
from zope.app.interfaces.content.xmldocument import IXMLDocument
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.app.interfaces.xml.source import IXMLSource
from zope.app.component.globalinterfaceservice import interfaceService

class IRandomInterface(Interface):
    pass

class XMLDocument2(XMLDocument):
    __implements__ = IXMLDocument, IRandomInterface

    
class XMLDocumentTests(PlacelessSetup, unittest.TestCase):

    def test_create(self):
        doc = XMLDocument()
        self.assertEquals('<doc/>', doc.source)
        
        doc = XMLDocument('<mydoc/>')
        self.assertEquals('<mydoc/>', doc.source)
    
    def test_set(self):
        src = '<mydoc/>'
        doc = XMLDocument(src)
        self.assertEqual(src, doc.source)
        new_src = '<newdoc/>'
        doc.source = new_src
        self.assertEqual(new_src, doc.source)

    def test_xmlschema_interfaces(self):
        doc = XMLDocument()
        self.assert_(IXMLDocument.isImplementedBy(doc))

        schema1 = 'http://schema.zope.org/hypothetical/schema1'
        schema2 = 'http://schema.zope.org/hypothetical/schema2'
        extends = (IXMLSource,)
        interface1 = InterfaceClass(schema1, extends, {})
        interface2 = InterfaceClass(schema2, extends, {})
        
        interfaceService.provideInterface(schema1, interface1)

        xml = '''
<doc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://schema.zope.org/hypothetical/schema1">
foo
</doc>'''
        doc.source = xml

        self.assert_(interface1.isImplementedBy(doc))
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))
        
        doc.source = '<doc />'

        self.assert_(not interface1.isImplementedBy(doc))
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))

        xml = '''
<doc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://schema.zope.org/hypothetical/schema1
                         http://schema.zope.org/hypothetical/schema2">
foo
</doc>'''
        doc.source = xml
        
        self.assert_(interface1.isImplementedBy(doc))
        # can't find it as it isn't provided yet
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))

        # finally provide and set document again
        interfaceService.provideInterface(schema2, interface2)

        doc.source = xml
        
        self.assert_(interface1.isImplementedBy(doc))
        self.assert_(interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))

    def test_xmlschema_interfaces2(self):
        # the same tests, but XMLDocument2 has two interfaces not just one
        
        doc = XMLDocument2()
        self.assert_(IXMLDocument.isImplementedBy(doc))
        self.assert_(IRandomInterface.isImplementedBy(doc))
        
        schema1 = 'http://schema.zope.org/hypothetical/schema1'
        schema2 = 'http://schema.zope.org/hypothetical/schema2'
        extends = (IXMLSource,)
        interface1 = InterfaceClass(schema1, extends, {})
        interface2 = InterfaceClass(schema2, extends, {})
        
        interfaceService.provideInterface(schema1, interface1)

        xml = '''
<doc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://schema.zope.org/hypothetical/schema1">
foo
</doc>'''
        doc.source = xml

        self.assert_(interface1.isImplementedBy(doc))
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))
        self.assert_(IRandomInterface.isImplementedBy(doc))

        doc.source = '<doc />'

        self.assert_(not interface1.isImplementedBy(doc))
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))
        self.assert_(IRandomInterface.isImplementedBy(doc))
        
        xml = '''
<doc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://schema.zope.org/hypothetical/schema1
                         http://schema.zope.org/hypothetical/schema2">
foo
</doc>'''
        doc.source = xml
        
        self.assert_(interface1.isImplementedBy(doc))
        # can't find it as it isn't provided yet
        self.assert_(not interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))
        self.assert_(IRandomInterface.isImplementedBy(doc))
        
        # finally provide and set document again
        interfaceService.provideInterface(schema2, interface2)

        doc.source = xml
        
        self.assert_(interface1.isImplementedBy(doc))
        self.assert_(interface2.isImplementedBy(doc))
        self.assert_(IXMLDocument.isImplementedBy(doc))
        self.assert_(IRandomInterface.isImplementedBy(doc))
        
def test_suite():
    return unittest.makeSuite(XMLDocumentTests)
