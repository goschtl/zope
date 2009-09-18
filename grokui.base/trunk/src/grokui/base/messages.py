# -*- coding: utf-8 -*-

import grok

from zope.interface import Interface
from zope.component import getUtility
from z3c.flashmessage.message import PersistentMessage
from z3c.flashmessage.sources import SessionMessageSource
from z3c.flashmessage.receiver import GlobalMessageReceiver
from z3c.flashmessage.interfaces import IMessageReceiver, IMessageSource


class AdminMessageSource(grok.GlobalUtility):
    """Source for the administration messages
    """
    grok.name('admin')
    grok.implements(IMessageSource)

    message = None

    def send(self, message, type='admin'):
        self.message = PersistentMessage(message, type)

    def list(self, type=None):
        if self.message is None:
            return
        if type is None or self.message.type == type:
            yield self.message

    def delete(self, message):
        if message is self.message:
            self.message = None
        else:
            raise KeyError(message)


class Messages(grok.View):
    """Messages render.
    """
    grok.context(Interface)

    @property
    def messages(self):
        receiver = getUtility(IMessageReceiver)
        return receiver.receive()


grok.global_utility(GlobalMessageReceiver)
grok.global_utility(SessionMessageSource, name='session')

