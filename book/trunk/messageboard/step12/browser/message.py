##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser Views for IMessage

$Id: message.py,v 1.3 2003/12/13 17:24:36 srichter Exp $
"""
from zope.i18n import MessageIDFactory

from zope.app import zapi
from zope.app.dublincore.interfaces import ICMFDublinCore

from book.messageboard.interfaces import IMessage
from book.messageboard.interfaces import IMailSubscriptions

_ = MessageIDFactory('messageboard')

class MessageDetails:

    def author(self):
        """Get user who last modified the Message."""
        creators = ICMFDublinCore(self.context).creators
        if not creators:
            return _('unknown')
        return creators[0]

    def modified(self):
        """Get last modification date."""
        date = ICMFDublinCore(self.context).modified
        if date is None:
            date = ICMFDublinCore(self.context).created
        if date is None:
            return ''
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        return formatter.format(date)

    def parent_info(self):
        """Get the parent of the message"""
        parent = zapi.getParent(self.context)
        if not IMessage.providedBy(parent):
            return None
        return {'name': zapi.name(parent), 'title': parent.title}


class MailSubscriptions:

    def subscriptions(self):
        return IMailSubscriptions(self.context).getSubscriptions()

    def change(self):
        if 'ADD' in self.request:
            emails = self.request['emails'].split('\n')
            IMailSubscriptions(self.context).addSubscriptions(emails)
        elif 'REMOVE' in self.request:
            emails = self.request['remails']
            if isinstance(emails, (str, unicode)):
                emails = [emails]
            IMailSubscriptions(self.context).removeSubscriptions(emails)

        self.request.response.redirect('./@@subscriptions.html')
