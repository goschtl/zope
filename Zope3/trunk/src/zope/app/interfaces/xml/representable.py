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
$Id: representable.py,v 1.1 2003/04/09 20:51:31 philikon Exp $
"""

from zope.interface import Interface, Attribute

class IXMLRepresentable(Interface):
    """
    This object can be adapted to one form of XML data representation
    """

class IXMLText(IXMLRepresentable):
    """
    This object represents XML data as text.
    """

    source = Attribute("XML text source")
