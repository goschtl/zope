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

$Id: test_directives.py,v 1.4 2003/06/23 15:45:40 alga Exp $
"""
import unittest
import threading

from cStringIO import StringIO

from zope.component import getService
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.configuration.xmlconfig import xmlconfig, Context, XMLConfig

from zope.app.component.metaconfigure import managerHandler, provideInterface
import zope.app.mail
import zope.app.interfaces.mail
from zope.app.mail.metaconfigure import provideMailer

template = """<zopeConfigure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:mail='http://namespaces.zope.org/mail'>
   xmlns:test='http://www.zope.org/NS/Zope3/test'>
   %s
   </zopeConfigure>"""


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
        PlacelessSetup.setUp(self)
        managerHandler('defineService', 'Mail',
                       zope.app.interfaces.mail.IMailService)
        provideInterface('zope.app.interfaces.mail.IMailService',
                         zope.app.interfaces.mail.IMailService)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.mail)()
        from zope.app.mail import service
        self.orig_maildir = service.Maildir
        service.Maildir = MaildirStub

    def tearDown(self):
        from zope.app.mail import service
        service.Maildir = self.orig_maildir

    def testQueuedService(self):
        threads = threading.activeCount()
        provideMailer("smtp", object())
        xmlconfig(StringIO(template % (
            '''
            <mail:queuedService name="Mail"
               queuePath="/path/to/mailbox"
               mailer="smtp"
               permission="zope.Public" />
            '''
            )), None, Context([], zope.app.mail))
        service = getService(None, 'Mail')
        self.assertEqual('QueuedMailService', service.__class__.__name__)
        self.assertEqual('/path/to/mailbox', service.queuePath)
        self.assertEqual(threading.activeCount(), threads + 1)

    def testDirectService(self):
        testMailer = object()
        provideMailer('test.mailer', testMailer)
        xmlconfig(StringIO(template % (
            '''
            <mail:directService name="Mail"
               mailer="test.mailer"
               permission="zope.Public" />
            '''
            )), None, Context([], zope.app.mail))
        service = getService(None, 'Mail')
        self.assertEqual('DirectMailService', service.__class__.__name__)
        self.assert_(testMailer is service.mailer)


    def testSendmailMailer(self):
        from zope.app.interfaces.mail import ISendmailMailer
        from zope.app.mail.metaconfigure import queryMailer
        xmlconfig(StringIO(template % (
            '''
            <mail:sendmailMailer id="Sendmail"
               command="/usr/lib/sendmail -oem -oi -f %(from)s %(to)s" />
            '''
            )), None, Context([], zope.app.mail))
        self.assert_(ISendmailMailer.isImplementedBy(queryMailer("Sendmail")))

    def testSMTPMailer(self):
        from zope.app.interfaces.mail import ISMTPMailer
        from zope.app.mail.metaconfigure import queryMailer
        xmlconfig(StringIO(template % (
            '''
            <mail:smtpMailer id="smtp"
               hostname="localhost"
               port="25"
               username="zope3"
               password="xyzzy"
               />
            '''
            )), None, Context([], zope.app.mail))

        xmlconfig(StringIO(template % (
            '''
            <mail:smtpMailer id="smtp2"
              hostname="smarthost"
            />
            '''
            )), None, Context([], zope.app.mail))
        self.assert_(ISMTPMailer.isImplementedBy(queryMailer("smtp")))

def test_suite():
    return unittest.makeSuite(DirectivesTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
