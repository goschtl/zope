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
from zope.configuration.fields import GlobalObject, Tokens

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

class ITraversableDirective(Interface):
    """State that a class traversal can be controlled by the use of
    an ITraverser adapter.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

class IViewableDirective(Interface):
    """State that an instance class can be viewed directly by
    choosing the default view through a IBrowserDefault adapter.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

