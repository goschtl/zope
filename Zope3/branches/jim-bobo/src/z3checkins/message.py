"""
Python code for z3checkins product.

# This module could be split into three: timeutils.py, message.py and views.py
# but it is small enough IMHO.

$Id: message.py,v 1.40 2004/05/14 19:56:05 gintautasm Exp $
"""

import re
import email
import email.Utils
import mailbox
import time
from StringIO import StringIO
from datetime import datetime, tzinfo, timedelta

from persistent import Persistent
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import FileWidget
from zope.app.container.interfaces import IReadContainer
from zope.app.datetimeutils import parseDatetimetz, DateTimeError
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility
from zope.component import getView
from zope.exceptions import DuplicationError
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.app.publisher.browser import BrowserView

from interfaces import IMessage, ICheckinMessage, IMessageContained
from interfaces import IMessageUpload, IBookmark
from interfaces import IMessageParser, IMessageArchive
from interfaces import FormatError

__metaclass__ = type

#
# Date/time utils
#

class FixedTimezone(tzinfo):
    """Timezone with a fixed UTC offset"""

    def __init__(self, offset=None):
        """Creates a timezone with a given UTC offset (minutes east of UTC)."""
        self._offset = offset

    def tzname(self, dt):
        if self._offset >= 0:
            sign = '+'
            h, m = divmod(self._offset, 60)
        else:
            sign = '-'
            h, m = divmod(-self._offset, 60)
        return '%c%02d%02d' % (sign, h, m)

    def utcoffset(self, dt):
        return timedelta(minutes=self._offset)

    def dst(self, dt):
        return timedelta(0)


class RFCDateTimeFormatter:
    """RFC822 view for datetime objects."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        """Renders datetime objects in RFC822 format."""
        return self.context.strftime("%a, %d %b %Y %H:%M:%S %z")

    __call__ = __str__


class ISODateTimeFormatter:
    """ISO 8601 view for datetime objects."""

    if time.localtime()[-1]:
        userstz = FixedTimezone(-time.altzone / 60)
    else:
        userstz = FixedTimezone(-time.timezone / 60)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        """Renders datetime objects as "YYYY-MM-DD hh:mm" in the local time
        zone."""
        return self.context.astimezone(self.userstz).strftime("%Y-%m-%d %H:%M")

    __call__ = __str__


#
# Checkin message content object
#

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


class Message(Persistent):
    """Persistent email message."""

    implements(IMessage, IMessageContained)

    __parent__ = __name__ = None

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
        if message_id[0] == "<" and message_id[-1] == ">":
            message_id = message_id[1:-1] # strip angle brackets
        author = m.get('From', '')
        author_name, author_email = email.Utils.parseaddr(author)
        date = m.get('Date', '')

        # Fix incorrect timezones (+ZZ:ZZ instead of RFC-822 mandated +ZZZZ)
        if date[-3] == ':':
            date = date[:-3] + date[-2:]

        (year, month, day, hours, minutes, seconds,
         weekday, yearday, dst, tzoffset) = email.Utils.parsedate_tz(date)

        # TODO: a workaround to deal with messages that don't specify a timezone
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
            # TODO: Format specific to the Zope3 mailing list
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
                    or line.startswith('-=-') # TODO: Zope3 ML specific
                    or line.startswith("Added:")
                    or line.startswith("Modified:")
                    or line.startswith("Removed:")
                    or line.startswith("Deleted:")
                    or line.startswith("Property changes on:")
                    or line == "Status:"
                    ):
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


class MessageContainerAdapter:
    """Adapts a container to a message archive."""

    implements(IMessageArchive)
    __used_for__ = IReadContainer

    def __init__(self, context):
        self.context = context
        items = []
        for key, item in self.context.items():
            if IMessage.providedBy(item):
                items.append((item.date, key, item))
        items.sort()
        self.messages = []
        for date, key, item in items:
            # TODO: is this nice?
            #item.__parent__ = self.context
            #item.__name__ = key
            self.messages.append(item)

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]

    def __getslice__(self, start, stop):
        return self.messages[start:stop]

    def __iter__(self):
        return iter(self.messages)

    def index(self, message):
        return self.messages.index(message)


class Bookmark:

    implements(IBookmark)


#
# Browser views
#

class MessageUpload:
    """Adding view mixin for uploading checkin messages."""

    implements(IMessageUpload, IMessageContained)
    data_widget = CustomWidgetFactory(FileWidget)

    def createAndAdd(self, data):
        if data.has_key('data'): # XXX should we bark if no data is given?
            msg_raw = data['data']
            parser = getUtility(IMessageParser)
            if msg_raw.startswith("From "):
                # detected an mbox file
                mbox = StringIO(msg_raw)
                messages = mailbox.PortableUnixMailbox(mbox,
                        factory=parser.parse)
                for message in messages:
                    try:
                        self.add(message)
                        dc = IZopeDublinCore(message, None)
                        if dc is not None:
                            # TODO: should handle RFC-2047
                            dc.title = unicode(message.subject)
                            dc.created = message.date
                    except DuplicationError:
                        pass # leave the old mesage unchanged
            else:
                message = parser.parse(msg_raw)
                self.add(message)


class ContainerView:
    """View mixin for locating checkin messages in a container."""

    max_bookmarks = 5

    def title(self):
        """Returns the title of this archive.

        Title is obtained from Dublin Core metadata of the folder.  If it is
        empty, "Zope 3 Checkins" is used.
        """
        dc = IZopeDublinCore(self.context, None)
        if dc is not None:
            title = dc.title
        else:
            title = ''
        return title or "Zope 3 Checkins"

    def description(self):
        """Returns the description of this archive.
        """
        return self.context.description

    def archive_url(self):
        """Returns the URL for mailing list archives.
        """
        return self.context.archive_url

    def bookmarks(self):
        """Returns a list of bookmarks from a cookie.  Each bookmark is
        expressed as a datetime object.
        """
        bookmarks = []
        cookie = self.request.get('bookmarks', '')
        for item in cookie.split():
            try:
                bookmarks.append(parseDatetimetz(item))
            except (DateTimeError, IndexError):
                pass
        return bookmarks

    def placeBookmark(self):
        """Place a new bookmark after the latest checkin message in a
        cookie."""
        if int(self.request.get('start', 0)) > 0:
            return # The user can't see the newest checkins
        if not hasattr(self, '_archive'):
            self._archive = IMessageArchive(self.context)
        if not self._archive:
            return # No messages -- no bookmarks
        bookmarks = self.bookmarks()
        bookmarks.sort()
        # Do not insert a bookmark if there were no checkins since the last
        # bookmark
        if (bookmarks and bookmarks[-1] >= self._archive[-1].date):
            return
        bookmarks.append(self._archive[-1].date)
        if len(bookmarks) > self.max_bookmarks:
            del bookmarks[:-self.max_bookmarks]
        cookie = " ".join([dt.isoformat() for dt in bookmarks])
        self.request.response.setCookie('bookmarks', cookie,
                                        max_age=365*24*60*60) # 1 year

    def checkins(self, start=None, size=None):
        """Returns a list of the last 'size' checkin messages in
        self.context, newest first, skipping the first 'start' messages.
        """
        if start is None: start = int(self.request.get('start', 0))
        if size is None: size = int(self.request.get('size', 20))
        if not hasattr(self, '_archive'):
            self._archive = IMessageArchive(self.context)
        idx = len(self._archive) - start
        items = self._archive[max(0, idx-size):idx]
        items = removeAllProxies(items)
        # insert bookmarks
        def bookmarkBetween(msg1, msg2, bookmarks=self.bookmarks()):
            for b in bookmarks:
                if msg1.date <= b < msg2.date:
                    return True
            return False
        n = 1
        while n < len(items):
            if bookmarkBetween(items[n-1], items[n]):
                items.insert(n, Bookmark())
                n += 2
            else:
                n += 1
        # insert bookmarks before the first/after the last batch item
        if items:
            before = self._archive[max(0, idx-size-1):max(0, idx-size)]
            if before and bookmarkBetween(before[0], items[0]):
                items.insert(0, Bookmark())
            after = self._archive[idx:idx+1]
            if after and bookmarkBetween(items[-1], after[0]):
                items.insert(len(items), Bookmark())
        # reverse order to present newest checkins first
        items.reverse()
        return items

    def renderCheckins(self, start=None, size=None):
        """Returns a list of checkins rendered into HTML.  See `checkins` for
        description of parameters."""
        html = []
        previous_message = None
        for item in self.checkins(start=start, size=size):
            if ICheckinMessage.providedBy(item):
                same_as_previous = item.log_message == previous_message
                previous_message = item.log_message
            else:
                same_as_previous = None
            view = getView(item, 'html', self.request)
            output = view(same_as_previous=same_as_previous)
            html.append(output)
        return "".join(html)

    def count(self):
        """Returns the number of checkin messages in the archive."""
        if not hasattr(self, '_archive'):
            self._archive = IMessageArchive(self.context)
        return len(self._archive)


class MessageRSSView(BrowserView):
    """View for messages.

    Makes sure the page template is treated as XML.
    """

    index = ViewPageTemplateFile('rss_message.pt', content_type='text/xml')


class MessageView:
    """View mixin for messages."""

    def _calc_index(self):
        if not hasattr(self, '_archive'):
            container = self.context.__parent__
            self._archive = container and IMessageArchive(container, None)
        if not self._archive:
            self._index = None
        elif not hasattr(self, '_index'):
            self._index = self._archive.index(self.context)

    def next(self):
        """Returns the next message in archive."""
        self._calc_index()
        if self._index is not None and self._index < len(self._archive) - 1:
            return self._archive[self._index + 1]
        else:
            return None

    def previous(self):
        """Returns the previous message in archive."""
        self._calc_index()
        if self._index is not None and self._index > 0:
            return self._archive[self._index - 1]
        else:
            return None

    def first(self):
        """Returns the first message in archive."""
        self._calc_index()
        if self._archive:
            return self._archive[0]
        else:
            return None

    def last(self):
        """Returns the last message in archive."""
        self._calc_index()
        if self._archive:
            return self._archive[-1]
        else:
            return None

    def icon(self):
        """Returns a mapping describing an icon for this checkin.  The mapping
        contains 'src', 'alt' and 'title' attributes."""
        return {'src': '++resource++message.png',
                'alt': 'Message',
                'title': 'Email message'}

    def body(self):
        """Colorizes the body of a checkin message."""

        text = self.context.body.replace('\r', '')\
                                .replace('&', '&amp;') \
                                .replace('<', '&lt;') \
                                .replace('>', '&gt;') \
                                .replace('"', '&quot;')
        # It would be nice to highlight quoted text here
        return '<pre>%s</pre>' % text


class CheckinMessageView(MessageView):
    """View mixin for checkin messages."""

    _subtrees = None
    def subtrees(self):
        """Returns a sequence of tuples (prefix, icon, alt, title).

        (icon, alt, title) are the resource name, alt text and tooltip used
        for any checkin messages that have directory starting with prefix.

        This information is currently taken from Dublin Core metadata
        description field, third paragraph.  Every line in that paragraph
        defines a subtree, with all fields separated by spaces or tabs.
        """
        if self._subtrees is not None:
            return self._subtrees
        self._subtrees = []
        container = self.context.__parent__
        icons = container.icons
        if not icons:
            return self._subtrees
        for line in icons.splitlines():
            if line.startswith('#'):
                continue
            items = line.split(None, 3)
            if len(items) < 4:
                continue
            if items[0] == '*':  # catch-all
                items[0] = ''
            self._subtrees.append(items)
        return self._subtrees

    def icon(self):
        """Returns a mapping describing an icon for this checkin.  The mapping
        contains 'src', 'alt' and 'title' attributes."""
        for prefix, icon, alt, title in self.subtrees():
            if self.context.directory.startswith(prefix):
                return {'src': '++resource++%s' % icon,
                        'alt': alt,
                        'title': title}
        return {'src': '++resource++product.png',
                'alt': 'Checkin',
                'title': 'Checkin'}

    def body(self):
        """Colorizes checkin message body."""

        text = self.context.body.replace('\r', '')\
                                .replace('&', '&amp;') \
                                .replace('<', '&lt;') \
                                .replace('>', '&gt;') \
                                .replace('"', '&quot;')

        text = re.sub(r'(https?://.+?)'
                      r'($|[ \t\r\n)]|&gt;|&quot;|[.,](?:$|[ \t\r\n]))',
                      r'<a href="\1">\1</a>\2', text)

        log_idx = text.find('\nLog message:\n')
        if log_idx == -1:
            log_idx = text.find('\nLog Message:\n')
        if log_idx != -1:
            log_idx += len('\nLog message:\n')
        if log_idx == -1:
            log_idx = text.find('\nLog:\n')
            if log_idx != -1:
                log_idx += len('\nLog:\n')
            else:
                log_idx = text.find('Log message') #TODO: Zope3 checkin-specific
                if log_idx != -1:
                    log_idx = text.find('\n', log_idx) + 1
                    # TODO: This is yucky...
                    text = text.replace('\n-=-\n', '')
        if log_idx == -1:
            return '<pre>%s</pre>' % text

        sig_idx = text.rfind(
                        '\n_______________________________________________')
        if sig_idx == -1:
            sig_idx = len(text)

        diff_idx = text.find('\n===')
        if diff_idx == -1:
            diff_idx = sig_idx

        status_idx = text.find('\nStatus:\n')
        if status_idx == -1:
            if text[diff_idx:diff_idx+5] == "\n====":
                # Subversion
                status_idx = text.rfind('\n', 0, diff_idx)
            else:
                status_idx = diff_idx

            propchange_idx = text.find('\nProperty changes on:')
            if propchange_idx != -1 and propchange_idx < status_idx:
                status_idx = propchange_idx

        assert log_idx <= status_idx <= diff_idx <= sig_idx

        intro = text[:log_idx]
        log = text[log_idx:status_idx].strip()
        import_status = text[status_idx:diff_idx]
        diff = text[diff_idx:sig_idx]
        sig = text[sig_idx:]

        def empty2nbsp(s):
            if not s:
                return '&nbsp;'
            n = 0
            while n < len(s) and s[n] == ' ':
                n += 1
            if n:
                return '&nbsp;' * n + s[n:]
            else:
                return s
        log = '<p>%s</p>' % '</p>\n<p>'.join(map(empty2nbsp, log.splitlines()))

        if import_status is None:
            import_status = ''

        if diff is None:
            diff = ''

        diff = "\n".join(map(self.mark_whitespace, diff.splitlines()))

        def colorize(style):
            return r'<div class="%s">\1</div>' % style

        # Unified diff
        diff = re.sub(r'(?m)^(===.*)$', colorize("file"), diff)
        diff = re.sub(r'(?m)^(---.*)$', colorize("oldfile"), diff)
        diff = re.sub(r'(?m)^(\+\+\+.*)$', colorize("newfile"), diff)
        diff = re.sub(r'(?m)^(@@.*)$', colorize("chunk"), diff)
        diff = re.sub(r'(?m)^(-.*)$', colorize("old"), diff)
        diff = re.sub(r'(?m)^(\+.*)$', colorize("new"), diff)

        # Postprocess for Mozilla
        diff = re.sub('</div>\n', '\n</div>', diff)

        if sig:
            sig = '<div class="signature">%s</div>' % sig

        text = '<pre>%s</pre><div class="log">%s</div><pre>%s%s%s</pre>' \
               % (intro, log, import_status, diff, sig)
        # TODO: find out the actual encoding instead of assuming UTF-8
        return unicode(text, 'UTF-8', 'replace')

    def mark_whitespace(self, line, tab=('>', '-'), trail='.'):
        """Mark whitespace in diff lines.

        Suggested values for tab: ('>', '-'), ('&#187;', ' '),
                                  ('&#187;', '&#x2010;')

        Suggested values for trail: '.', '&#x2423;'
        """
        if line == ' ' or (not line.endswith(' ') and '\t' not in line):
            return line
        m = re.search('\s+\Z', line)
        if m:
            n = m.start()
            if n == 0:
                n = 1 # don't highlight the first space in a diff
            line = '%s<span class="trail">%s</span>' % (line[:n],
                            line[n:].replace(' ', trail))
        if '\t' in line:
            NORMAL, TAG, ENTITY = 0, 1, 2
            idx = col = 0
            mode = NORMAL
            tabs = []
            for c in line[1:]: # ignore first space in a diff
                idx += 1
                if mode == TAG:
                    if c == '>':
                        mode = NORMAL
                elif mode == ENTITY:
                    if c == ';':
                        col += 1
                        mode = NORMAL
                else:
                    if c == '<':
                        mode = TAG
                    elif c == '&':
                        mode = ENTITY
                    elif c == '\t':
                        width = 8 - (col % 8)
                        tabs.append((idx, width))
                        col += width
                    else:
                        col += 1
            if tabs:
                parts = []
                last = 0
                for idx, width in tabs:
                    parts.append(line[last:idx])
                    parts.append('<span class="tab">%s%s</span>'
                                 % (tab[0], tab[1] * (width - 1)))
                    last = idx + 1
                parts.append(line[last:])
                line = "".join(parts)
        return line
