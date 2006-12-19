#!/usr/bin/python
"""
Unit tests for timeutils.py

$Id$
"""

import unittest
import time
from datetime import datetime, timedelta


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
        from z3checkins.timeutils import FixedTimezone, RFCDateTimeFormatter
        for Y, M, D, h, m, s, tz, res in self.times:
            dt = datetime(Y, M, D, h, m, s, tzinfo=FixedTimezone(tz))
            view = RFCDateTimeFormatter(dt, None)
            self.assertEquals(str(view), res)
            self.assertEquals(view(), res)


class TestISODateTimeFormatter(unittest.TestCase):

    times = ((2003, 4, 2, 12, 33, 41, 3*60, "2003-04-02 09:33"),
             (2000, 1, 2, 17, 41, 33, -5*60, "2000-01-02 22:41"))

    def test_usertz(self):
        from z3checkins.timeutils import ISODateTimeFormatter
        t = time.time()
        delta = ISODateTimeFormatter(None, None).userstz._offset * 60
        self.assertEquals(time.gmtime(t)[:8], time.localtime(t - delta)[:8])

    def test_isotime(self):
        from z3checkins.timeutils import FixedTimezone, ISODateTimeFormatter
        for Y, M, D, h, m, s, tz, res in self.times:
            dt = datetime(Y, M, D, h, m, s, tzinfo=FixedTimezone(tz))
            dt -= ISODateTimeFormatter(None, None).userstz.utcoffset(None)
            view = ISODateTimeFormatter(dt, None)
            self.assertEquals(str(view), res)
            self.assertEquals(view(), res)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFixedTimezone))
    suite.addTest(unittest.makeSuite(TestRFCDateTimeFormatter))
    suite.addTest(unittest.makeSuite(TestISODateTimeFormatter))
    return suite


if __name__ == "__main__":
    unittest.main()
