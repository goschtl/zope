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

"""Permission change view

Use when updating the permissions on the process definition.

$Id:$
"""

from zope.app import zapi
from zope.event import notify

from zope.app.workflow.stateful.pd_events import \
     ProcessDefinitionAddPermissionsEvent, ProcessDefinitionDelPermissionsEvent

class PermissionChangeView:
    """Permission Change view

    The permissions are changed on the process definition
    We send a ProcessDefinitionPermissionsChangedEvent
    """

    def __init__(self, context, request):
        """Constructor
        """
        self.context=context
        self.request=request

    def sendProcessDefinitionAddPermissionsEvent(self,
                                                 permissions_to_add):
        """Add a permission
        """

        event = ProcessDefinitionAddPermissionsEvent(self.context,
                                                     permissions_to_add)
        notify(event)

        #
        # Redirect on the context default view
        # Maybe we would like to define the redirection somewhere
        #

        redirect_url = zapi.getView(self.context, 'absolute_url', self.request)
        self.request.response.redirect(redirect_url)

    def sendProcessDefinitionDelPermissionsEvent(self,
                                                 permissions_to_remove):
        """Del a permission
        """

        event = ProcessDefinitionDelPermissionsEvent(self.context,
                                                     permissions_to_remove)
        notify(event)

        #
        # Redirect on the context default view
        # Maybe we would like to define the redirection somewhere
        #

        redirect_url = zapi.getView(self.context, 'absolute_url', self.request)
        self.request.response.redirect(redirect_url)
