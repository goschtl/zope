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
"""Schemas for the 'help' ZCML namespace 

$Id: metadirectives.py,v 1.2 2003/08/03 19:08:30 philikon Exp $
"""
from zope.configuration.fields import GlobalObject, Path, MessageID
from zope.interface import Interface, implements, classProvides
from zope.schema import TextLine, BytesLine

class IRegisterDirective(Interface):
    """Register directive for onlien help topics."""

    id = BytesLine(
        title=u"Topic Id",
        description=u"Id of the topic as it will appear in the URL.",
        required=True)

    title = MessageID(
        title=u"Title",
        description=u"Provides a title for the online Help Topic.",
        required=True)

    parent = BytesLine(
        title=u"Parent Topic",
        description=u"Id of the parent topic.",
        default="",
        required=False)

    for_ = GlobalObject(
        title=u"Object Interface",
        description=u"Interface for which this Help Topic is registered.",
        default=None,
        required=False)

    view = BytesLine(
        title=u"View Name",
        description=u"The view name for which this Help Topic is registered.",
        default="",
        required=False)

    doc_path = Path(
        title=u"Path to File",
        description=u"Path to the file that contains the Help Topic content.",
        required=True)
