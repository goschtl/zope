"""
Browser views for z3checkins.

$Id$
"""
import re
import mailbox
from StringIO import StringIO

from zope.interface import implements
from zope.exceptions import DuplicationError
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.datetimeutils import parseDatetimetz, DateTimeError
from zope.app.publisher.browser import BrowserView
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import FileWidget
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.pagetemplate import ViewPageTemplateFile

from z3checkins.message import Bookmark
from z3checkins.interfaces import IMessage, ICheckinMessage, IMessageContained
from z3checkins.interfaces import IMessageUpload, IMessageParser, IBookmark

__metaclass__ = type


class MessageUpload:
    """Adding view mixin for uploading checkin messages."""

    implements(IMessageUpload, IMessageContained)
    data_widget = CustomWidgetFactory(FileWidget)

    def createAndAdd(self, data):
        if data.has_key('data'): # TODO should we bark if no data is given?
            msg_raw = data['data']
            parser = zapi.getUtility(IMessageParser)
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
        """Return the description of this archive."""
        return self.context.description

    def archive_url(self):
        """Return the URL for mailing list archives."""
        return self.context.archive_url

    def bookmarks(self):
        """Return a list of bookmarks from a cookie.

        Each bookmark is expressed as a datetime object.
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
        """Place a new bookmark after the latest message in a cookie."""
        if int(self.request.get('start', 0)) > 0:
            return # The user can't see the newest checkins
        if not self.context.messages:
            return # No messages -- no bookmarks
        bookmarks = self.bookmarks()
        bookmarks.sort()
        # Do not insert a bookmark if there were no checkins since the last
        # bookmark
        if (bookmarks and bookmarks[-1] >= self.context.messages[0].date):
            return
        bookmarks.append(self.context.messages[0].date)
        if len(bookmarks) > self.max_bookmarks:
            del bookmarks[:-self.max_bookmarks]
        cookie = " ".join([dt.isoformat() for dt in bookmarks])
        self.request.response.setCookie('bookmarks', cookie,
                                        max_age=365*24*60*60) # 1 year

    def checkins(self, start=None, size=None):
        """Return a list of messages.

        Returns the last 'size' checkin messages in self.context, newest
        first, skipping the first 'start' messages.
        """
        if start is None:
            start = int(self.request.get('start', 0))
        if size is None:
            size = int(self.request.get('size', 20))
        last = start + size
        items = self.context.messages[start:last]
        items = removeAllProxies(items)

        # insert bookmarks

        def bookmarkBetween(msg1, msg2, bookmarks=self.bookmarks()):
            for b in bookmarks:
                if msg1.date > b >= msg2.date:
                    return True
            return False

        n = 0
        while n < len(items) - 1:
            if bookmarkBetween(items[n], items[n+1]):
                items.insert(n+1, Bookmark())
                n += 1
            n += 1
        # insert bookmarks before the first / after the last batch item
        if items:
            before = self.context.messages[:1]
            if before and bookmarkBetween(before[0], items[0]):
                items.insert(0, Bookmark())
            after = self.context.messages[-1:]
            if after and bookmarkBetween(items[-1], after[0]):
                items.append(Bookmark())
        return items

    def renderCheckins(self, start=None, size=None):
        """Return a list of checkins rendered into HTML.

        See `checkins` for description of parameters."""
        html = []
        previous_message = None
        for item in self.checkins(start=start, size=size):
            if ICheckinMessage.providedBy(item):
                same_as_previous = item.log_message == previous_message
                previous_message = item.log_message
            else:
                same_as_previous = None
            view = zapi.getMultiAdapter((item, self.request), name='html')
            output = view(same_as_previous=same_as_previous)
            html.append(output)
        return "".join(html)

    def count(self):
        """Return the number of checkin messages in the archive."""
        return len(self.context.messages)


class MessageRSSView(BrowserView):
    """View for messages.

    Makes sure the page template is treated as XML.
    """

    index = ViewPageTemplateFile('rss_message.pt', content_type='text/xml')


class MessageView:
    """View mixin for messages."""

    _archive = None
    _index = None

    def _calc_index(self):

        if not self.context.__parent__:
            return

        self._archive = self.context.__parent__.messages
        try:
            self._index = self._archive.index(self.context)
        except ValueError:
            pass

    def previous(self):
        """Return the previous message in archive."""
        self._calc_index()
        if self._index is not None and self._index < len(self._archive) - 1:
            return self._archive[self._index + 1]
        else:
            return None

    def next(self):
        """Return the next message in archive."""
        self._calc_index()
        if self._index is not None and self._index > 0:
            return self._archive[self._index - 1]
        else:
            return None

    def last(self):
        """Return the last message in archive."""
        self._calc_index()
        if self._archive:
            return self._archive[0]
        else:
            return None

    def first(self):
        """Return the first message in archive."""
        self._calc_index()
        if self._archive:
            return self._archive[-1]
        else:
            return None

    def icon(self):
        """Return a mapping describing an icon for this checkin."""
        return {'src': '++resource++message.png',
                'alt': 'Message',
                'title': 'Email message'}

    def body(self):
        """Colorize the body of a message."""
        text = self.context.body.replace('\r', '')\
                                .replace('&', '&amp;') \
                                .replace('<', '&lt;') \
                                .replace('>', '&gt;') \
                                .replace('"', '&quot;')
        # It would be nice to highlight quoted text here
        return '<pre>%s</pre>' % text

    def body_plain(self):
        """Return the full text of the message."""
        return self.context.full_text


class CheckinMessageView(MessageView):
    """View mixin for checkin messages."""

    _subtrees = None

    def subtrees(self):
        """Return a sequence of tuples (prefix, icon, alt, title).

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
        """Return a mapping describing an icon for this checkin."""
        for prefix, icon, alt, title in self.subtrees():
            if self.context.directory.startswith(prefix):
                return {'src': '++resource++%s' % icon,
                        'alt': alt,
                        'title': title}
        return {'src': '++resource++product.png',
                'alt': 'Checkin',
                'title': 'Checkin'}

    def body(self):
        """Colorize checkin message body."""
        # TODO This method is rather bloated and hard to understand.
        text = self.context.body.replace('\r', '') \
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
                log_idx = text.find('Log message')
                # This section is specific to Zope3 checkins
                if log_idx != -1:
                    log_idx = text.find('\n', log_idx) + 1
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
            status_idx = text.find('\nChanged:\n')
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
        m = re.search(r'\s+\Z', line)
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
