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
"""Tests for mailers.

$Id$
"""

import unittest
from StringIO import StringIO
from zope.interface.verify import verifyObject
from zope.app.mail.interfaces import ISendmailMailer, ISMTPMailer


class TestSendmailMailer(unittest.TestCase):

    def setUp(self):
        from zope.app.mail.mailer import SendmailMailer

        class ShtringIO(StringIO):
            def close(self):
                pass
        self.input = ShtringIO()
        def popen(cmd, mode):
            self.cmd_arg = cmd
            self.mode_arg = mode
            return self.input
        self.mailer = SendmailMailer()
        self.mailer.popen = popen

    def test_interface(self):
        verifyObject(ISendmailMailer, self.mailer)

    def test_send(self):
        msgtext = 'Headers: headers\n\nbodybodybody\n-- \nsig\n'
        self.mailer.send('me@example.com',
                         ('you@example.com', 'him@example.com'),
                         msgtext)
        self.assertEquals(self.input.getvalue(), msgtext)
        self.assertEquals(self.cmd_arg, "/usr/lib/sendmail -oem -oi"
                          " -f me@example.com you@example.com him@example.com")
        self.assertEquals(self.mode_arg, "w")


class TestSMTPMailer(unittest.TestCase):

    def setUp(self, port=None):
        from zope.app.mail.mailer import SMTPMailer

        class SMTP:

            def __init__(myself, h, p):
                myself.hostname = h
                myself.port = p
                if type(p) == type(u""):
                    import socket
                    raise socket.error("Int or String expected")
                self.smtp = myself

            def sendmail(self, f, t, m):
                self.fromaddr = f
                self.toaddrs = t
                self.msgtext = m

            def login(self, username, password):
                self.username = username
                self.password = password

            def quit(self):
                self.quit = True

        if port is None:
            self.mailer = SMTPMailer()
        else:
            self.mailer = SMTPMailer(u'localhost', port)
        self.mailer.smtp = SMTP

    def test_interface(self):
        verifyObject(ISMTPMailer, self.mailer)

    def test_send(self):
        for run in (1,2):
            if run == 2:
                self.setUp(u'25')
            fromaddr = 'me@example.com'
            toaddrs = ('you@example.com', 'him@example.com')
            msgtext = 'Headers: headers\n\nbodybodybody\n-- \nsig\n'
            self.mailer.send(fromaddr, toaddrs, msgtext)
            self.assertEquals(self.smtp.fromaddr, fromaddr)
            self.assertEquals(self.smtp.toaddrs, toaddrs)
            self.assertEquals(self.smtp.msgtext, msgtext)
            self.assert_(self.smtp.quit)

    def test_send_auth(self):
        fromaddr = 'me@example.com'
        toaddrs = ('you@example.com', 'him@example.com')
        msgtext = 'Headers: headers\n\nbodybodybody\n-- \nsig\n'
        self.mailer.username = 'foo'
        self.mailer.password = 'evil'
        self.mailer.hostname = 'spamrelay'
        self.mailer.port = 31337
        self.mailer.send(fromaddr, toaddrs, msgtext)
        self.assertEquals(self.smtp.username, 'foo')
        self.assertEquals(self.smtp.password, 'evil')
        self.assertEquals(self.smtp.hostname, 'spamrelay')
        self.assertEquals(self.smtp.port, '31337')
        self.assertEquals(self.smtp.fromaddr, fromaddr)
        self.assertEquals(self.smtp.toaddrs, toaddrs)
        self.assertEquals(self.smtp.msgtext, msgtext)
        self.assert_(self.smtp.quit)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSendmailMailer))
    suite.addTest(unittest.makeSuite(TestSMTPMailer))
    return suite


if __name__ == '__main__':
    unittest.main()
