##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet metadirective

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

from zope.schema import TextLine
from zope.schema import Int

from zope.app.security.fields import Permission
from zope.app.component.fields import LayerField

from zope.configuration.fields import GlobalObject, GlobalInterface



class IPageletDirective(Interface):
    """TODO: write documentation."""

    name = TextLine(
        title=u"The name of the pagelet.",
        description=u"The name of the pagelet has to be unique",
        required=True
        )

    slot = GlobalInterface(
        title=u"slot",
        description=u"The slot interface this pagelet is for.",
        required=True
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the pagelet.",
        required=True
        )

    for_ = GlobalInterface(
        title=u"for",
        description=u"The interface this pagelet is for (default IInterface)",
        required=False
        )

    layer = LayerField(
        title=u"The layer the pagelet should be found in",
        description=u"""
            For information on layers, see the documentation for the skin
            directive. Defaults to "default".""",
        required=False
        )

    view = GlobalInterface(
        title=u"view",
        description=u"""
            The interface of the view this pagelet is for. (default IView)""",
        required=False
        )

    weight = Int(
        title=u"weight",
        description=u"Integer key for sorting pagelets in the same slot.",
        required=False
        )

    template = TextLine(
        title=u"Page template.",
        description=u"""
            Refers to a file containing a page template (must end in
            extension '.pt').""",
        required=False
        )
