##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
The z3checkins product.

$Id$
"""
import email
import email.Utils
import mailbox
import time
from datetime import datetime, tzinfo, timedelta
from persistent import Persistent
from StringIO import StringIO

from zope.exceptions import DuplicationError
from zope.interface import implements
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IReadContainer
from zope.app.datetimeutils import parseDatetimetz, DateTimeError
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import FileWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.publisher.browser import BrowserView

from z3checkins.interfaces import IMessage, ICheckinMessage, IMessageContained
from z3checkins.interfaces import IBookmark, IMessageParser, FormatError
from z3checkins.timeutils import FixedTimezone

__metaclass__ = type


class Message(Persistent, Contained):
    """Persistent email message."""

    implements(IMessage, IMessageContained)

    def __init__(self, message_id=None, author_name=None,
                 author_email=None, subject=None, date=None,
                 full_text=None):
        self.message_id = message_id
        self.author_name = author_name
        self.author_email = author_email
        self.subject = subject
        self.date = date
        self.full_text = full_text

    def _getBody(self):
        if self.full_text is None:
            return None
        else:
            return self.full_text[find_body_start(self.full_text):]

    body = property(_getBody)

    def __eq__(self, other):
        """Messages with the same message_id compare identical."""
        if not IMessage.providedBy(other):
            return False
        return self.message_id == other.message_id

    def __ne__(self, other):
        return not self.__eq__(other)


class CheckinMessage(Message):
    """Persistent checkin message."""

    implements(ICheckinMessage)

    def __init__(self, message_id=None, author_name=None,
                 author_email=None, subject=None, date=None, full_text=None,
                 directory=None, log_message=None, branch=None):
        Message.__init__(self, message_id=message_id,
            author_name=author_name, author_email=author_email,
            subject=subject, date=date, full_text=full_text)
        self.directory = directory
        self.log_message = log_message
        self.branch = branch


class CheckinMessageParser:
    """Parser for RFC822 mail messages."""

    implements(IMessageParser)

    def parse(self, input):
        """See IMessageParser."""
        if not hasattr(input, 'readline'):
            full_text = str(input)
        elif hasattr(input, 'seek') and hasattr(input, 'tell'):
            old_pos = input.tell()
            full_text = input.read()
            input.seek(old_pos)
        else:
            full_text = input.read()

        m = email.message_from_string(full_text)
        subject = m.get('Subject', '').replace('\n', '')
        message_id = m.get('Message-Id', None)
        if message_id is None:
            raise FormatError("Message does not have a message id")
        if message_id.startswith("<") and message_id.endswith(">"):
            message_id = message_id[1:-1] # strip angle brackets
        author = m.get('From', '')
        author_name, author_email = email.Utils.parseaddr(author)
        date = m.get('Date', '')

        # Fix incorrect timezones (+ZZ:ZZ instead of RFC-822 mandated +ZZZZ)
        if date[-3] == ':':
            date = date[:-3] + date[-2:]

        (year, month, day, hours, minutes, seconds,
         weekday, yearday, dst, tzoffset) = email.Utils.parsedate_tz(date)

        # A workaround to deal with messages that don't specify a timezone.
        if tzoffset is None:
            tzoffset = 0

        date = datetime(year, month, day, hours, minutes, seconds,
                        tzinfo=FixedTimezone(tzoffset / 60))

        checkin_info = self.tryToParseCheckinMessage(subject, m)
        if checkin_info is not None:
            subject, directory, log_message, branch = checkin_info
            return CheckinMessage(message_id=message_id,
                                  author_name=author_name,
                                  author_email=author_email, subject=subject,
                                  date=date, full_text=full_text,
                                  directory=directory, log_message=log_message,
                                  branch=branch)

        return Message(message_id=message_id,
                       author_name=author_name,
                       author_email=author_email, subject=subject,
                       date=date, full_text=full_text)

    def tryToParseCheckinMessage(self, subject, msg):
        """Detect and parse CVS/Subversion checkin messages.

        Returns a tuple (directory, log_message, branch) for checkin
        messages, and None if the message is not a checkin message.
        """
        if subject.startswith("Re:"):
            return None

        if "CVS:" in subject:
            # [foo-bar] CVS: foobaz/bar - baz.py:1.5
            parts = subject.split("CVS: ", 1)
            if len(parts) < 2:
                return None
            subject = parts[1]
            directory = subject.split(' - ')[0]
        elif "SVN:" in subject:
            # Format that is specific to the Zope3 mailing list
            # [foo-bar] SVN: foobaz/boo/bar.py log message
            parts = subject.split("SVN: ", 1)
            if len(parts) < 2:
                return None
            subject = parts[1]
            directory = subject.split(None, 1)[0]
            # Remove the mailing list name and the trailing note, which
            # is shown on the next line anyway.
            subject = "SVN: " + directory
        elif "rev " in subject:
            # [foo-bar] rev 42 - trunk/foofoofoo
            parts = subject.split(' - ')
            if len(parts) < 2:
                return None
            directory = parts[1]
        else:
            return None

        body_lines = msg.get_payload().splitlines()
        try:
            log_message, branch = self.extract_log(body_lines)
        except FormatError:
            return None

        return subject, directory, log_message, branch

    def extract_log(self, lines):
        log_message = []
        branch = None
        in_log_msg = False
        for line in lines:
            if in_log_msg:
                if (line.startswith('=== ')
                    or line.startswith("Changed:")
                    or line.startswith("Added:")
                    or line.startswith("Modified:")
                    or line.startswith("Removed:")
                    or line.startswith("Deleted:")
                    or line.startswith("Copied:")
                    or line.startswith("Property changes on:")
                    or line == "Status:"):
                    break
                else:
                    log_message.append(line)
            else:
                if (line.lower().startswith('log message') or
                    line.startswith("Log:")):
                    in_log_msg = True
                elif line.startswith('      Tag: '):
                    branch = line[len('      Tag: '):].strip()
        if not in_log_msg:
            raise FormatError("Could not find log message")
        return "\n".join(log_message).strip(), branch


class Bookmark:
    """A bookmark placed between messages."""

    implements(IBookmark)


def find_body_start(full_text):
    """Find the body of an RFC-822 message and return its index in full_text."""
    pos1 = full_text.find('\n\n')
    pos2 = full_text.find('\r\n\r\n')
    if pos1 == -1:
        pos1 = len(full_text)
    else:
        pos1 += 2
    if pos2 == -1:
        pos2 = len(full_text)
    else:
        pos2 += 4
    return min(pos1, pos2)

