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

$Id: event.py,v 1.2 2003/06/06 19:29:03 stevea Exp $
"""
from zope.app.interfaces.mail import IMailSentEvent
from zope.interface import implements


class MailSentEvent:
    __doc__ = IMailSentEvent.__doc__

    implements(IMailSentEvent)

    def __init__(self, mailer):
        self.mailer = mailer 
