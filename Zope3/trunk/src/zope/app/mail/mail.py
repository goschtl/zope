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

$Id: mail.py,v 1.2 2003/05/19 10:03:37 ryzaja Exp $
"""
from smtplib import SMTP

from zope.app.interfaces.mail import IAsyncMailService, IMailer, IMailSentEvent
from zope.app.event import publish

class AsyncMailService:
    __doc__ = IAsyncMailService.__doc__

    __implements__ = IAsyncMailService


    # See zope.app.interfaces.services.mail.IMailService
    hostname = u''

    # See zope.app.interfaces.services.mail.IMailService
    port = 25

    # See zope.app.interfaces.services.mail.IMailService
    username = None

    # See zope.app.interfaces.services.mail.IMailService
    password = None

    def __init__(self):
        """Initialize the object."""
        self.__mailers = {}
        self.__default_mailer = ''

    def createMailer(self, name):
        "See zope.app.interfaces.services.mail.IAsyncMailService"
        return self.__mailers[name]()

    def getMailerNames(self):
        "See zope.app.interfaces.services.mail.IAsyncMailService"
        return self.__mailers.keys()

    def getDefaultMailerName(self):
        "See zope.app.interfaces.services.mail.IAsyncMailService"
        return self.__default_mailer

    def send(self, fromaddr, toaddrs, message, mailer=None):
        "See zope.app.interfaces.services.mail.IMailService"
        if mailer is None:
            mailer = self.createMailer(self.getDefaultMailerName)
        # XXX: should be called in new thread:should we use thread or async?
        mailer.send(fromaddr, toaddrs, message, self.hostname, self.port,
                    self.username, self.password)

    def provideMailer(self, name, klass, default=False):
        """Add a new mailer to the service."""
        self.__mailers[name] = klass
        if default:
            self.__default_mailer = name

