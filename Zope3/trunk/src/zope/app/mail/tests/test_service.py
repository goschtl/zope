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

$Id: test_service.py,v 1.3 2003/08/17 06:07:17 philikon Exp $
"""
import os.path
from tempfile import mktemp
from unittest import TestCase, TestSuite, makeSuite

from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.app.interfaces.mail import IMailer

from transaction import get_transaction

__metaclass__ = type


class MailerStub:

    implements(IMailer)
    def __init__(self, *args, **kw):
        self.sent_messages = []

    def send(self, fromaddr, toaddrs, message):
        self.sent_messages.append((fromaddr, toaddrs, message))


class TestMailDataManager(TestCase):

    def testInterface(self):
        from transaction.interfaces import IDataManager
        from zope.app.mail.service import MailDataManager
        manager = MailDataManager(object, (1, 2))
        verifyObject(IDataManager, manager)
        self.assertEqual(manager.callable, object)
        self.assertEqual(manager.args, (1, 2))


class TestDirectMailService(TestCase):

    def testInterface(self):
        from zope.app.interfaces.mail import IDirectMailService
        from zope.app.mail.service import DirectMailService
        mailer = MailerStub()
        service = DirectMailService(mailer)
        verifyObject(IDirectMailService, service)
        self.assertEqual(service.mailer, mailer)

    def testSend(self):
        from zope.app.mail.service import DirectMailService
        mailer = MailerStub()
        service = DirectMailService(mailer)
        fromaddr = 'Jim <jim@example.com'
        toaddrs = ('Guido <guido@example.com>',
                   'Steve <steve@examplecom>')
        opt_headers = ('From: Jim <jim@example.org>\n'
                       'To: some-zope-coders:;\n'
                       'Date: Mon, 19 May 2003 10:17:36 -0400\n'
                       'Message-Id: <20030519.1234@example.org>\n')
        message =     ('Subject: example\n'
                       '\n'
                       'This is just an example\n')

        msgid = service.send(fromaddr, toaddrs, opt_headers + message)
        self.assertEquals(msgid, '20030519.1234@example.org')
        self.assertEquals(mailer.sent_messages, [])
        get_transaction().commit()
        self.assertEquals(mailer.sent_messages,
                          [(fromaddr, toaddrs, opt_headers + message)])

        mailer.sent_messages = []
        msgid = service.send(fromaddr, toaddrs, message)
        self.assert_('@' in msgid)
        self.assertEquals(mailer.sent_messages, [])
        get_transaction().commit()
        self.assertEquals(len(mailer.sent_messages), 1)
        self.assertEquals(mailer.sent_messages[0][0], fromaddr)
        self.assertEquals(mailer.sent_messages[0][1], toaddrs)
        self.assert_(mailer.sent_messages[0][2].endswith(message))
        new_headers = mailer.sent_messages[0][2][:-len(message)]
        self.assert_(new_headers.find('Message-Id: <%s>' % msgid) != -1)

        mailer.sent_messages = []
        msgid = service.send(fromaddr, toaddrs, opt_headers + message)
        self.assertEquals(mailer.sent_messages, [])
        get_transaction().abort()
        self.assertEquals(mailer.sent_messages, [])


class MaildirWriterStub:

    data = ''
    commited_messages = []  # this list is shared among all instances
    aborted_messages = []   # this one too

    def write(self, str):
        self.data += str

    def writelines(self, seq):
        self.data += ''.join(seq)

    def commit(self):
        self._commited = True
        self.commited_messages.append(self.data)

    def abort(self):
        self._aborted = True
        self.aborted_messages.append(self.data)


class MaildirStub:

    def __init__(self, path, create=False):
        self.path = path
        self.create = create
        self.msgs = []
        self.files = []

    def __iter__(self):
        return iter(self.files)

    def newMessage(self):
        m = MaildirWriterStub()
        self.msgs.append(m)
        return m

class LoggerStub:

    def __init__(self):
        self.infos = []
        self.errors = []

    def getLogger(name):
        return self

    def error(self, msg, *args, **kwargs):
        self.errors.append((msg, args, kwargs))

    def info(self, msg, *args, **kwargs):
        self.infos.append((msg, args, kwargs))

class BizzarreMailError(IOError):
    pass

class BrokenMailerStub:

    implements(IMailer)
    def __init__(self, *args, **kw):
        pass

    def send(self, fromaddr, toaddrs, message):
        raise BizzarreMailError("bad things happened while sending mail")

class TestQueuedMailService(TestCase):

    def setUp(self):
        import zope.app.mail.service as mail_service_module
        self.mail_service_module = mail_service_module
        self.old_Maildir = mail_service_module.Maildir
        mail_service_module.Maildir = MaildirStub

    def tearDown(self):
        self.mail_service_module.Maildir = self.old_Maildir

    def testInterface(self):
        from zope.app.interfaces.mail import IQueuedMailService
        from zope.app.mail.service import QueuedMailService
        service = QueuedMailService('/path/to/mailbox')
        verifyObject(IQueuedMailService, service)
        self.assertEqual(service.queuePath, '/path/to/mailbox')

    def testSend(self):
        from zope.app.mail.service import QueuedMailService
        service = QueuedMailService('/path/to/mailbox')
        fromaddr = 'jim@example.com'
        toaddrs = ('guido@example.com',
                   'steve@examplecom')
        zope_headers = ('X-Zope-From: jim@example.com\n'
                       'X-Zope-To: guido@example.com, steve@examplecom\n')
        opt_headers = ('From: Jim <jim@example.org>\n'
                       'To: some-zope-coders:;\n'
                       'Date: Mon, 19 May 2003 10:17:36 -0400\n'
                       'Message-Id: <20030519.1234@example.org>\n')
        message =     ('Subject: example\n'
                       '\n'
                       'This is just an example\n')

        msgid = service.send(fromaddr, toaddrs, opt_headers + message)
        self.assertEquals(msgid, '20030519.1234@example.org')
        self.assertEquals(MaildirWriterStub.commited_messages, [])
        self.assertEquals(MaildirWriterStub.aborted_messages, [])
        get_transaction().commit()
        self.assertEquals(MaildirWriterStub.commited_messages,
                          [zope_headers + opt_headers + message])
        self.assertEquals(MaildirWriterStub.aborted_messages, [])

        MaildirWriterStub.commited_messages = []
        msgid = service.send(fromaddr, toaddrs, message)
        self.assert_('@' in msgid)
        self.assertEquals(MaildirWriterStub.commited_messages, [])
        self.assertEquals(MaildirWriterStub.aborted_messages, [])
        get_transaction().commit()
        self.assertEquals(len(MaildirWriterStub.commited_messages), 1)
        self.assert_(MaildirWriterStub.commited_messages[0].endswith(message))
        new_headers = MaildirWriterStub.commited_messages[0][:-len(message)]
        self.assert_(new_headers.find('Message-Id: <%s>' % msgid) != -1)
        self.assert_(new_headers.find('X-Zope-From: %s' % fromaddr) != 1)
        self.assert_(new_headers.find('X-Zope-To: %s' % ", ".join(toaddrs)) != 1)
        self.assertEquals(MaildirWriterStub.aborted_messages, [])

        MaildirWriterStub.commited_messages = []
        msgid = service.send(fromaddr, toaddrs, opt_headers + message)
        self.assertEquals(MaildirWriterStub.commited_messages, [])
        self.assertEquals(MaildirWriterStub.aborted_messages, [])
        get_transaction().abort()
        self.assertEquals(MaildirWriterStub.commited_messages, [])
        self.assertEquals(len(MaildirWriterStub.aborted_messages), 1)


class TestQueueProcessorThread(TestCase):

    def setUp(self):
        from zope.app.mail.service import QueueProcessorThread
        self.md = MaildirStub('/foo/bar/baz')
        self.thread = QueueProcessorThread()
        self.thread.setMaildir(self.md)
        self.mailer = MailerStub()
        self.thread.setMailer(self.mailer)
        self.thread.log = LoggerStub()

    def test_parseMessage(self):

        hdr = ('X-Zope-From: foo@example.com\n'
               'X-Zope-To: bar@example.com, baz@example.com\n')
        msg = ('Header: value\n'
               '\n'
               'Body\n')


        f, t, m = self.thread._parseMessage(hdr + msg)
        self.assertEquals(f, 'foo@example.com')
        self.assertEquals(t, ('bar@example.com', 'baz@example.com'))
        self.assertEquals(m, msg)

    def test_deliveration(self):
        self.filename = mktemp()
        temp = open(self.filename, "w+b")
        temp.write('X-Zope-From: foo@example.com\n'
                   'X-Zope-To: bar@example.com, baz@example.com\n'
                   'Header: value\n\nBody\n')
        temp.close()
        self.md.files.append(self.filename)
        self.thread.run(forever=False)
        self.assertEquals(self.mailer.sent_messages,
                          [('foo@example.com',
                            ('bar@example.com', 'baz@example.com'),
                            'Header: value\n\nBody\n')])
        self.failIf(os.path.exists(self.filename), 'File exists')
        self.assertEquals(self.thread.log.infos,
                          [('Mail from %s to %s sent.',
                            ('foo@example.com',
                             'bar@example.com, baz@example.com'),
                            {})])


    def test_error_logging(self):
        self.thread.setMailer(BrokenMailerStub())
        self.filename = mktemp()
        temp = open(self.filename, "w+b")
        temp.write('X-Zope-From: foo@example.com\n'
                   'X-Zope-To: bar@example.com, baz@example.com\n'
                   'Header: value\n\nBody\n')
        temp.close()
        self.md.files.append(self.filename)
        self.thread.run(forever=False)
        self.assertEquals(self.thread.log.errors,
                          [('Error while sending mail from %s to %s.',
                            ('foo@example.com',
                             'bar@example.com, baz@example.com'),
                            {'exc_info': 1})])



def test_suite():
    return TestSuite((
        makeSuite(TestMailDataManager),
        makeSuite(TestDirectMailService),
        makeSuite(TestQueuedMailService),
        makeSuite(TestQueueProcessorThread),
        ))
