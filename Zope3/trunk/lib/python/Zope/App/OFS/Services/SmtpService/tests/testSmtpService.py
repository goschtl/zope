##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

"""This module tests the regular persistent SMTP Service.

$Id: testSmtpService.py,v 1.1 2002/10/28 21:05:00 bwarsaw Exp $
"""

import sys
import unittest
import smtpd
import asyncore
import threading

from Zope.App.OFS.Services.SmtpService.SmtpService import SmtpService

UNPRIV_PORT = 9225
#smtpd.DEBUGSTREAM = sys.stderr

class OneShotChannel(smtpd.SMTPChannel):
    def smtp_QUIT(self, arg):
        smtpd.SMTPChannel.smtp_QUIT(self, arg)
        raise asyncore.ExitNow


class SinkServer(smtpd.SMTPServer, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        smtpd.SMTPServer.__init__(
            self ,
            ('localhost', UNPRIV_PORT), ('ignored', 25))
        self.msgtext = None

    def handle_accept(self):
        conn, addr = self.accept()
        channel = OneShotChannel(self, conn, addr)

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.msgtext = data

    def run(self):
        try:
            # timeout is in milliseconds, see asyncore.py poll3()
            asyncore.loop(timeout=30.0)
            self.msgtext = None
        except asyncore.ExitNow:
            pass

    def close(self):
        smtpd.SMTPServer.close(self)


class TestSmtpService(unittest.TestCase):
    def setUp(self):
        self._service = SmtpService(smtpport=UNPRIV_PORT)
        self._reader = SinkServer()

    def tearDown(self):
        self._reader.close()

    def testSendMessage(self):
        text = """\
This is a test message.
"""
        mfrom = 'tests@example.com (Zope3 Test Suite)'
        mto = 'results@example.com (Zope3 Test Results)'
        subject = 'testSmtpService.testSendMessage'

        self._reader.start()
        self._service.sendMessage(text, mto, mfrom, subject)
        self._reader.join()
        response = self._reader.msgtext

        self.assertEqual(response, """\
subject: testSmtpService.testSendMessage

This is a test message.""")


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestSmtpService)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
