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
"""Portlet state handler implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app import zapi
import zope.interface
from zope.app.preference import preference

from zope.contentprovider.interfaces import IContentProviderType
from zope.portlet import interfaces
from zope.portlet.preference import IPortletPreference


class PreferenceStateHandler(object):
    """State handler based on preferences."""

    zope.interface.implements(interfaces.IStateHandler)

    def __init__(self, context):
        self.context = context

    def setState(self, value, name):
        """Set the state of the portlet; the name parameter is the name
           of the portlet in the portlet manager.
        """
        cpType = zapi.queryType(self.context, IContentProviderType)
        cpTypeName = cpType.__module__ + '.' + cpType.__name__
        settings = preference.PreferenceGroup(
            cpTypeName + '/' + name,
            schema=IPortletPreference,
            title=u"Portlet User Settings",
            description=u""
            )
        settings.state = value

    def getState(self, name):
        """Return the state of the portlet; the name parameter is the name
           of the portlet in the portlet manager.
        """
        cpType = zapi.queryType(self.context, IContentProviderType)
        cpTypeName = cpType.__module__ + '.' + cpType.__name__
        settings = preference.PreferenceGroup(
            cpTypeName + '/' + name,
            schema=IPortletPreference,
            title=u"Portlet User Settings",
            description=u""
            )
        return settings.state



