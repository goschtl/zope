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
"""MailService Implementation

Simple implementation of the MailService, Mailers and MailEvents.

$Id: mailer.py,v 1.4 2003/06/06 19:29:03 stevea Exp $
"""
from smtplib import SMTP

from zope.app.interfaces.mail import IMailer, IBatchMailer
from zope.app.event import publish
from zope.app.mail.event import MailSentEvent
from zope.interface import implements


class SimpleMailer:
    __doc__ = IMailer.__doc__

    implements(IMailer)

    def send(self, fromaddr, toaddrs, message,
             hostname, port, username, password):
        "See zope.app.interfaces.services.mail.IMailer"
        server = SMTP(hostname, port)
        server.set_debuglevel(0)
        if username is not None and password is not None:
            server.login(username, password)
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()
        publish(self, MailSentEvent(self))


class BatchMailer:
    __doc__ = IBatchMailer.__doc__

    implements(IBatchMailer)

    # See zope.app.interfaces.mail.IBatchMailer
    batchDelay = 5000

    # See zope.app.interfaces.mail.IBatchMailer
    batchSize = 5

    def send(self, fromaddr, toaddrs, message,
             hostname, port, username, password):
        "See zope.app.interfaces.mail.IMailer"
        server = SMTP(hostname, port)
        server.set_debuglevel(0)
        if username is not None and password is not None:
            server.login(username, password)
        recv = list(toaddrs)
        batch = []
        while recv:
            while len(batch) < self.batchSize and recv:
                batch.append(recv.pop())
            server.sendmail(fromaddr, batch, message)
            batch = []
            time.sleep(self.batchDelay/1000.0)
        server.quit()
        publish(self, MailSentEvent(self))
