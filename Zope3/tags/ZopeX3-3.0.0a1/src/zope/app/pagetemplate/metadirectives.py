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
"""ZCML configuration directives for configuring the default zope:
namespace in TALES.

$Id$
"""

from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine

class INamespaceDirective(Interface):
    """
    Define a new tales namespace
     
    A namespace is defined by providing a prefix and an interface. A
    handler for the namespace will be obtained by looking up an
    adapter for the given interface.
    """

    prefix = TextLine(
        title=u"The prefix used in tales expressions.",
        description=u"""
        For example, if the prefix is "dc", then a tales expression
        would look like: ``foo/bar/dc:title``.""",
        required=True
        )

    interface = GlobalObject(
        title=u"The namespace interface",
        description=u"""
        This is an interface that the namespace must provide.  we'll
        get the namespace by getting an adapter for this
        interface.""",
        required=True
        )

class IExpressionTypeDirective(Interface):
    """Register a new TALES expression type"""

    name = TextLine(
        title=u"Name",
        description=u"""Name of the expression. This will also be used
        as the prefix in actual TALES expressions.""",
        required=True
        )

    handler = GlobalObject(
        title=u"Handler",
        description=u"""Handler is class that implements
        zope.tales.interfaces.ITALESExpression.""",
        required=True
        )
