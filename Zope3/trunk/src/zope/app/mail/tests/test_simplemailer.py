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

$Id: test_simplemailer.py,v 1.1 2003/04/16 13:45:44 srichter Exp $
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.app.interfaces.mail import IAsyncMailService, IMailer, IMailSentEvent
from zope.app.mail.event import MailSentEvent 
import zope.app.mail.mailer 

from zope.component.tests.placelesssetup import PlacelessSetup
import zope.app.event.tests.placelesssetup as event_setup

class SMTPStub(TestCase):

    hostname = ''
    port = 25
    username = ''
    password = ''
    fromaddr = ''
    toaddrs = ''
    message = ''

    def __init__(self, hostname, port=25):
        self.assertEqual(self.hostname, hostname)
        self.assertEqual(self.port, port)

    def set_debuglevel(self, level):
        pass

    def login(self, username, password):
        self.assertEqual(self.username, username)
        self.assertEqual(self.password, password)


    def sendmail(self, fromaddr, toaddrs, message):
        self.assertEqual(self.fromaddr, fromaddr)
        self.assertEqual(self.toaddrs, toaddrs)
        self.assertEqual(self.message, message)

    def quit(self):
        pass



class TestSimpleMailer(event_setup.PlacelessSetup, PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        event_setup.PlacelessSetup.setUp(self)
        self.obj = zope.app.mail.mailer.SimpleMailer()

    def test_InterfaceConformity(self):
        self.assert_(IMailer.isImplementedBy(self.obj))

    def test_send(self):
        SMTPStub.hostname = 'localhost'
        SMTPStub.port = 1025
        SMTPStub.username = 'srichter'
        SMTPStub.password = 'blah'
        SMTPStub.fromaddr = 'foo@bar.com'
        SMTPStub.toaddrs = ['blah@bar.com', 'booh@bar.com']
        SMTPStub.message = 'This is the message'
        zope.app.mail.mailer.SMTP = SMTPStub
        
        self.obj.send('foo@bar.com', ['blah@bar.com', 'booh@bar.com'],
                      'This is the message', 'localhost', 1025,
                      'srichter', 'blah');
        self.assertEqual(MailSentEvent, event_setup.events[0].__class__)
        

def test_suite():
    return TestSuite((
        makeSuite(TestSimpleMailer),
        ))
