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
"""MailService Interfaces

Interfaces relevant for the MailService

$Id: mail.py,v 1.3 2003/05/21 10:52:53 mgedmin Exp $
"""

from zope.interface import Interface, Attribute
import zope.schema

from zope.app.interfaces.event import IEvent
from zope.app.i18n import ZopeMessageIDFactory as _


class IMailService(Interface):
    """A mail service allows someone to send an email to a group of people.

    Note: This interface is purposefully held very simple, so that it is easy
    to provide a basic mail service implementation.
    """

    hostname = zope.schema.TextLine(
        title=_(u"Hostname"),
        description=_(u"Name of server to be used as SMTP server."))

    port = zope.schema.Int(
        title=_(u"Port"),
        description=_(u"Port of SMTP service"),
        default=25)

    username = zope.schema.TextLine(
        title=_(u"Username"),
        description=_(u"Username used for optional SMTP authentication."))

    password = zope.schema.Password(
        title=_(u"Password"),
        description=_(u"Password used for optional SMTP authentication."))

    def send(fromaddr, toaddrs, message):
        """Send a message to the tos (list of email unicode strings) with a
        sender specified in from (unicode string).
        """


# XXX: Needs better name: AsyncMailService, MailerMailService, ...
class IAsyncMailService(IMailService):
    """This mail service handles mail delivery using so called Mailer objects.

    The policies for sending the mail are encoded in the Mailer object.  Also,
    it is recommended that the mailer is called in a different thread, so that
    the request is not blocked.
    """

    def createMailer(name):
        """Create a Mailer object which class was registered under the passed
        name."""

    def getMailerNames():
        """Return a list of the names of all registered mailers."""

    def getDefaultMailerName():
        """Return the name of the default Mailer.  None, means there is no
        default mailer class defined.
        """

    def send(fromaddr, toaddrs, message, mailer=None):
        """This interface extends the send method by an optional mailer
        attribute.  If the mailer is None, an object from the default mailer
        class is created and used.
        """


class IMailer(Interface):
    """This is a generic Mailer interface.

    Mailers implement mailing policies, such as batching, scheduling and so
    on.
    """

    def send(fromaddr, toaddrs, message, hostname, port, username, password):
        """Send a message.  How and when the mailer is going to send
        out the mail is purely up to the mailer's policy.
        """


class IBatchMailer(IMailer):
    """The Batch Mailer allows for sending emails in batches, so that the
    server load will not be too high.
    """

    batchSize = zope.schema.Int(
        title=_(u"Batch Size"),
        description=_(u"Amount of E-mails sent in one batch."),
        min=1)

    batchDelay = zope.schema.Int(
        title=_(u"Batch Delay"),
        description=_(u"Delay time in milliseconds between batches."),
        min=100)


class IScheduleMailer(IMailer):
    """This mailer allows you to specify a specific date/time to send the
    mails.
    """

    sendAt = zope.schema.Datetime(
        title=_(u"Send at"),
        description=_(u"Date/time the message should be send."))


class IMailEvent(IEvent):
    """Generic Mailer event that can be sent from the mailer or the mail
    service.
    """

    mailer = Attribute("Mailer object that is used to send the mail.")


class IMailSentEvent(IMailEvent):
    """Event that is fired when all the mail in the mailer was sent.

    Note: Subscribing to this event eliminates the need for implementing
    callback functions for the asynchronous delivery.
    """



class IMaildirFactory(Interface):

    def __call__(dirname, create=False):
        """Opens a Maildir folder at a given filesystem path.

        If 'create' is True, the folder will be created when it does not
        exist.  If 'create' is False and the folder does not exist, an
        exception (OSError) will be raised.

        If path points to a file or an existing directory that is not a
        valid Maildir folder, an exception is raised regardless of the
        'create' argument.
        """


class IMaildir(Interface):
    """Read/write access to Maildir folders.

    See http://www.qmail.org/man/man5/maildir.html for detailed format
    description.
    """

    def __iter__():
        """Returns an iterator over the pathnames of messages in this folder.
        """

    def newMessage():
        """Creates a new message in the maildir.

        Returns a file-like object for a new file in the 'tmp' subdirectory
        of the Maildir.  After writing message contents to it, call the
        commit() or abort() method on it.

        The returned object implements IMaildirMessageWriter.
        """


class IMaildirMessageWriter(Interface):
    """A file-like object to a new message in a Maildir."""

    def write(str):
        """Writes a string to the file.

        There is no return value. Due to buffering, the string may not actually
        show up in the file until the commit() method is called.
        """

    def writelines(sequence):
        """Writes a sequence of strings to the file.

        The sequence can be any iterable object producing strings, typically a
        list of strings. There is no return value.  'writelines' does not add
        any line separators.
        """

    def commit():
        """Commits the new message using the Maildir protocol.

        First, the message file is flushed, closed, then it is moved from
        'tmp' into 'new' subdirectory of the maildir.

        Calling commit() more than once is allowed.
        """

    def abort():
        """Aborts the new message.

        The message file is closed and removed from the 'tmp' subdirectory
        of the maildir.

        Calling abort() more than once is allowed.
        """

