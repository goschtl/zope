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
"""'tool' directive for 'browser' namespace

$Id: metadirectives.py,v 1.1 2004/03/21 16:02:18 srichter Exp $
"""
from zope.configuration.fields import GlobalObject, PythonIdentifier, MessageID
from zope.interface import Interface

class IUtilityToolDirective(Interface):
    """Directive for creating new utility-based tools."""

    interface = GlobalObject(
        title=u"Interface",
        description=u"Interface used to filter out the available entries in a \
                      tool",
        required=True)
    
    folder = PythonIdentifier(
        title=u"Destination Folder",
        description=u"""Destination Folder in which the tool instances are
                        placed.""",
        required=False,
        default=u"tools")
    
    title = MessageID(
        title=u"Title",
        description=u"""The title of the tool.""",
        required=False
        )

    description = MessageID(
        title=u"Description",
        description=u"Narrative description of what the tool represents.",
        required=False
        )
