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
from zope.configuration.fields import GlobalObject, Tokens, Bool
from zope.schema import TextLine

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

    force = Bool(
        title=u"Force",
        description=u"Force making the class viewable",
        required=False,
        default=False)

class ISkinDirectoryDirective(Interface):
    """Register each file in a skin directory as a resource
    """

    for_ = GlobalObject(
        title=u"The interface this view is for.",
        required=False
        )

    module = GlobalObject(
        title=u"Module",
        required=True
        )

    directory = TextLine(
        title=u"Directory",
        description=u"The directory containing the resource data.",
        required=True
        )
