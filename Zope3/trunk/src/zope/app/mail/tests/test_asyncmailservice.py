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

$Id: test_asyncmailservice.py,v 1.2 2003/05/01 19:35:24 faassen Exp $
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.app.interfaces.mail import IAsyncMailService, IMailer
from zope.app.mail.service import AsyncMailService


class MailerStub:
    __implements__ = IMailer

    def send(self, fromaddr, toaddrs, message,
             hostname, port, username, password):
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.message = message
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password


class TestAsyncMailService(TestCase):

    def setUp(self):
        self.obj = AsyncMailService()
        self.obj.provideMailer('dummy', MailerStub, True)

    def testInterfaceConformity(self):
        self.assert_(IAsyncMailService.isImplementedBy(self.obj))

    def test_createMailer(self):
        self.assertEqual(MailerStub, self.obj.createMailer('dummy').__class__)
        self.assertRaises(KeyError, self.obj.createMailer, ('foo',))

    def test_getMailerNames(self):
        self.assertEqual(['dummy'], self.obj.getMailerNames())
        self.obj.provideMailer('dummy2', MailerStub)
        names = self.obj.getMailerNames()
        names.sort()
        self.assertEqual(['dummy', 'dummy2'], names)

    def test_getDefaultMailerName(self):
        self.assertEqual('dummy', self.obj.getDefaultMailerName())

    def test_send(self):
        # Just test API conformity
        self.obj.send('foo@bar.com', ['blah@bar.com'], 'This is a message')
        mailer = MailerStub()
        self.obj.send('foo@bar.com', ['blah@bar.com'], 'This is a message',
                      mailer)
        self.assertEqual('foo@bar.com', mailer.fromaddr)
        self.assertEqual(['blah@bar.com'], mailer.toaddrs)
        self.assertEqual('This is a message', mailer.message)

    

def test_suite():
    return TestSuite((
        makeSuite(TestAsyncMailService),
        ))
