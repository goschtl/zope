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
$Id: xmldocument.py,v 1.4 2003/06/07 06:37:23 stevea Exp $
"""
from persistence import Persistent
from zope.app.interfaces.content.xmldocument import IXMLDocument
from zope.app.xml.w3cschemalocations import setInstanceInterfacesForXMLText
from zope.interface import implements

class XMLDocument(Persistent):

    implements(IXMLDocument)

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
        setInstanceInterfacesForXMLText(self)

    def _getSource(self):
        return self._source

    source = property(_getSource, _setSource)
