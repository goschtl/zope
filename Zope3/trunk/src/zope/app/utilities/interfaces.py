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
"""Special Mutable Schema interfaces.

$Id: interfaces.py,v 1.2 2003/08/16 00:44:21 srichter Exp $
"""
from zope.interface import Interface
from zope.app.utilities.mutableschemafield \
     import MutableSchemaField, MutableSchemasField

class IMutableSchemaContent(Interface):
    """An interface for content that can choose a mutable schema
    to be used for it"""

    mutableschema = MutableSchemaField(
        title=u"Mutable Schema to use",
        description=u"""Mutable Schema to use as additional fields for """
                    """this content type""")

class IMutableSchemasContent(Interface):
    """An interface for content that can choose a mutable schema
    to be used for it"""

    mutableschemas = MutableSchemasField(
        title=u"Mutable Schemas to use",
        description=u"""Mutable Schemas to use as additional fields for """
                    """this content type""")
