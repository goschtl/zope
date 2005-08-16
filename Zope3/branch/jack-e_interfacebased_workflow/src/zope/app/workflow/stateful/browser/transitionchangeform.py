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

"""Transition Change Form View

$Id: $
"""

from zope.app import zapi
from zope.event import notify
from zope.app.workflow.stateful.transition_events import \
     TransitionUserTriggeredEvent

class TransitionChangeForm:
    """Transition Change Form view

    The transition change form will have as form action the
    sendTransistionEvent method
    """

    def __init__(self, context, request):
        """Constructor
        """
        self.context=context
        self.request=request

    def sendTransitionUserTriggeredEvent(self, transition='', **kw):
        """Send Transition Event

        Construct a TransitionUserTrigerred event and then notify
        """

        event = TransitionUserTriggeredEvent(object=self.context,
                                             transition=transition,
                                             kwargs=kw)
        notify(event)

        #
        # Redirect on the context default view
        # Maybe we would like to define the redirection somewhere
        #

        redirect_url = zapi.getView(self.context, 'absolute_url', self.request)
        self.request.response.redirect(redirect_url)
