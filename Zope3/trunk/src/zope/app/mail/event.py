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
"""Collection of possible Mail Events.

$Id: event.py,v 1.3 2003/06/23 15:45:39 alga Exp $
"""
from zope.app.interfaces.mail import IMailSentEvent, IMailErrorEvent
from zope.interface import implements

__metaclass__ = type


class MailSentEvent:
    __doc__ = IMailSentEvent.__doc__

    implements(IMailSentEvent)

    def __init__(self, messageId):
        self.messageId = messageId


class MailErrorEvent:
    __doc__ = IMailErrorEvent.__doc__

    implements(IMailErrorEvent)

    def __init__(self, messageId, errorMessage):
        self.messageId = messageId
        self.errorMessage = errorMessage
