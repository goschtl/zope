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
This module contains a few utilities to extract information from XML text.

$Id: w3cschemalocations.py,v 1.7 2003/07/17 14:54:46 fdrake Exp $
"""
from zope.interface import directlyProvides
from xml.parsers.expat import ParserCreate, ExpatError
from zope.app.component.globalinterfaceservice import interfaceService

def setInstanceInterfacesForXMLText(xmltext):
    """
    Sets the schema interfaces on an instance that implements IXMLText
    according to the schemas locations the text refers to
    """
    schema_uris = getW3CXMLSchemaLocations(xmltext.source)
    schema_interfaces = getInterfacesForXMLSchemaLocations(schema_uris)
    directlyProvides(xmltext, *schema_interfaces)

def getInterfacesForXMLSchemaLocations(schema_uris):
    """
    Get interfaces for XML schema locations (URIs)
    """
    result = []
    for uri in schema_uris:
        interface = interfaceService.queryInterface(uri, None)
        if interface is not None:
            result.append(interface)
    return result

def getW3CXMLSchemaLocations(xml):
    """Give list of URIs of the schema an XML document promises to implement.

    These are specified in the xsi:schemaLocation attribute of the document
    element.
    """
    parser = W3CXMLSchemaLocationParser(xml)
    parser.parse()
    return parser.getSchemaLocations()

class DoneParsing(Exception):
    pass

class W3CXMLSchemaLocationParser:

    CHUNK_SIZE = 1024

    SCHEMA_INSTANCE_NAME = (
        'http://www.w3.org/2001/XMLSchema-instance schemaLocation')

    def __init__(self, xml):
        self._xml = xml
        self._schema_uris = []
        self._parser = ParserCreate(namespace_separator=" ")
        self._parser.StartElementHandler = self.startElement

    def startElement(self, name, attrs):
        self._schema_uris = attrs.get(self.SCHEMA_INSTANCE_NAME, '').split()
        # abort parsing after the first element, which is the document element
        # raising an error is the best way to exit the parse
        raise DoneParsing

    def parse(self):
        start = 0
        try:
            # Feed the document to Expat a little bit at a time; this
            # allows a parse of a well-formed but large document to
            # exit more quickly once the start tag for the document
            # element has been found.
            while 1:
                text = self._xml[start:start + self.CHUNK_SIZE]
                if not text:
                    break
                start += self.CHUNK_SIZE
                self._parser.Parse(text, False)
        except ExpatError:
            # we do not take any special pains to make sure this is
            # well-formed anyway; this should happen at a higher level
            # (views) or will be detected at a lower layer (parsing into
            # a DOM or SAX events) anyway.
            pass
        except DoneParsing:
            pass

    def getSchemaLocations(self):
        return self._schema_uris
