#!/usr/bin/python
"""
Unit tests for message.py

$Id: test_message.py,v 1.26 2004/03/26 22:18:08 gintautasm Exp $
"""

import unittest
import os
import sys
import time
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService, servicenames
from zope.interface import Interface, implements
from zope.interface.verify import verifyObject
from zope.exceptions import DuplicationError

from z3checkins.interfaces import IMessage, IMessageContained, \
        ICheckinMessage, IBookmark, IMessageParser, IMessageArchive


class TestFixedTimezone(unittest.TestCase):

    def test_timezone(self):
        from z3checkins.message import FixedTimezone
        for tzoff, name in ((30, "+0030"), (-300, "-0500")):
            tz = FixedTimezone(tzoff)
            self.assertEquals(tz.tzname(None), name)
            self.assertEquals(tz.utcoffset(None), timedelta(minutes=tzoff))
            self.assertEquals(tz.dst(None), timedelta(0))


class TestRFCDateTimeFormatter(unittest.TestCase):

    times = ((2003, 4, 2, 12, 33, 41, 3*60, "Wed, 02 Apr 2003 12:33:41 +0300"),
             (2000, 1, 2, 17, 41, 33, -5*60, "Sun, 02 Jan 2000 17:41:33 -0500"))

    def test_rfctime(self):
        from z3checkins.message import FixedTimezone, RFCDateTimeFormatter
        for Y, M, D, h, m, s, tz, res in self.times:
            dt = datetime(Y, M, D, h, m, s, tzinfo=FixedTimezone(tz))
            view = RFCDateTimeFormatter(dt, None)
            self.assertEquals(str(view), res)
            self.assertEquals(view(), res)


class TestISODateTimeFormatter(unittest.TestCase):

    times = ((2003, 4, 2, 12, 33, 41, 3*60, "2003-04-02 09:33"),
             (2000, 1, 2, 17, 41, 33, -5*60, "2000-01-02 22:41"))

    def test_usertz(self):
        from z3checkins.message import ISODateTimeFormatter
        t = time.time()
        delta = ISODateTimeFormatter.userstz._offset * 60
        self.assertEquals(time.gmtime(t)[:8], time.localtime(t - delta)[:8])

    def test_isotime(self):
        from z3checkins.message import FixedTimezone, ISODateTimeFormatter
        for Y, M, D, h, m, s, tz, res in self.times:
            dt = datetime(Y, M, D, h, m, s, tzinfo=FixedTimezone(tz))
            dt -= ISODateTimeFormatter.userstz.utcoffset(None)
            view = ISODateTimeFormatter(dt, None)
            self.assertEquals(str(view), res)
            self.assertEquals(view(), res)


class TestCheckinMessage(unittest.TestCase):

    def test_find_body_start(self):
        from z3checkins.message import find_body_start
        self.assertEquals(find_body_start("Foo: X\nBar: Y\n  Z\n\nQQQ"), 19)
        self.assertEquals(find_body_start("Foo: X\r\nBar: Y\r\n  Z\r\n\r\nQQQ"),
                          23)
        self.assertEquals(find_body_start("Foo: X\n\nQQQ\n\nWWW"), 8)
        self.assertEquals(find_body_start("Foo: X\n\n\nQQQ\n\nWWW"), 8)
        self.assertEquals(find_body_start("Foo: X\n\nQQQ\r\n\r\nWWW"), 8)
        self.assertEquals(find_body_start("Foo: X\r\n\r\nQQQ\n\nWWW"), 10)
        self.assertEquals(find_body_start("Foo: X\n\n"), 8)
        self.assertEquals(find_body_start("\r\n\r\n"), 4)
        self.assertEquals(find_body_start("xyzzy"), 5)

    def test_interface(self):
        from z3checkins.message import Message
        from z3checkins.message import CheckinMessage
        verifyObject(IMessage, Message())
        verifyObject(ICheckinMessage, CheckinMessage())

    def test_body(self):
        from z3checkins.message import Message
        m = Message(full_text="Subject: foo\n\nBody text\n")
        self.assertEquals(m.body, "Body text\n")

    def test_equality(self):
        from z3checkins.message import Message
        a = Message(message_id="abc")
        b = Message(message_id="abc")
        c = Message(message_id="xyz")
        self.assertEquals(a, b)
        self.assertNotEquals(a, c)
        self.assertNotEquals(b, c)


class TestCheckinMessageParser(unittest.TestCase):

    def test_interface(self):
        from z3checkins.message import CheckinMessageParser
        verifyObject(IMessageParser, CheckinMessageParser())

    def test_parser1(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        sample_msg1 = open_test_data("sample_msg1.txt")
        sample_msg1_text = sample_msg1.read()
        sample_msg1.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(sample_msg1)
        self.assert_(ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "42@bar.com")
        self.assertEquals(msg.author_name, "Foo Bar")
        self.assertEquals(msg.author_email, "foo.bar@bar.com")
        self.assertEquals(msg.date, datetime(2003, 03, 28, 11, 58, 05,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.directory, "Zope3/src/foo/bar")
        self.assertEquals(msg.branch, None)
        self.assertEquals(msg.log_message, """\
Ipsum suum dolores quantum est er nonsensicum textum writum esmum inum tuum
lineum furum testum logum messageum.""")
        self.assertEquals(msg.body,
                          sample_msg1_text.split("\n\n", 1)[1])

    def test_parser2(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        sample_msg2 = open_test_data("sample_msg2.txt")
        sample_msg2_text = sample_msg2.read()
        sample_msg2.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(sample_msg2)
        self.assert_(ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "42@bar.com")
        self.assertEquals(msg.author_name, "Foo Bar")
        self.assertEquals(msg.author_email, "foo.bar@bar.com")
        self.assertEquals(msg.date, datetime(2003, 03, 28, 11, 58, 05,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.directory, "Zope3/src/foo/bar")
        self.assertEquals(msg.branch, "foo-branch")
        self.assertEquals(msg.log_message, """\
Ipsum suum dolores quantum est er nonsensicum textum writum esmum inum tuum
lineum furum testum logum messageum.""")
        self.assertEquals(msg.body,
                          sample_msg2_text.split("\n\n", 1)[1])

    def test_parser_empty(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.interfaces import FormatError
        parser = CheckinMessageParser()
        self.assertRaises(FormatError, parser.parse, '')

    def test_parser_importmsg(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        sample_import_msg = open_test_data("sample_import_msg.txt")
        sample_import_msg_text = sample_import_msg.read()
        sample_import_msg.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(sample_import_msg)
        self.assert_(ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "42@bar.com")
        self.assertEquals(msg.author_name, "Foo Bar")
        self.assertEquals(msg.author_email, "foo.bar@bar.com")
        self.assertEquals(msg.date, datetime(2003, 03, 28, 11, 58, 05,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.directory, "Zope3/src/foo/bar")
        self.assertEquals(msg.branch, None)
        self.assertEquals(msg.log_message, """\
Ipsum suum dolores quantum est er nonsensicum textum writum esmum inum tuum
lineum furum testum logum messageum.""")
        self.assertEquals(msg.body,
                          sample_import_msg_text.split("\n\n", 1)[1])

    def test_parser_simplemsg(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        simple_msg = open_test_data("simple_msg.txt")
        simple_msg_text = simple_msg.read()
        simple_msg.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(simple_msg)
        self.assert_(IMessage.providedBy(msg))
        self.assert_(not ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "q$w$e$r$t$y@example.com")
        self.assertEquals(msg.author_name, "John Doe")
        self.assertEquals(msg.author_email, "john@example.com")
        self.assertEquals(msg.date, datetime(2003, 07, 29, 14, 42, 11,
                                             tzinfo=FixedTimezone(2*60)))
        self.assertEquals(msg.body, simple_msg_text.split("\n\n", 1)[1])

    def test_parser_svnmsg(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        svn_msg = open_test_data("svn_msg.txt")
        svn_msg_text = svn_msg.read()
        svn_msg.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(svn_msg)
        self.assert_(ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "20030908101551.6F900C32F@mail.pov.lt")
        self.assertEquals(msg.author_name, "Albertas Agejevas")
        self.assertEquals(msg.author_email, "alga@pov.lt")
        self.assertEquals(msg.date, datetime(2003, 9, 8, 13, 15, 51,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.directory, "trunk/schooltool")
        self.assertEquals(msg.branch, None)
        self.assertEquals(msg.log_message, """Added a period.""")
        self.assertEquals(msg.body,
                          svn_msg_text.split("\n\n", 1)[1])

    def test_parser_svnmsg_with_split_subject(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        svn_msg2 = open_test_data("svn_msg2.txt")
        svn_msg2_text = svn_msg2.read()
        svn_msg2.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(svn_msg2)
        self.assert_(ICheckinMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "20030908101551.6F900C32F@mail.pov.lt")
        self.assertEquals(msg.author_name, "Albertas Agejevas")
        self.assertEquals(msg.author_email, "alga@pov.lt")
        self.assertEquals(msg.date, datetime(2003, 9, 8, 13, 15, 51,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.directory, "trunk/schooltool")
        self.assertEquals(msg.branch, None)
        self.assertEquals(msg.log_message, """Added a period.""")
        self.assertEquals(msg.body,
                          svn_msg2_text.split("\n\n", 1)[1])

    def test_parser_svnmsg_with_rev(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.message import FixedTimezone
        svn_msg3 = open_test_data("svn_msg3.txt")
        svn_msg3_text = svn_msg3.read()
        svn_msg3.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(svn_msg3)
        self.assert_(IMessage.providedBy(msg))
        self.assertEquals(msg.message_id, "20030909101551.6F900C32F@mail.pov.lt")
        self.assertEquals(msg.author_name, "Albertas Agejevas")
        self.assertEquals(msg.author_email, "alga@pov.lt")
        self.assertEquals(msg.date, datetime(2003, 9, 8, 13, 15, 51,
                                             tzinfo=FixedTimezone(3*60)))
        self.assertEquals(msg.body, svn_msg3_text.split("\n\n", 1)[1])


class MessageStub:

    implements(ICheckinMessage, IMessageContained)

    __name__ = __parent__ = None

    def __init__(self, data=None, date=None, body=None, log_message='',
                       subject='', message_id="message@id"):
        self.data = data
        self.date = date
        self.body = body
        self.subject = subject
        self.log_message = log_message
        self.message_id = message_id


class TestMessageContainerAdapter(unittest.TestCase):

    def test_interface(self):
        from z3checkins.message import MessageContainerAdapter
        verifyObject(IMessageArchive, MessageContainerAdapter({}))

    def test_len(self):
        from z3checkins.message import MessageContainerAdapter
        a = MessageContainerAdapter({})
        self.assertEquals(len(a), 0)
        a = MessageContainerAdapter({'1': 2, '3': 'abc'})
        self.assertEquals(len(a), 0)
        a = MessageContainerAdapter({'1': 2, '3': 'abc', 4: MessageStub()})
        self.assertEquals(len(a), 1)

    def test_getitem(self):
        from z3checkins.message import MessageContainerAdapter
        a = MessageContainerAdapter({'1': 2, '3': 'abc',
                                     '4': MessageStub(date=1, message_id='1'),
                                     '5': MessageStub(date=4, message_id='2'),
                                     '6': MessageStub(date=3, message_id='3'),
                                     '7': MessageStub(date=2, message_id='4')})
        self.assertEquals(a[0].message_id, '1')
        self.assertEquals(a[1].message_id, '4')
        self.assertEquals(a[2].message_id, '3')
        self.assertEquals(a[3].message_id, '2')
        self.assertEquals(a[-1].message_id, '2')
        self.assertRaises(IndexError, a.__getitem__, 4)
        self.assertRaises(IndexError, a.__getitem__, -5)
        self.assertRaises(TypeError, a.__getitem__, 'xyzzy')
        self.assertRaises(TypeError, a.__getitem__, None)
        self.assertEquals(len(a[1:3]), 2)
        self.assertEquals(len(a[1:-1]), 2)
        self.assertEquals(len(a[3:1]), 0)

    def test_iter(self):
        from z3checkins.message import MessageContainerAdapter
        a = MessageContainerAdapter({'1': 2, '3': 'abc',
                                     '4': MessageStub(date=1, message_id='1'),
                                     '5': MessageStub(date=4, message_id='2'),
                                     '6': MessageStub(date=3, message_id='3'),
                                     '7': MessageStub(date=2, message_id='4')})
        b = [x.message_id for x in a]
        self.assertEquals(b, ['1', '4', '3', '2'])
        self.assert_(MessageStub(message_id='5') not in a)
        self.assert_(a.context['6'] in a)

    def test_index(self):
        from z3checkins.message import MessageContainerAdapter
        m1 = MessageStub(date=1, message_id='1')
        m2 = MessageStub(date=4, message_id='2')
        m3 = MessageStub(date=3, message_id='3')
        m4 = MessageStub(date=2, message_id='4')
        a = MessageContainerAdapter({'1': 2, '3': 'abc',
                                     '4': m1, '5': m2, '6': m3, '7': m4})
        self.assertEquals(a.index(m1), 0)
        self.assertEquals(a.index(m4), 1)
        self.assertEquals(a.index(m3), 2)
        self.assertEquals(a.index(m2), 3)
        self.assertRaises(ValueError, a.index, MessageStub)


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
        self.added = []

    def add(self, obj):
        # ignore duplicates happening with default messages
        if obj.message_id != "message@id":
            for message in self.added:
                if message.message_id == obj.message_id:
                    raise DuplicationError()
        self.added.append(obj)

class TestMessageUpload(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None, 'Utilities').provideUtility(IMessageParser,
                                                     ParserStub())

    def test_createAndAdd(self):
        from z3checkins.message import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        added = view.context.added
        self.assertEquals(len(added), 0)
        view.createAndAdd({})
        self.assertEquals(len(added), 0)
        view.createAndAdd({'data': 'Ipsum suum'})
        self.assertEquals(len(added), 1)
        self.assertEquals(added[0].__class__, MessageStub)
        self.assertEquals(added[0].message_id, "message@id")
        self.assertEquals(added[0].data, "Ipsum suum")

    def test_createAndAdd_mbox(self):
        from z3checkins.message import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        added = view.context.added
        data = open_test_data('mbox.txt').read()
        self.assertEquals(len(added), 0)
        view.createAndAdd({'data': data})
        self.assertEquals(len(added), 4)
        for message in added:
            self.assertEquals(message.__class__, MessageStub)
        self.assertEquals(added[0].data.count("Steve Alexander"), 1)
        self.assertEquals(added[1].data.count("Steve Alexander"), 1)
        self.assertEquals(added[2].data.count("Tim Peters"), 1)
        self.assertEquals(added[3].data.count("Tim Peters"), 1)

    def test_createAndAdd_mbox_with_dupes(self):
        from z3checkins.message import MessageUpload
        view = MessageUpload()
        view.context = AddingStub()
        view.add = view.context.add
        added = view.context.added
        data = open_test_data('mbox_with_dupes.txt').read()
        self.assertEquals(len(added), 0)
        view.createAndAdd({'data': data})
        self.assertEquals(len(added), 2)
        for message in added:
            self.assertEquals(message.__class__, MessageStub)
        self.assertEquals(added[0].data.count("Steve Alexander"), 1)
        self.assertEquals(added[1].data.count("Tim Peters"), 1)


class IUnitTestPresentation(Interface):
    pass

class IRequest(Interface):
    pass

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

    implements(IRequest)

    _cookies = ()

    def __init__(self, **kw):
        super(RequestStub, self).__init__()
        self.update(kw)
        self.response = self

    def setCookie(self, name, value, **kw):
        self._cookies += (name, value, kw)

    def getPresentationType(self):
        return IUnitTestPresentation

    def getPresentationSkin(self):
        return ''

class TestContainerView(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from z3checkins.message import MessageContainerAdapter
        getService(None, servicenames.Adapters).register(
                [None], IMessageArchive, "", MessageContainerAdapter)

    def test_checkins(self):
        from z3checkins.message import ContainerView
        view = ContainerView()
        view.context = {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                        'a': MessageStub(date=2), 'c': MessageStub(date=3)}
        view.request = {}
        res = view.checkins()
        self.assertEquals(len(res), 3)
        self.assertEquals(view.count(), 3)
        self.assertEquals(res[0].date, 3)
        self.assertEquals(res[1].date, 2)
        self.assertEquals(res[2].date, 1)

    def test_checkins_limited(self):
        from z3checkins.message import ContainerView
        view = ContainerView()
        view.context = {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                        'a': MessageStub(date=2), 'c': MessageStub(date=3)}
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
        from z3checkins.message import ContainerView
        view = ContainerView()
        view.context = {'x': 123, 'y': object(), 'z': MessageStub(date=1),
                        'a': MessageStub(date=2), 'c': MessageStub(date=4)}
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
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
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
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {}
        view.request = RequestStub()
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_empty_bookmarks(self):
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))}
        view.request = RequestStub()
        view.placeBookmark()
        self.assertEquals(view.request._cookies,
                          ('bookmarks', '2003-01-04T21:33:04-05:00',
                           {'max_age': 31536000}))

    def test_placeBookmark_not_at_start(self):
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))}
        view.request = RequestStub(start=1)
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_no_new_checkins(self):
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))}
        view.request = RequestStub(bookmarks='2003-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-02-02T02:02:02+02:00')
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60)))}
        view.request = RequestStub(bookmarks='2004-01-04T21:33:04-05:00 '
                                             'errors are ignored '
                                             '2002-02-02T02:02:02+02:00')
        view.placeBookmark()
        self.assertEquals(view.request._cookies, ())

    def test_placeBookmark_new_checkins(self):
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60))),
                        'w': MessageStub(date=datetime(2003, 1, 6, 22, 33, 44,
                                                tzinfo=FixedTimezone(+3*60)))}
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
        from z3checkins.message import ContainerView
        from z3checkins.message import FixedTimezone
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=datetime(2003, 1, 4, 21, 33, 4,
                                                tzinfo=FixedTimezone(-5*60))),
                        'w': MessageStub(date=datetime(2003, 1, 6, 22, 33, 44,
                                                tzinfo=FixedTimezone(+3*60)))}
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
        from z3checkins.message import ContainerView
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=1, log_message='xxx'),
                        'a': MessageStub(date=2, log_message='xxx'),
                        'c': MessageStub(date=3, log_message='yyy')}
        view.request = RequestStub()
        view.index = view
        getService(None, servicenames.Presentation).provideView(
                ICheckinMessage, 'html', IRequest, MessageTestView)

        res = view.renderCheckins()
        self.assertEquals(res, 'msg3\nmsg2\nmsg1*\n')
        res = view.renderCheckins(start=1, size=1)
        self.assertEquals(res, 'msg2\n')

    def test_renderCheckins_with_bookmarks(self):
        from z3checkins.message import ContainerView
        view = ContainerView()
        view.context = {'x': 123, 'y': object(),
                        'z': MessageStub(date=1, log_message='xxx'),
                        'a': MessageStub(date=2, log_message='xxx'),
                        'c': MessageStub(date=3, log_message='yyy')}
        view.request = RequestStub()
        view.index = view
        view.bookmarks = lambda: [1]
        getService(None, servicenames.Presentation).provideView(
                ICheckinMessage, 'html', IRequest, MessageTestView)
        getService(None, servicenames.Presentation).provideView(
                IBookmark, 'html', IRequest, BookmarkTestView)

        res = view.renderCheckins()
        self.assertEquals(res, 'msg3\nmsg2\n-\nmsg1*\n')


def diff(a, b):
    "Compare the differences of two sequences of strings"

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

class TestCheckinMessageView(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from z3checkins.message import MessageContainerAdapter
        getService(None, servicenames.Adapters).register(
                [None], IMessageArchive, "", MessageContainerAdapter)

    def test_body_strange(self):
        from z3checkins.message import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub(body="Something & strange")
        self.assertEquals(view.body(), "<pre>Something &amp; strange</pre>")

    def test_body(self):
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
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
        from z3checkins.message import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub()
        self.assertEquals(view.first(), None)
        self.assertEquals(view.last(), None)
        self.assertEquals(view.next(), None)
        self.assertEquals(view.previous(), None)

    def test_navigation_empty_archive(self):
        from z3checkins.message import CheckinMessageView
        view = CheckinMessageView()
        view.context = MessageStub()
        view.context.__parent__ = {'1': 2}
        self.assertEquals(view.first(), None)
        self.assertEquals(view.last(), None)
        self.assertEquals(view.next(), None)
        self.assertEquals(view.previous(), None)

    def test_navigation(self):
        from z3checkins.message import CheckinMessageView
        m1 = MessageStub(date=1, message_id='1')
        m2 = MessageStub(date=2, message_id='2')
        m3 = MessageStub(date=3, message_id='3')
        m4 = MessageStub(date=4, message_id='4')

        folder = {'1': 2, '3': 'abc', '4': m1, '5': m2, '6': m3, '7': m4}
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


class TestMessageNameChooser(unittest.TestCase):

    def test_chooseName(self):
        from z3checkins.folder import MessageNameChooser
        msg = MessageStub(message_id="msg@id")
        chooser = MessageNameChooser(None)
        self.assertEquals(chooser.chooseName(None, msg), msg.message_id)
        msg2 = MessageStub(message_id="foo@bar")
        self.assertEquals(chooser.chooseName(None, msg2), msg2.message_id)

    def test_checkName(self):
        from z3checkins.folder import MessageNameChooser
        msg = MessageStub(message_id="msg@id")
        chooser = MessageNameChooser(None)
        self.assertEquals(chooser.checkName("msg@id", msg), True)


class TestMessageSized(unittest.TestCase):

    def test_interface(self):
        from z3checkins.folder import MessageSized
        from zope.app.size.interfaces import ISized
        self.assert_(ISized.providedBy(MessageSized(MessageStub())))

    def test_sizeForSorting(self):
        from z3checkins.folder import MessageSized
        msg = MessageStub()
        sized = MessageSized(msg)
        msg.full_text = '*' * 42;
        self.assertEquals(sized.sizeForSorting(), 42)
        msg.full_text = '*' * 32768;
        self.assertEquals(sized.sizeForSorting(), 32768)

    def test_sizeForDisplay(self):
        from z3checkins.folder import MessageSized
        msg = MessageStub()
        sized = MessageSized(msg)
        msg.full_text = '*' * 42;
        self.assertEquals(sized.sizeForDisplay(), u"42 bytes")
        msg.full_text = '*' * 32767;
        self.assertEquals(sized.sizeForDisplay(), u"31 KB")
        msg.full_text = '*' * 32768;
        self.assertEquals(sized.sizeForDisplay(), u"32 KB")


def open_test_data(filename):
    """Open a file relative to the location of this module."""
    base = os.path.dirname(__file__)
    return open(os.path.join(base, filename))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFixedTimezone))
    suite.addTest(unittest.makeSuite(TestRFCDateTimeFormatter))
    suite.addTest(unittest.makeSuite(TestISODateTimeFormatter))
    suite.addTest(unittest.makeSuite(TestCheckinMessage))
    suite.addTest(unittest.makeSuite(TestCheckinMessageParser))
    suite.addTest(unittest.makeSuite(TestMessageContainerAdapter))
    suite.addTest(unittest.makeSuite(TestMessageUpload))
    suite.addTest(unittest.makeSuite(TestContainerView))
    suite.addTest(unittest.makeSuite(TestCheckinMessageView))
    suite.addTest(unittest.makeSuite(TestMessageNameChooser))
    suite.addTest(unittest.makeSuite(TestMessageSized))
    return suite


if __name__ == "__main__":
    unittest.main()
