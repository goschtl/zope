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
"""Viewlet metadirective

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.configuration.fields import GlobalInterface
from zope.schema import Int

from zope.app.publisher.browser import metadirectives


class IPortletDirective(metadirectives.IPagesDirective,
                        metadirectives.IViewPageSubdirective):
    """A directive to register a new portlet.

    Portlet registrations are very similar to page registrations, except that
    they are additionally qualified by the type and view they are used for. An
    additional `weight` attribute is specified that is intended to coarsly
    control the order of the portlets.
    """

    viewletType = GlobalInterface(
        title=u"type",
        description=u"The type interface of this portlet.",
        required=True)

    view = GlobalInterface(
        title=u"view",
        description=u"The interface of the view this portlet is for. "
                    u"(default IBrowserView)""",
        required=False)

    weight = Int(
        title=u"weight",
        description=u"Integer key for sorting portlet in the same region.",
        required=False)
