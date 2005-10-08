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
"""Portlet preferences implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.schema import Bool

from zope.app.i18n import ZopeMessageIDFactory as _



class IPortletPreference(Interface):
    """User Preference for a single portlet."""

    expanded = Bool(
        title=_(u"Show portlet expanded"),
        description=_(u"Shows portlet in its inital state expanded.")
        )

    state = Choice(
        title=_(u"Portlet state"),
        description=_(u"Render portlt in the given mode.")
        )