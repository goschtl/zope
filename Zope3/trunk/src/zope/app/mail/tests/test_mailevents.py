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

$Id: test_mailevents.py,v 1.2 2003/06/06 19:29:04 stevea Exp $
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.app.interfaces.mail import IMailer, IMailSentEvent
from zope.app.mail.event import MailSentEvent
from zope.interface import implements

class MailerStub:
    implements(IMailer)

    def send(self, fromaddr, toaddrs, message,
             hostname, port, username, password):
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.message = message
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password


class TestMailSentEvent(TestCase):

    def setUp(self):
        self.mailer = MailerStub()
        self.obj = MailSentEvent(self.mailer)

    def test_InterfaceConformity(self):
        self.assert_(IMailSentEvent.isImplementedBy(self.obj))

    def test_mailerAttr(self):
        self.assertEqual(self.mailer, self.obj.mailer)


def test_suite():
    return TestSuite((
        makeSuite(TestMailSentEvent),
        ))
