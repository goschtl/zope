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
"""Mail service implementation

This module contains various implementations of MailServices.

$Id: service.py,v 1.4 2003/06/23 15:45:39 alga Exp $
"""
import rfc822
import threading
import os.path
import logging
from os import listdir, unlink
from cStringIO import StringIO
from random import randrange
from time import strftime
from socket import gethostname
from os import getpid
from time import sleep
from zope.interface import implements
from zope.app.interfaces.mail import IDirectMailService, IQueuedMailService
from zope.app.mail.maildir import Maildir
from transaction.interfaces import IDataManager
from transaction import get_transaction

__metaclass__ = type

class MailDataManager:
    """XXX I need a docstring"""

    implements(IDataManager)

    def __init__(self, callable, args=(), onAbort=None):
        self.callable = callable
        self.args = args
        self.onAbort = onAbort

    def prepare(self, transaction):
        pass

    def abort(self, transaction):
        if self.onAbort:
            self.onAbort()

    def commit(self, transaction):
        self.callable(*self.args)

    def savepoint(self, transaction):
        pass


class AbstractMailService:

    def newMessageId(self):
        """Generates a new message ID according to RFC 2822 rules"""
        randmax = 0x7fffffff
        left_part = '%s.%d.%d' % (strftime('%Y%m%d%H%M%S'),
                                  getpid(),
                                  randrange(0, randmax))
        return "%s@%s" % (left_part, gethostname())

    def send(self, fromaddr, toaddrs, message):
        parser = rfc822.Message(StringIO(message))
        messageid = parser.getheader('Message-Id')
        if messageid:
            if not messageid.startswith('<') or not messageid.endswith('>'):
                raise ValueError('Malformed Message-Id header')
            messageid = messageid[1:-1]
        else:
            messageid = self.newMessageId()
            message = 'Message-Id: <%s>\n%s' % (messageid, message)
        get_transaction().join(self.createDataManager(fromaddr, toaddrs, message))
        return messageid


class DirectMailService(AbstractMailService):
    __doc__ = IDirectMailService.__doc__

    implements(IDirectMailService)

    def __init__(self, mailer):
        self.mailer = mailer

    def createDataManager(self, fromaddr, toaddrs, message):
        return MailDataManager(self.mailer.send, args=(fromaddr, toaddrs, message))


class QueuedMailService(AbstractMailService):
    __doc__ = IQueuedMailService.__doc__

    implements(IQueuedMailService)

    def __init__(self, queuePath):
        self._queuePath = queuePath

    queuePath = property(lambda self: self._queuePath)

    def createDataManager(self, fromaddr, toaddrs, message):
        maildir = Maildir(self.queuePath, True)
        msg = maildir.newMessage()
        msg.write('X-Zope-From: %s\n' % fromaddr)
        msg.write('X-Zope-To: %s\n' % ", ".join(toaddrs))
        msg.write(message)
        return MailDataManager(msg.commit, onAbort=msg.abort)

class QueueProcessorThread(threading.Thread):
    """This thread is started at configuration time from the
    mail:queuedService directive handler.
    """
    log = logging.getLogger("QueueProcessorThread")

    def setMaildir(self, maildir):
        """Set the maildir.

        This method is used just to provide a maildir stubs ."""
        self.maildir = maildir

    def setQueuePath(self, path):
        self.maildir = Maildir(path)

    def setMailer(self, mailer):
        self.mailer = mailer

    def _parseMessage(self, message):
        """Extract fromaddr and toaddrs from the first two lines of
        the message.

        Returns a fromaddr string, a toaddrs tuple and the message
        string.
        """

        fromaddr = ""
        toaddrs = ()
        rest = ""

        try:
            first, second, rest = message.split('\n', 2)
        except ValueError:
            return fromaddr, toaddrs, message

        if first.startswith("X-Zope-From: "):
            i = len("X-Zope-From: ")
            fromaddr = first[i:]

        if second.startswith("X-Zope-To: "):
            i = len("X-Zope-To: ")
            toaddrs = tuple(second[i:].split(", "))

        return fromaddr, toaddrs, rest

    def run(self, forever=True):
        while True:
            for filename in self.maildir:
                try:
                    file = open(filename)
                    message = file.read()
                    file.close()
                    fromaddr, toaddrs, message = self._parseMessage(message)
                    self.mailer.send(fromaddr, toaddrs, message)
                    unlink(filename)
                    # XXX maybe log the Message-Id of the message sent
                    self.log.info("Mail from %s to %s sent.",
                                  fromaddr, ", ".join(toaddrs))
                    # Blanket except because we don't want this thread to ever die
                except:
                    # XXX maybe throw away erroring messages here?
                    self.log.error("Error while sending mail from %s to %s.",
                                   fromaddr, ", ".join(toaddrs), exc_info=1)
            else:
                if forever:
                    sleep(3)

            # A testing plug
            if not forever:
                break
