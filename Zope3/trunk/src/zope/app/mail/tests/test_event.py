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

$Id: test_event.py,v 1.2 2003/06/23 15:45:40 alga Exp $
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.interface.verify import verifyObject
from zope.app.interfaces.mail import IMailSentEvent, IMailErrorEvent


class TestMailEvents(TestCase):

    def testMailSendEvent(self):
        from zope.app.mail.event import MailSentEvent
        msgid = '<1234@example.com>'
        m = MailSentEvent(msgid)
        verifyObject(IMailSentEvent, m)
        self.assertEquals(m.messageId, msgid)

    def testMailErrorEvent(self):
        from zope.app.mail.event import MailErrorEvent
        msgid = '<1234@example.com>'
        error = '550 Relay access denied'
        m = MailErrorEvent(msgid, error)
        verifyObject(IMailErrorEvent, m)
        self.assertEquals(m.messageId, msgid)
        self.assertEquals(m.errorMessage, error)


def test_suite():
    return TestSuite((
        makeSuite(TestMailEvents),
        ))
