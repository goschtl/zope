##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id$
"""
from zope import interface, component
from zope.component import getAdapter
from zope.session.interfaces import ISession
from zope.publisher.interfaces.browser import IBrowserRequest

from interfaces import SESSIONKEY, IMessage, IStatusMessage


class MessageService(object):
    """ message service """
    component.adapts(IBrowserRequest)
    interface.implements(IStatusMessage)

    def __init__(self, request):
        self.request = request

    def add(self, text, type='info'):
        message = getAdapter(self.request, IMessage, type)

        session = ISession(self.request, None)
        if session is not None:
            try:
                data = session[SESSIONKEY]
                messages = data.get('messages', [])
                messages.append(message.render(text))
                data['messages'] = messages
            except Exception, e:
                print e

    def clear(self):
        session = ISession(self.request, None)
        if session is not None:
            data = session.get(SESSIONKEY)
            if data is not None:
                messages = data.get('messages')
                if messages:
                    del data['messages']
                    return messages
        return ()

    def messages(self):
        session = ISession(self.request, None)
        if session is not None:
            data = session.get(SESSIONKEY)
            if data is not None:
                messages = data.get('messages')
                if messages:
                    return messages
        return ()

    def __nonzero__(self):
        return bool(self.messages())
