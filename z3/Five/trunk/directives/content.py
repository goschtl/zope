##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: metadirectives.py 25177 2004-06-02 13:17:31Z jim $
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, \
     PythonIdentifier, MessageID
from zope.schema import TextLine, Id
from Products.Five.security.fields import Permission

class IContentDirective(Interface):
    """
    Make statements about a content class
    """

    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

class IImplementsSubdirective(Interface):
    """
    Declare that the class given by the content directive's class
    attribute implements a given interface
    """

    interface = Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=GlobalObject()
        )

class IRequireSubdirective(Interface):
    """
    Indicate that the a specified list of names or the names in a
    given Interface require a given permission for access.
    """

    permission = Permission(
        title=u"Permission",
        description=u"""
        Specifies the permission by id that will be required to
        access or mutate the attributes and methods specified.""",
        required=False
        )

    attributes = Tokens(
        title=u"Attributes and methods",
        description=u"""
        This is a list of attributes and methods that can be accessed.""",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interfaces",
        description=u"""
        The listed interfaces' methods and attributes can be accessed.""",
        required=False,
        value_type=GlobalObject()
        )

class IAllowSubdirective(Interface):
    """
    Declare a part of the class to be publicly viewable (that is,
    requires the zope.Public permission). Only one of the following
    two attributes may be used.
    """

    attributes = Tokens(
        title=u"Attributes",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interface",
        required=False,
        value_type=GlobalObject()
        )

class IDenySubdirective(Interface):
    """
    Declare a part of the class to be private (that is,
    can't be accessed through the web). Only one of the following
    two attributes may be used.
    """

    attributes = Tokens(
        title=u"Attributes",
        required=False,
        value_type=PythonIdentifier()
        )

    interface = Tokens(
        title=u"Interface",
        required=False,
        value_type=GlobalObject()
        )
