##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: field.py,v 1.2 2003/04/09 09:46:47 faassen Exp $
"""
from zope.app.interfaces.xml.field import IXML
from zope.schema.interfaces import ValidationError
from zope.schema import Bytes
from xml.parsers.expat import ParserCreate, ExpatError

NotWellFormedXML = u"NotWellFormedXML"

class XML(Bytes):
    
    __implements__ = IXML

    def _validate(self, value):
        super(XML, self)._validate(value)
        parser = ParserCreate()
        try:
            parser.Parse(value, True)
        except ExpatError, e:
            raise ValidationError(NotWellFormedXML)
        
