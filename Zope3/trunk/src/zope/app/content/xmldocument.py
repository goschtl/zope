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
$Id: xmldocument.py,v 1.2 2003/04/10 13:04:43 faassen Exp $
"""
from persistence import Persistent
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.content.xmldocument import IXMLDocument
from zope.app.xml.w3cschemalocations import getW3CXMLSchemaLocations
from zope.app.component.globalinterfaceservice import interfaceService

class XMLDocument(Persistent):

    __implements__ = IXMLDocument
    
    def __init__(self, source='<doc/>'):
        self.source = source
        
    def _setSource(self, value):
        self._source = value
        
        # XXX for now, parse the document and lift the W3C XML schema
        # locations from it to identify which schemas are used
        # this dependency on W3C XML schema should go away at some point,
        # and it should also become possible to set schemas explicitly
        # XML Schema interfaces are looked up for each mentioned schema,
        # and if this interface exists, we manipulate this instance to
        # state it has those interfaces.
        
        # XXX the interface manipulation is a hack, should be fixed after
        # interfacegheddon
        
        schema_uris = getW3CXMLSchemaLocations(value)

        # if there are no schemas, then we go back to whatever the class
        # implements
        if not schema_uris:
            try:
                del self.__implements__
            except AttributeError:
                pass
            return

        cls = self.__class__
        if isinstance(cls.__implements__, tuple):
            implements = list(cls.__implements__)
        else:
            implements = [cls.__implements__]

        orig_implements = implements[:]
        
        for schema_uri in schema_uris:
            interface = interfaceService.queryInterface(schema_uri, None)
            if interface is not None and interface not in implements:
                implements.append(interface)

        # if there are no changes in the interfaces, go back to whatever
        # the class implements
        if implements == orig_implements:
            try:
                del self.__implements__
            except AttributeError:
                pass
            return

        self.__implements__ = tuple(implements)    

    def _getSource(self):
        return self._source
    
    source = property(_getSource, _setSource)

    
            
