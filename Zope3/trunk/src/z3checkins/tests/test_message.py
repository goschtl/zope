#!/usr/bin/python
"""
Unit tests for message.py

$Id: test_message.py,v 1.26 2004/03/26 22:18:08 gintautasm Exp $
"""

import unittest
import os
import sys
import time
from datetime import datetime

from zope.interface import Interface, implements
from zope.interface.verify import verifyObject
from zope.app.container.contained import Contained

from z3checkins.interfaces import IMessage, IMessageContained
from z3checkins.interfaces import ICheckinMessage, IBookmark, IMessageParser


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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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
        from z3checkins.timeutils import FixedTimezone
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

    def test_parser_svnmsg_zope(self):
        from z3checkins.message import CheckinMessageParser
        from z3checkins.timeutils import FixedTimezone
        # TODO: The Zope 3 checkin mailing list uses a non-standard format.
        # This test checks the compatibility hacks planted in the code.
        # I hope that they will be removed in the future.
        svn_msg4 = open_test_data("svn_msg4.txt")
        svn_msg4_text = svn_msg4.read()
        svn_msg4.seek(0)
        parser = CheckinMessageParser()
        msg = parser.parse(svn_msg4)
        self.assert_(IMessage.providedBy(msg))
        self.assertEquals(msg.message_id,
                          "200405220157.i4M1v7YW001064@cvs.zope.org")
        self.assertEquals(msg.author_name, "Albertas Agejevas")
        self.assertEquals(msg.author_email, "alga@pov.lt")
        self.assertEquals(msg.date, datetime(2004, 5, 21, 21, 57, 07,
                                             tzinfo=FixedTimezone(-4*60)))
        self.assertEquals(msg.subject, "SVN: zope/app/traversing/interfaces.py")
        self.assertEquals(msg.directory, "zope/app/traversing/interfaces.py")
        self.assertEquals(msg.branch, None)
        self.assertEquals(msg.log_message, """Changed a comment.""")
        self.assertEquals(msg.body, svn_msg4_text.split("\n\n", 1)[1])


class MessageStub(Contained):

    implements(ICheckinMessage, IMessageContained)

    full_text = "full text of this message"

    def __init__(self, data=None, date=None, body=None, log_message='',
                       subject='', message_id="message@id"):
        self.data = data
        self.date = date
        self.body = body
        self.subject = subject
        self.log_message = log_message
        self.message_id = message_id


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
    suite.addTest(unittest.makeSuite(TestCheckinMessage))
    suite.addTest(unittest.makeSuite(TestCheckinMessageParser))
    suite.addTest(unittest.makeSuite(TestMessageNameChooser))
    suite.addTest(unittest.makeSuite(TestMessageSized))
    return suite


if __name__ == "__main__":
    unittest.main()
