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
$Id: metadirectives.py,v 1.2 2004/05/18 13:58:57 faassen Exp $
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, \
     PythonIdentifier, MessageID
from zope.schema import TextLine, Id

class IBasicComponentInformation(Interface):

    component = GlobalObject(
        title=u"Component to be used",
        required=False
        )

    factory = GlobalObject(
        title=u"Factory",
        required=False
        )

class IServiceTypeDirective(Interface):

    id = TextLine(
        title=u"ID of the service type",
        required=True
        )

    interface = GlobalObject(
        title=u"Interface of the service type",
        required=True
        )

class IServiceDirective(IBasicComponentInformation):
    """
    Register a service
    """

    serviceType = TextLine(
        title=u"ID of service type",
        required=True
        )

class IInterfaceDirective(Interface):
    """
    Define an interface
    """

    interface = GlobalObject(
        title=u"Interface",
        required=True
        )

    type = GlobalObject(
        title=u"Interface type",
        required=False
        )

class IAdapterDirective(Interface):
    """
    Register an adapter
    """

    factory = Tokens(
        title=u"Adapter factory/factories",
        description=u"""A list of factories (usually just one) that create the
        adapter instance.""",
        required=True,
        value_type=GlobalObject()
        )

    provides = GlobalObject(
        title=u"Interface the component provides",
        description=u"""This attribute specifes the interface the adapter
        instance must provide.""",
        required=True
        )

    for_ = Tokens(
        title=u"Specifications to be adapted",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=GlobalObject(missing_value=object())
        )

    name = TextLine(
        title=u"Name",
        description=u"""Adapters can have names. This attribute allows you to
        specify the name for this adapter.""",
        required=False
        )

class IUtilityDirective(IBasicComponentInformation):
    """
    Register a utility
    """

    provides = GlobalObject(
        title=u"Interface the component provides",
        required=True
        )

    name = TextLine(
        title=u"Name",
        required=False
        )

class IBaseDefineDirective(Interface):
    """Define a new security object."""

    id = Id(
        title=u"Id",
        description=u"Id as which this object will be known and used.",
        required=True)

    title = MessageID(
        title=u"Title",
        description=u"Provides a title for the object.",
        required=True)

    description = MessageID(
        title=u"Description",
        description=u"Provides a description for the object.",
        required=False)


class IDefinePermissionDirective(IBaseDefineDirective):
    """Define a new permission."""
