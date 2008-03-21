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
import logging, sys

from zope import interface, component
from zope.component import getUtility
from zope.session.interfaces import ISession
from zope.publisher.interfaces.browser import IBrowserRequest

from interfaces import SESSIONKEY, IMessageFactory, IStatusMessage


def log_exc(msg='', subsystem='z3ext.statusmessage'):
    log = logging.getLogger(subsystem)
    log.log(logging.ERROR, msg, exc_info=sys.exc_info())


@component.adapter(IBrowserRequest)
@interface.implementer(IStatusMessage)
def getSessionMessageService(request):
    try:
        session = ISession(request, None)
        if session is not None:
            return SessionMessageService(session)
    except:
        pass


class SessionMessageService(object):
    """ message service that store messages in session """
    interface.implements(IStatusMessage)

    def __init__(self, session):
        self.session = session

    def add(self, text, type='info'):
        factory = getUtility(IMessageFactory, type)
        self.addMessage(factory(text))

    def addMessage(self, message):
        data = self.session[SESSIONKEY]

        try:
            messages = data.get('messages', [])
            messages.append(message)
            data['messages'] = messages
        except Exception, e:
            log_exc(str(e))

    def list(self):
        data = self.session[SESSIONKEY]
        return data.get('messages', ())

    def clear(self):
        data = self.session[SESSIONKEY]

        messages = data.get('messages')
        if messages is not None:
            del data['messages']
            return messages
        else:
            return ()

    def hasMessages(self):
        data = self.session[SESSIONKEY]

        messages = data.get('messages')
        if messages is not None:
            return bool(messages)
        else:
            return False
