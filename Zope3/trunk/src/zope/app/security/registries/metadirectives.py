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
"""Renderer configuration code

$Id: metadirectives.py,v 1.2 2003/08/03 19:08:39 philikon Exp $
"""
from zope.interface import Interface
from zope.schema import TextLine, Text, Id
from zope.configuration.fields import MessageID

class IBaseDefineDirective(Interface):
    """Define a new security object."""
    
    id = TextLine(
        title=u"Id",
        description=u"Id as which this object will be known and used.",
        required=True)

    title = MessageID(
        title=u"Title",
        description=u"Provides a title for the object.",
        required=True)

    description = MessageID(
        title=u"Title",
        description=u"Provides a description for the object.",
        required=False)


class IDefinePermissionDirective(IBaseDefineDirective):
    """Define a new permission."""

    id = Id(
        title=u"Id",
        description=u"Id as which this permission will be known and used.",
        required=True)

class IDefineRoleDirective(IBaseDefineDirective):
    """Define a new role."""

class IDefinePrincipalDirective(IBaseDefineDirective):
    """Define a new principal."""

    login = TextLine(
        title=u"Username/Login",
        description=u"Specifies the Principal's Username/Login.",
        required=True)

    password = TextLine(
        title=u"Password",
        description=u"Specifies the Principal's Password.",
        required=True)

class IDefineUnauthenticatedPrincipalDirective(IBaseDefineDirective):
    """Define a new unauthenticated principal."""

