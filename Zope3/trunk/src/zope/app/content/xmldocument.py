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
$Id: xmldocument.py,v 1.1 2003/04/09 11:47:52 philikon Exp $
"""
from persistence import Persistent

from zope.schema.fieldproperty import FieldProperty
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.content.xmldocument import IXMLDocument

class XMLDocument(Persistent):

    __implements__ = IXMLDocument, IAnnotatable

    source = FieldProperty(IXMLDocument['source'])
 
    def __init__(self, source='<doc/>'):
        self.source = source
