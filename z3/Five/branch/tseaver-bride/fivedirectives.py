##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Five ZCML directive schemas

$Id$
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens, PythonIdentifier

class IImplementsDirective(Interface):
    """State that a class implements something.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

    interface = Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=GlobalObject()
        )

class IViewableDirective(Interface):
    """State that a class can be viewed.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )


class IBridgeDirective(Interface):
    """Bridge from a Zope 2 interface to an equivalent Zope3 interface.
    """
    zope2 = GlobalObject(
        title=u"Zope2",
        required=True
        )

    package = GlobalObject(
        title=u"Target package",
        required=True
        )

    name = PythonIdentifier(
        title=u"Zope3 Interface name",
        description=u"If not supplied, the new interface will have the same "
                    u"name as the source interface.",
        required=False
        )

