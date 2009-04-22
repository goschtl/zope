##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os
import tempfile

import transaction

from zope import component
from zope import interface

from zope.sendmail.interfaces import IMailer, IMailDelivery
from zope.sendmail.delivery import QueueProcessorThread


sentMails = []


class TestMailDelivery(object):

    """a  mail delivery utility that stores its messages without
    sending for testing

    >>> md = TestMailDelivery()

    It implements the maildelivery interface
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IMailDelivery, md)
    True

    We can send messages ...
    >>> md.send('from', ['to'], 'message')

    They are stored in sent
    >>> md.sent
    [('from', ('to',), 'message')]

    We can also clear the messages
    >>> md.clear()
    >>> md.sent
    []
    """
    interface.implements(IMailDelivery)

    def __init__(self):
        self.clear()

    def send(self, fromaddr, toaddrs, message):
        self.sent.append((fromaddr, tuple(toaddrs), message))

    def clear(self):
        self.sent = []

class TestMailerConnection(object):

    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

    does_esmtp = True

    def login(self, username, password):
        pass

    def sendmail(self, fromaddr, toaddr, message):
        sentMails.append((fromaddr, toaddr, message))

    def ehlo(self):
        return 200, ''

    def helo(self):
        return 200, ''

    def has_extn(self, query):
        return False

    def quit(self):
        pass

oldSMTP = None
oldQueuePath = None
mailer = None
deliver = None
thread = None

def setUpSMTPTesting(mailerName, deliveryName, unit_test=False):
    """Set up the mail testing for SMTP mailer.

    We replace the smpt mail module by our test mailer.
    """
    global oldSMTP, oldQueuePath, mailer, delivery, thread
    del sentMails[:]
    mailer = component.getUtility(IMailer, mailerName)
    oldSMTP = mailer.smtp
    mailer.smtp = TestMailerConnection
    delivery = component.getUtility(IMailDelivery, deliveryName)
    oldQueuePath = delivery._queuePath
    delivery._queuePath = os.path.join(tempfile.mkdtemp(), 'mail')
    thread = QueueProcessorThread()
    thread.setMailer(mailer)
    thread.setQueuePath(delivery.queuePath)


def tearDownSMTPTesting():
    global oldSMTP, oldQueuePath, mailer, delivery, thread
    mailer.smtp = oldSMTP
    delivery._queuePath = oldQueuePath
    import threading
    for t in threading.enumerate():
        if isinstance(t, QueueProcessorThread):
            t.stop()
    thread = None
    del sentMails[:]


def triggerMail():
    # send pending mails
    global thread
    transaction.commit()
    if thread:
        thread.run(False)
        
def clearSentMails():
    del sentMails[:]

