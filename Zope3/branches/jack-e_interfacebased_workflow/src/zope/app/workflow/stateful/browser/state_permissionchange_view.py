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

"""State Permission Change View

Use when updating the permissions roles mapping in the state

$Id:$
"""

from zope.app import zapi
from zope.event import notify

from zope.app.workflow.stateful.state_events import \
     StatePermissionsRolesMappingUpdateEvent

class PermissionsRolesMappingChangeView:
    """Permissions Roles Mapping Change View

    The permissions roles mapping on the state has been updated
    """

    def __init__(self, context, request):
        """Constructor
        """
        self.context=context
        self.request=request

    def sendStateUpdatePermissionsRolesMappingEvent(self):
        """Update the permissions roles mapping on the state
        """

        # XXX Extract the form elements we need
        mapping = self.request.form
        event = StatePermissionsRolesMappingUpdateEvent(self.context,
                                                        mapping)

        #
        # Sending an event is really cool since we will be able
        # to do actions somehow for what we want to realize after
        # the update of the mapping on the state.
        # Basically just defining subscribers to this event for doing a
        # particulat job.
        #

        notify(event)

        #
        # Redirect on the context default view
        # Maybe we would like to define the redirection somewhere
        #

        redirect_url = zapi.getView(self.context, 'absolute_url', self.request)
        self.request.response.redirect(redirect_url)
