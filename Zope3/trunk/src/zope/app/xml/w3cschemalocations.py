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

$Id: w3cschemalocations.py,v 1.4 2003/04/30 20:13:23 jim Exp $
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
    setInstanceInterfaces(xmltext, schema_interfaces)

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

def setInstanceInterfaces(ob, interfaces):
    directlyProvides(ob, *interfaces)

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

    SCHEMA_INSTANCE_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

    def __init__(self, xml):
        self._xml = xml
        self._schema_uris = []
        self._parser = ParserCreate(namespace_separator=" ")
        self._parser.StartElementHandler = self.startElement
        
    def startElement(self, name, attrs):
        for key, value in attrs.items():
            try:
                namespace_uri, name = key.split(' ')
            except ValueError:
                namespace_uri = None
                name = key
            if (namespace_uri == self.SCHEMA_INSTANCE_NAMESPACE and
                name == 'schemaLocation'):
                self._schema_uris = value.strip().split()
        # abort parsing after the first element, which is the document element
        # raising an error seems to be a legitimate way to do this
        raise DoneParsing

    def parse(self):
        try:
            self._parser.Parse(self._xml, True)
        except ExpatError, e:
            # we do not take any special pains to make sure this is
            # well-formed anyway; this should happen at a higher level
            # (views) or will be detected at a lower layer (parsing into
            # a DOM or SAX events) anyway. 
            pass 
        except DoneParsing:
            pass
        
    def getSchemaLocations(self):
        return self._schema_uris
