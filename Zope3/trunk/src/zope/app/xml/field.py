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
$Id: field.py,v 1.4 2003/06/03 15:47:51 stevea Exp $
"""
from zope.app.interfaces.xml.field import IXML
from zope.schema.interfaces import ValidationError
from zope.schema import Bytes
from zope.schema.fieldproperty import FieldProperty
from xml.parsers.expat import ParserCreate, ExpatError
from zope.interface import implements

NotWellFormedXML = u"NotWellFormedXML"

class XML(Bytes):
    implements(IXML)

    check_wellformedness = FieldProperty(IXML['check_wellformedness'])

    def _validate(self, value):
        super(XML, self)._validate(value)
        if not self.check_wellformedness:
            return
        parser = ParserCreate()
        try:
            parser.Parse(value, True)
        except ExpatError, e:
            raise ValidationError(NotWellFormedXML)
