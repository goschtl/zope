##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

from zope import component

from zope.sendmail.interfaces import IMailDelivery

from email.MIMEText import MIMEText
import email.Charset
email.Charset.add_charset('utf-8', email.Charset.SHORTEST, None, None)
from datetime import datetime


def sendmail(subject, fromaddr, toaddrs, body, replyTo=None, bodytype='plain'):

    if isinstance(fromaddr, tuple):
        fromaddr = '%s <%s>'% fromaddr

    recipients = []
    for toaddr in toaddrs:
        if isinstance(toaddr, tuple):
            toaddr = '%s <%s>'% toaddr
        recipients.append(toaddr)

    message = MIMEText(body.encode('utf-8'), bodytype, 'utf-8')
    message['Subject'] = subject
    message['From'] = fromaddr
    if replyTo:
        message['Reply-To'] = replyTo
    message['To'] = ', '.join(recipients)
    message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
    mailer = component.getUtility(IMailDelivery, name='lovely-mail-delivery')
    mailer.send(fromaddr, recipients, message.as_string())

