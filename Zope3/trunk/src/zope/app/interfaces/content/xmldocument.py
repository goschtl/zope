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
$Id: xmldocument.py,v 1.1 2003/04/09 11:47:53 philikon Exp $
"""
import zope.app.xml.field
from zope.interface import Interface
from zope.app.i18n import ZopeMessageIDFactory as _

class IXMLDocument(Interface):
    """XMLDocument stores XML text."""

    source = zope.app.xml.field.XML(
        title=_(u"Source"),
        description=_(u"""The text source of the XML document."""),
        required=True)
