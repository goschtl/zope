##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Test the gts ZCML namespace directives.

$Id: test_directives.py,v 1.9 2003/11/27 13:59:21 philikon Exp $
"""
import os
import unittest
import threading
import time

from zope.app.component.metaconfigure import managerHandler, provideInterface
from zope.app.interfaces.mail import IMailService, ISMTPMailer, ISendmailMailer
from zope.app.mail.metaconfigure import provideMailer, queryMailer
from zope.app.mail.service import QueueProcessorThread
from zope.app.mail import service
from zope.component import getService
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration import xmlconfig
import zope.app.mail.tests


class MaildirStub:

    def __init__(self, path, create=False):
        self.path = path
        self.create = create

    def __iter__(self):
        return iter(())

    def newMessage(self):
        return None


class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        managerHandler('defineService', 'Mail', IMailService)
        managerHandler('defineService', 'Mail2', IMailService)
        provideInterface('zope.app.interfaces.mail.IMailService', IMailService)
        provideMailer("test.smtp", object())
        self.testMailer = object()
        provideMailer('test.mailer', self.testMailer)
        self.context = xmlconfig.file("mail.zcml", zope.app.mail.tests)
        self.orig_maildir = service.Maildir
        service.Maildir = MaildirStub
        

    def tearDown(self):
        service.Maildir = self.orig_maildir

        # Tear down the mail queue processor thread.
        # Give the other thread a chance to start:
        time.sleep(0.001)
        threads = list(threading.enumerate())
        for thread in threads:
            if isinstance(thread, QueueProcessorThread):
                thread.stop()
                thread.join()
                
        

    def testQueuedService(self):
        service = getService(None, 'Mail')
        self.assertEqual('QueuedMailService', service.__class__.__name__)
        testdir = os.path.dirname(zope.app.mail.tests.__file__)
        self.assertEqual(os.path.join(testdir, 'mailbox'),
                         service.queuePath)

    def testDirectService(self):
        service = getService(None, 'Mail2')
        self.assertEqual('DirectMailService', service.__class__.__name__)
        self.assert_(self.testMailer is service.mailer)


    def testSendmailMailer(self):
        self.assert_(ISendmailMailer.isImplementedBy(queryMailer("Sendmail")))

    def testSMTPMailer(self):
        self.assert_(ISMTPMailer.isImplementedBy(queryMailer("smtp")))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
