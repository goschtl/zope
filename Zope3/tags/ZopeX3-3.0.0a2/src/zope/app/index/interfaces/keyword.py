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
"""Interfaces related to keyword indexing and searching.

Should be refactored (along with text and field)

$Id$
"""
from zope.interface import Interface
from zope.schema import BytesLine, Choice


class IUIKeywordCatalogIndex(Interface):
    """Interface for creating a KeywordIndex in a catalog from the ZMI."""

    interface = Choice(
        title=u"Interface",
        description=u"Objects will be adapted to this interface",
        vocabulary="Interfaces",
        required=False)

    field_name = BytesLine(
        title=u"Field Name",
        description=u"Name of the field to index")

