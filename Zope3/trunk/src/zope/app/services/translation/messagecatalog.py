##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A simple implementation of a Message Catalog.

$Id: messagecatalog.py,v 1.3 2002/12/31 02:52:05 jim Exp $
"""
import time

from zodb.btrees.OOBTree import OOBTree
from persistence import Persistent
from zope.proxy.introspection import removeAllProxies
from zope.component.interfaces import IFactory
from zope.app.security.registries.registeredobject import RegisteredObject
from zope.i18n.interfaces import IMessageCatalog


class MessageCatalog(RegisteredObject, Persistent):

    __implements__ =  IMessageCatalog
    __class_implements__ = IFactory

    def __init__(self, language, domain="default"):
        """Initialize the message catalog"""
        super(MessageCatalog, self).__init__('', '', '')
        self._language = language
        self._domain = domain
        self._messages = OOBTree()

    def getMessage(self, id):
        'See IReadMessageCatalog'
        return removeAllProxies(self._messages[id][0])

    def queryMessage(self, id, default=None):
        'See IReadMessageCatalog'
        result = removeAllProxies(self._messages.get(id))
        if result is not None:
            result = result[0]
        else:
            result = default
        return result

    def getLanguage(self):
        'See IReadMessageCatalog'
        return self._language

    def getDomain(self):
        'See IReadMessageCatalog'
        return self._domain

    def getIdentifier(self):
        'See IReadMessageCatalog'
        return (self._language, self._domain)

    def getFullMessage(self, msgid):
        'See IWriteMessageCatalog'
        message = removeAllProxies(self._messages[msgid])
        return {'domain'   : self._domain,
                'language' : self._language,
                'msgid'    : msgid,
                'msgstr'   : message[0],
                'mod_time' : message[1]}

    def setMessage(self, msgid, message, mod_time=None):
        'See IWriteMessageCatalog'
        if mod_time is None:
            mod_time = int(time.time())
        self._messages[msgid] = (message, mod_time)

    def deleteMessage(self, msgid):
        'See IWriteMessageCatalog'
        del self._messages[msgid]

    def getMessageIds(self):
        'See IWriteMessageCatalog'
        return list(self._messages.keys())

    def getMessages(self):
        'See IWriteMessageCatalog'
        messages = []
        for message in self._messages.items():
            messages.append({'domain'   : self._domain,
                             'language' : self._language,
                             'msgid'    : message[0],
                             'msgstr'   : message[1][0],
                             'mod_time' : message[1][1]})
        return messages

    def getInterfaces(self):
        'See IFactory'
        return self.__implements__
