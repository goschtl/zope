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

$Id: mail.py,v 1.2 2003/08/01 11:14:10 srichter Exp $
"""
from bugtracker import TrackerMessageID as _
from bugtracker.interfaces import IBug, IMailSubscriptions

class MailSubscriptions:

    def subscriptions(self):
        return IMailSubscriptions(self.context).getSubscriptions()

    def update(self):
        status = None
        if 'ADD' in self.request:
            emails = self.request['emails'].strip().split('\n')
            IMailSubscriptions(self.context).addSubscriptions(emails)
            status = _('Subscribers successfully added: $emails')
            status.mapping = {'emails': ', '.join(emails)}
        elif 'REMOVE' in self.request:
            emails = self.request['remails']
            if isinstance(emails, (str, unicode)):
                emails = [emails]
            IMailSubscriptions(self.context).removeSubscriptions(emails)
            status = _('Subscribers successfully deleted: $emails')
            status.mapping = {'emails': ', '.join(emails)}

        return status
