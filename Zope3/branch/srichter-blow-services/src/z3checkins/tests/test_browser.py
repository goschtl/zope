#!/usr/bin/python
"""
Unit tests for browser.py

$Id$
"""

import unittest
from difflib import SequenceMatcher
from datetime import datetime

from zope.publisher.browser import TestRequest
from zope.interface import Interface, implements
from zope.exceptions import DuplicationError
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup

from z3checkins.interfaces import ICheckinMessage, IBookmark, IMessageParser
from z3checkins.tests.test_message import MessageStub, open_test_data


class ParserStub:

    implements(IMessageParser)

    def parse(self, data):
        if hasattr(data, 'read'):
            full_text = data.read()
        else:
            full_text = data

        message_id = "message@id"
        id_lines = filter(lambda s: s.lower().startswith("message-id: "),
                full_text.splitlines())
        if len(id_lines) == 1:
            message_id = id_lines[0][len("message-id: "):]
        return MessageStub(data=full_text, message_id=message_id)

class AddingStub:

    def __init__(self):
        from z3checkins.folder import CheckinFolder
        self.added = CheckinFolder()

    def add(self, obj):
        # ignore duplicates happening with default messages
        if obj.message_id != "message@id":
            for message in self.added.values():
                if message.message_id == obj.message_id:
                    raise DuplicationError()
        self.added[obj.message_id] = obj

class TestMessageUpload(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        ztapi.provideUtility(IMessageParser, ParserStub())

    def test_createAndAdd(self):
        from z3checkins.browser import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        added = view.context.added
        self.assertEquals(len(added), 0)
        view.createAndAdd({})
        self.assertEquals(len(added), 0)
        view.createAndAdd({'data': 'Ipsum suum'})
        added = list(added.values())
        self.assertEquals(len(added), 1)
        self.assertEquals(added[0].__class__, MessageStub)
        self.assertEquals(added[0].message_id, "message@id")
        self.assertEquals(added[0].data, "Ipsum suum")

    def test_createAndAdd_mbox(self):
        from z3checkins.browser import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        data = open_test_data('mbox.txt').read()
        self.assertEquals(len(view.context.added), 0)
        view.createAndAdd({'data': data})
        added = list(view.context.added.values())
        self.assertEquals(len(added), 4)
        for message in added:
            self.assertEquals(message.__class__, MessageStub)
        self.assertEquals(added[0].data.count("Steve Alexander"), 1)
        self.assertEquals(added[1].data.count("Steve Alexander"), 1)
        self.assertEquals(added[2].data.count("Tim Peters"), 1)
        self.assertEquals(added[3].data.count("Tim Peters"), 1)

    def test_createAndAdd_mbox_with_dupes(self):
        from z3checkins.browser import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        data = open_test_data('mbox_with_dupes.txt').read()
        self.assertEquals(len(view.context.added), 0)
        view.createAndAdd({'data': data})
        added = list(view.context.added.values())
        self.assertEquals(len(added), 2)
        for message in added:
            self.assertEquals(message.__class__, MessageStub)
        self.assertEquals(added[0].data.count("Steve Alexander"), 1)
        self.assertEquals(added[1].data.count("Tim Peters"), 1)


class MessageTestView:
    def __init__(self, context, request):
        self.context = context
    def __call__(self, same_as_previous=False):
        result = 'msg%d' % self.context.date
        if same_as_previous:
            result += '*'
        return result + '\n'

class BookmarkTestView:
    def __init__(self, context, request):
        self.context = context
    def __call__(self, same_as_previous=False):
        return '-\n'

class RequestStub(dict):

    _cookies = ()

    def __init__(self, **kw):
        super(RequestStub, self).__init__()
        self.update(kw)
        self.response = self

    def setCookie(self, name, value, **kw):
        self._cookies += (name, value, kw)

    def getPresentationType(self):
        class IUnitTestPresentation(Interface):
            pass
        return IUnitTestPresentation


class TestContainerView(PlacelessSetup, unittest.TestCase):

    def test_checkins(self):
        from z3checkins.browser import ContainerView
        view = ContainerView()
        view.context = create_checkin_folder(
                 {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                  'a': MessageStub(date=2), 'c': MessageStub(date=3)})
        view.request = {}
        res = view.checkins()
        self.assertEquals(len(res), 3)
        self.assertEquals(view.count(), 3)
        self.assertEquals(res[0].date, 3)
        self.assertEquals(res[1].date, 2)
        self.assertEquals(res[2].date, 1)

    def test_checkins_limited(self):
        from z3checkins.browser import ContainerView
        view = ContainerView()
        view.context = create_checkin_folder(
                 {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                  'a': MessageStub(date=2), 'c': MessageStub(date=3)})
        view.request = {}
        res = view.checkins(size=2)
        self.assertEquals(len(res), 2)
        self.assertEquals(res[0].date, 3)
        self.assertEquals(res[1].date, 2)

        res = view.checkins(start=1, size=3)
        self.assertEquals(len(res), 2)
        self.assertEquals(res[0].date, 2)
        self.assertEquals(res[1].date, 1)

    def test_checkins_bookmarks(self):
        from z3checkins.browser import ContainerView
        view = ContainerView()
        view.context = create_checkin_folder(
                 {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                  'a': MessageStub(date=2), 'c': MessageStub(date=4)})
        view.request = {}
        view.bookmarks = lambda: [3]
        res = view.checkins()
        self.assertEquals(len(res), 4)
        self.assertEquals(res[0].date, 4)
        self.assert_(IBookmark.providedBy(res[1]))
        self.assertEquals(res[2].date, 2)
        self.assertEquals(res[3].date, 1)

        view.bookmarks = lambda: [2]
        res = view.checkins()
        self.assertEquals(len(res), 4)
        self.assertEquals(res[0].date, 4)
        self.assert_(IBookmark.providedBy(res[1]))
        self.assertEquals(res[2].date, 2)
        self.assertEquals(res[3].date, 1)

        view.bookmarks = lambda: [0, 1, 2, 3, 4, 5, 6, 2, 3, 1]
        res = view.checkins()
        self.assertEquals(len(res), 5)
        self.assertEquals(res[0].date, 4)
        self.assert_(IBookmark.providedBy(res[1]))
        self.assertEquals(res[2].date, 2)
        self.assert_(IBookmark.providedBy(res[3]))
        self.assertEquals(res[4].date, 1)

        res = view.checkins(start=1, size=1)
        self.assertEquals(len(res), 3)
        self.assert_(IBookmark.providedBy(res[0]))
        self.assertEquals(res[1].date, 2)
        self.assert_(IBookmark.providedBy(res[2]))

    def test_bookmarks(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.request = {}
        self.assertEquals(view.bookmarks(), [])
        view.request = {'bookmarks': '2003-01-04T21:33:04-05:00'}
        self.assertEquals(view.bookmarks(),
                          [datetime(2003, 01, 04, 21, 33, 04,
                                    tzinfo=FixedTimezone(-5*60))])
        view.request = {'bookmarks': '2003-01-04T21:33:04-05:00 '
                                     'errors are ignored '
                                     '2004-05-06T07:08:09+10:00 '
                                     '2002-02-02T02:02:02+02:00 '
                                     '2005-02-29T07:08:09+10:00'}
        self.assertEquals(view.bookmarks(),
                          [datetime(2003, 1, 4, 21, 33, 4,
                                    tzinfo=FixedTimezone(-5*60)),
                           datetime(2004, 5, 6, 7, 8, 9,
                                    tzinfo=FixedTimezone(10*60)),
                           datetime(2002, 2, 2, 2, 2, 2,
                                    tzinfo=FixedTimezone(2*60))])

    def test_placeBookmark_empty_archive(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = create_checkin_folder({})
        view.request = RequestStub()
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_empty_bookmarks(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))})
        view.request = RequestStub()
        view.placeBookmark()
        self.assertEquals(view.request._cookies,
                          ('bookmarks', '2003-01-04T21:33:04-05:00',
                           {'max_age': 31536000}))

    def test_placeBookmark_not_at_start(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))}
        view.request = RequestStub(start=1)
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_no_new_checkins(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = create_checkin_folder(
                {'x': 123, 'y': object(),
                 'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))})
        view.request = RequestStub(bookmarks='2003-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-02-02T02:02:02+02:00')
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))})
        view.request = RequestStub(bookmarks='2004-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-02-02T02:02:02+02:00')
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_new_checkins(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60))),
                        'w': MessageStub(date=datetime(2003, 1, 6, 22, 33, 44,
                                                tzinfo=FixedTimezone(+3*60)))})
        view.request = RequestStub(bookmarks='2003-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-02-02T02:02:02+02:00')
        view.placeBookmark()
        self.assertEquals(view.request._cookies,
                          ('bookmarks', '2002-02-02T02:02:02+02:00 '
                                        '2003-01-04T21:33:04-05:00 '
                                        '2003-01-06T22:33:44+03:00',
                           {'max_age': 31536000}))

    def test_placeBookmark_new_checkins_overflow(self):
        from z3checkins.browser import ContainerView
        from z3checkins.timeutils import FixedTimezone
        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60))),
                        'w': MessageStub(date=datetime(2003, 1, 6, 22, 33, 44,
                                                tzinfo=FixedTimezone(+3*60)))})
        view.request = RequestStub(bookmarks='2003-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-01-01T02:02:02+02:00 '
                                             '2002-01-02T02:02:02+02:00 '
                                             '2002-01-03T02:02:02+02:00 '
                                             '2002-01-04T02:02:02+02:00 '
                                             '2002-02-02T02:02:02+02:00 ')
        view.placeBookmark()
        self.assertEquals(view.request._cookies,
                          ('bookmarks', '2002-01-03T02:02:02+02:00 '
                                        '2002-01-04T02:02:02+02:00 '
                                        '2002-02-02T02:02:02+02:00 '
                                        '2003-01-04T21:33:04-05:00 '
                                        '2003-01-06T22:33:44+03:00',
                           {'max_age': 31536000}))

    def test_renderCheckins(self):
        from z3checkins.browser import ContainerView
        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=1, log_message='xxx'),
                        'a': MessageStub(date=2, log_message='xxx'),
                        'c': MessageStub(date=3, log_message='yyy')})
        view.request = TestRequest()
        view.index = view
        ztapi.browserView(ICheckinMessage, 'html', MessageTestView)

        res = view.renderCheckins()
        self.assertEquals(res, 'msg3\nmsg2\nmsg1*\n')
        res = view.renderCheckins(start=1, size=1)
        self.assertEquals(res, 'msg2\n')

    def test_renderCheckins_with_bookmarks(self):
        from z3checkins.browser import ContainerView
        view = ContainerView()
        view.context = create_checkin_folder(
                       {'x': 123, 'y': object(),
                        'z': MessageStub(date=1, log_message='xxx'),
                        'a': MessageStub(date=2, log_message='xxx'),
                        'c': MessageStub(date=3, log_message='yyy')})
        view.request = TestRequest()
        view.index = view
        view.bookmarks = lambda: [1]
        ztapi.browserView(ICheckinMessage, 'html', MessageTestView)
        ztapi.browserView(IBookmark, 'html', BookmarkTestView)

        res = view.renderCheckins()
        self.assertEquals(res, 'msg3\nmsg2\n-\nmsg1*\n')


def create_checkin_folder(values):
    from z3checkins.folder import CheckinFolder
    folder = CheckinFolder()
    for key, value in values.items():
        folder[key] = value
    return folder


class TestCheckinMessageView(unittest.TestCase):

    def test_body_strange(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Something & strange")
        self.assertEquals(view.body(), "<pre>Something &amp; strange</pre>")

    def test_body(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Blah blah\n"
                          "blah\n"
                          "Log message:\n"
                          "Blurb blurb\n"
                          "blurb.\n"
                          "\n"
                          "=== foo.py: 1.2 -> 1.3 ===\n"
                          "--- foo.py:1.2\tdatetime\n"
                          "+++ foo.py\tdatetime\n"
                          "@@@ -123,4 +567,8 @@@\n"
                          " fwoosh <>&\"\n"
                          "-fouoww\n"
                          "+fruuuh\n"
                          " fargle\n"
                          "_______________________________________________\n"
                          "signature\n")
        self.assertEquals(view.body_plain(), "full text of this message")
        result = view.body()
        expected = ('<pre>Blah blah\n'
                    'blah\n'
                    'Log message:\n'
                    '</pre>'
                    '<div class="log">'
                    '<p>Blurb blurb</p>\n'
                    '<p>blurb.</p>'
                    '</div>'
                    '<pre>\n'
                    '<div class="file">=== foo.py: 1.2 -&gt; 1.3 ===\n</div>'
                    '<div class="oldfile">--- foo.py:1.2<span class="tab">>--</span>datetime\n</div>'
                    '<div class="newfile">+++ foo.py<span class="tab">>------</span>datetime\n</div>'
                    '<div class="chunk">@@@ -123,4 +567,8 @@@\n</div>'
                    ' fwoosh &lt;&gt;&amp;&quot;\n'
                    '<div class="old">-fouoww\n</div>'
                    '<div class="new">+fruuuh\n</div>'
                    ' fargle'
                    '<div class="signature">\n'
                    '_______________________________________________\n'
                    'signature\n'
                    '</div>'
                    '</pre>')
        self.assertEquals(result, expected, diff(expected, result))

    def test_body_svn(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="""\
Author: mg
Date: 2003-09-09 21:21:09 +0300 (Tue, 09 Sep 2003)
New Revision: 15

Added:
   trunk/schooltool/schooltool/ftests/
   trunk/schooltool/schooltool/ftests/__init__.py
   trunk/schooltool/schooltool/ftests/test_rest.py
   trunk/schooltool/schooltool/main.py
   trunk/schooltool/schooltool/tests/test_main.py
Removed:
   trunk/schooltool/schooltool/tests/test_rest.py
Modified:
   trunk/schooltool/schooltool/tests/__init__.py
Log:
First prototype of SchoolTool HTTP server that serves RESTful pages, complete
with unit and functional tests.



Added: trunk/schooltool/schooltool/ftests/__init__.py
===================================================================
--- trunk/schooltool/schooltool/ftests/__init__.py	2003-09-09 18:03:43 UTC (rev 14)
+++ trunk/schooltool/schooltool/ftests/__init__.py	2003-09-09 18:21:09 UTC (rev 15)
@@ -0,0 +1,21 @@
+#
+# SchoolTool - common information systems platform for school administration
"""
)
        result = view.body()
        expected = ("""\
<pre>Author: mg
Date: 2003-09-09 21:21:09 +0300 (Tue, 09 Sep 2003)
New Revision: 15

Added:
   trunk/schooltool/schooltool/ftests/
   trunk/schooltool/schooltool/ftests/__init__.py
   trunk/schooltool/schooltool/ftests/test_rest.py
   trunk/schooltool/schooltool/main.py
   trunk/schooltool/schooltool/tests/test_main.py
Removed:
   trunk/schooltool/schooltool/tests/test_rest.py
Modified:
   trunk/schooltool/schooltool/tests/__init__.py
Log:
</pre><div class="log"><p>First prototype of SchoolTool HTTP server that serves RESTful pages, complete</p>
<p>with unit and functional tests.</p></div><pre>
Added: trunk/schooltool/schooltool/ftests/__init__.py
<div class="file">===================================================================
</div><div class="oldfile">--- trunk/schooltool/schooltool/ftests/__init__.py<span class="tab">>------</span>2003-09-09 18:03:43 UTC (rev 14)
</div><div class="newfile">+++ trunk/schooltool/schooltool/ftests/__init__.py<span class="tab">>------</span>2003-09-09 18:21:09 UTC (rev 15)
</div><div class="chunk">@@ -0,0 +1,21 @@
</div><div class="new">+#
</div><div class="new">+# SchoolTool - common information systems platform for school administration</div></pre>"""
                    )
        self.assertEquals(result, expected, diff(expected, result))

    def test_body_crlf(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Blah blah\r\n"
                          "blah\r\n"
                          "Log message:\r\n"
                          "Blurb blurb\r\n"
                          "blurb.\r\n"
                          "\r\n"
                          "=== foo.py: 1.2 -> 1.3 ===\r\n"
                          "--- foo.py:1.2\tdatetime\r\n"
                          "+++ foo.py\tdatetime\r\n"
                          "@@@ -123,4 +567,8 @@@\r\n"
                          " fwoosh <>&\"\r\n"
                          "-fouoww  \r\n"
                          "+fruuuh\r\n"
                          " fargle\r\n"
                          "   \r\n"
                          " \r\n"
                          "_______________________________________________\r\n"
                          "signature\r\n")
        result = view.body()
        expected = ('<pre>Blah blah\n'
                    'blah\n'
                    'Log message:\n'
                    '</pre>'
                    '<div class="log">'
                    '<p>Blurb blurb</p>\n'
                    '<p>blurb.</p>'
                    '</div>'
                    '<pre>\n'
                    '<div class="file">=== foo.py: 1.2 -&gt; 1.3 ===\n</div>'
                    '<div class="oldfile">--- foo.py:1.2<span class="tab">>--</span>datetime\n</div>'
                    '<div class="newfile">+++ foo.py<span class="tab">>------</span>datetime\n</div>'
                    '<div class="chunk">@@@ -123,4 +567,8 @@@\n</div>'
                    ' fwoosh &lt;&gt;&amp;&quot;\n'
                    '<div class="old">-fouoww<span class="trail">..</span>\n</div>'
                    '<div class="new">+fruuuh\n</div>'
                    ' fargle\n'
                    ' <span class="trail">..</span>\n'
                    ' '
                    '<div class="signature">\n'
                    '_______________________________________________\n'
                    'signature\n'
                    '</div>'
                    '</pre>')
        self.assertEquals(result, expected, diff(expected, result))

    def test_body_nosig(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Blah blah\n"
                          "blah\n"
                          "Log message:\n"
                          "Blurb blurb\n"
                          "blurb.\n"
                          "\n"
                          "=== foo.py: 1.2 -> 1.3 ===\n"
                          "--- foo.py:1.2\tdatetime\n"
                          "+++ foo.py\tdatetime\n"
                          "@@@ -123,4 +567,8 @@@\n"
                          " fwoosh <>&\"\n"
                          "-fouoww\n"
                          "+fruuuh\n"
                          " fargle")
        result = view.body()
        expected = ('<pre>Blah blah\n'
                    'blah\n'
                    'Log message:\n'
                    '</pre>'
                    '<div class="log">'
                    '<p>Blurb blurb</p>\n'
                    '<p>blurb.</p>'
                    '</div>'
                    '<pre>\n'
                    '<div class="file">=== foo.py: 1.2 -&gt; 1.3 ===\n</div>'
                    '<div class="oldfile">--- foo.py:1.2<span class="tab">>--</span>datetime\n</div>'
                    '<div class="newfile">+++ foo.py<span class="tab">>------</span>datetime\n</div>'
                    '<div class="chunk">@@@ -123,4 +567,8 @@@\n</div>'
                    ' fwoosh &lt;&gt;&amp;&quot;\n'
                    '<div class="old">-fouoww\n</div>'
                    '<div class="new">+fruuuh\n</div>'
                    ' fargle'
                    '</pre>')
        self.assertEquals(result, expected, diff(expected, result))

    def test_body_importmsg(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Blah blah\n"
                          "blah\n"
                          "Log message:\n"
                          "Blurb blurb\n"
                          "blurb.\n"
                          "\n"
                          "Status:\n"
                          "\n"
                          "Vendor Tag:\tnovendor\n"
                          "Release Tags:\tstart\n"
                          "\n"
                          "N foo/bar.py\n"
                          "N foo/baz.pt\n"
                          "\n"
                          "No conflicts created by this import\n")
        result = view.body()
        expected = ('<pre>Blah blah\n'
                    'blah\n'
                    'Log message:\n'
                    '</pre>'
                    '<div class="log">'
                    '<p>Blurb blurb</p>\n'
                    '<p>blurb.</p>'
                    '</div>'
                    '<pre>\n'
                    'Status:\n'
                    '\n'
                    'Vendor Tag:\tnovendor\n'
                    'Release Tags:\tstart\n'
                    '\n'
                    'N foo/bar.py\n'
                    'N foo/baz.pt\n'
                    '\n'
                    'No conflicts created by this import\n'
                    '</pre>')
        self.assertEquals(result, expected, diff(expected, result))

    def test_markwitespace(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        m = view.mark_whitespace
        self.assertEquals(m(''), '')
        self.assertEquals(m('xyzzy'), 'xyzzy')
        self.assertEquals(m('  '), ' <span class="trail">.</span>')
        self.assertEquals(m('  xy z  '), '  xy z<span class="trail">..</span>')
        self.assertEquals(m('  xy z \t '), '  xy z<span class="trail">.<span class="tab">>-</span>.</span>')
        self.assertEquals(m(' \t|'), ' <span class="tab">>-------</span>|')
        self.assertEquals(m(' |\t|'), ' |<span class="tab">>------</span>|')
        self.assertEquals(m(' xxxxxx|\t|'), ' xxxxxx|<span class="tab">></span>|')
        self.assertEquals(m(' x<tag\t>xxxxx|\t|'), ' x<tag\t>xxxxx|<span class="tab">></span>|')
        self.assertEquals(m(' x&ent;xxxx|\t|'), ' x&ent;xxxx|<span class="tab">></span>|')

    def test_urls(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        prefixes = ['', 'A link: ', '(', '<']
        suffixes = ['', ' etc.', ')', '>', '.', ',', '\n']
        urls = ['http://www.example.com', 'https://www.example.com', 'http://localhost:8080/foo?q=a&w=b']

        def quote(text):
            return (text.replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('"', '&quot;'))

        for prefix in prefixes:
            for link in urls:
                for suffix in suffixes:
                    view.context = MessageStub(body="%s%s%s" % (prefix, link, suffix))
                    prefix = quote(prefix)
                    link = quote(link)
                    suffix = quote(suffix)
                    self.assertEquals(view.body(), '<pre>%s<a href="%s">%s</a>%s</pre>' % (prefix, link, link, suffix))

    def test_navigation_no_archive(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub()
        self.assertEquals(view.first(), None)
        self.assertEquals(view.last(), None)
        self.assertEquals(view.next(), None)
        self.assertEquals(view.previous(), None)

    def test_navigation_empty_archive(self):
        from z3checkins.browser import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub()
        view.context.__parent__ = create_checkin_folder({'1': 2})
        self.assertEquals(view.first(), None)
        self.assertEquals(view.last(), None)
        self.assertEquals(view.next(), None)
        self.assertEquals(view.previous(), None)

    def test_navigation(self):
        from z3checkins.browser import CheckinMessageView
        m1 = MessageStub(date=1, message_id='1')
        m2 = MessageStub(date=2, message_id='2')
        m3 = MessageStub(date=3, message_id='3')
        m4 = MessageStub(date=4, message_id='4')

        folder = create_checkin_folder(
                    {'1': 2, '3': 'abc', '4': m1, '5': m2, '6': m3, '7': m4})
        view = CheckinMessageView()
        view.context = m3
        m3.__parent__ = folder
        self.assertEquals(view.first(), m1)
        self.assertEquals(view.last(), m4)
        self.assertEquals(view.next(), m4)
        self.assertEquals(view.previous(), m2)

        view = CheckinMessageView()
        view.context = m1
        m1.__parent__ = folder
        self.assertEquals(view.first(), m1)
        self.assertEquals(view.last(), m4)
        self.assertEquals(view.next(), m2)
        self.assertEquals(view.previous(), None)

        view = CheckinMessageView()
        view.context = m4
        m4.__parent__ = folder
        self.assertEquals(view.first(), m1)
        self.assertEquals(view.last(), m4)
        self.assertEquals(view.next(), None)
        self.assertEquals(view.previous(), m3)


def diff(a, b):
    """Outline the differences of two sequences of strings."""
    if isinstance(a, (str, unicode)): a = a.splitlines()
    if isinstance(b, (str, unicode)): b = b.splitlines()

    diff = []
    def dump(tag, x, lo, hi, diff=diff):
        for i in xrange(lo, hi):
            diff.append(tag + x[i])

    differ = SequenceMatcher(a=a, b=b)
    for tag, alo, ahi, blo, bhi in differ.get_opcodes():
        if tag == 'replace':
            dump('-', a, alo, ahi)
            dump('+', b, blo, bhi)
        elif tag == 'delete':
            dump('-', a, alo, ahi)
        elif tag == 'insert':
            dump('+', b, blo, bhi)
        elif tag == 'equal':
            dump(' ', a, alo, ahi)
        else:
            raise ValueError, 'unknown tag ' + `tag`
    return "\n".join(diff)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMessageUpload))
    suite.addTest(unittest.makeSuite(TestContainerView))
    suite.addTest(unittest.makeSuite(TestCheckinMessageView))
    return suite


if __name__ == "__main__":
    unittest.main()
