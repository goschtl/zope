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
"""Content Component Definition and Instance Interfaces

$Id: content.py,v 1.2 2003/08/16 00:43:34 srichter Exp $
"""
from zope.interface import Interface, Attribute
from zope.schema import TextLine
from zope.app.component.interfacefield import InterfaceField


class IContentComponentDefinition(Interface):
    """Content Component Definitions describe simple single-schema based
    content components including their security declarations."""

    name = TextLine(
        title=u"Name of Content Component Type",
        description=u"""This is the name of the document type.""",
        required=True)

    schema = InterfaceField(
        title=u"Schema",
        description=u"Specifies the schema that characterizes the document.",
        required=True)

    permissions = Attribute(
        u"A dictionary that maps set/get permissions on the schema's"
        u"fields. Entries looks as follows: {fieldname:(set_perm, get_perm)}")


class IContentComponentInstance(Interface):
    """Interface describing a Content Component Instance"""

    __name__ = TextLine(
        title=u"Name of Content Component Type",
        description=u"""This is the name of the document type.""",
        required=True)

    __schema__ = InterfaceField(
        title=u"Schema",
        description=u"Specifies the schema that characterizes the document.",
        required=True)
