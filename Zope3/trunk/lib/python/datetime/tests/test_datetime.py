"""Test date/time type.

See http://www.zope.org/Members/fdrake/DateTimeWiki/TestCases
"""

import sys
import unittest

from datetime import date, time, timetz, datetime, datetimetz, timedelta
from datetime import MINYEAR, MAXYEAR


class TestDate(unittest.TestCase):

    theclass = date

    # All the other tests here have been moved into test_both.  This one
    # relies on stuff only the Python version implements.
    def test_ordinal_conversions(self):
        from datetime import _ymd2ord, _ord2ymd

        # Check some fixed values.
        for y, m, d, n in [(1, 1, 1, 1),      # calendar origin
                           (0, 12, 31, 0),
                           (0, 12, 30, -1),
                           # first example from "Calendrical Calculations"
                           (1945, 11, 12, 710347)]:
            self.assertEqual(n, _ymd2ord(y, m, d))
            self.assertEqual((y, m, d), _ord2ymd(n))

        # Check first and last days of year exhaustively across 2000 years
        # centered at the origin, and spottily over the whole range of
        # years datetime objects support.
        for year in range(-1001, 1002) + range(MINYEAR, MAXYEAR+1, 7):
            # Verify (year, 1, 1) -> ordinal -> y, m, d is identity.
            n = _ymd2ord(year, 1, 1)
            self.assertEqual((year, 1, 1), _ord2ymd(n))
            # Verify that moving back a day gets to the end of year-1.
            self.assertEqual((year-1, 12, 31), _ord2ymd(n-1))
            self.assertEqual(_ymd2ord(year-1, 12, 31), n-1)

        # Test every day in a leap-year and a non-leap year.
        dim = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        for year, isleap in (2000, 1), (2002, 0):
            n = _ymd2ord(year, 1, 1)
            for month, maxday in zip(range(1, 13), dim):
                if month == 2 and isleap:
                    maxday += 1
                for day in range(1, maxday+1):
                    self.assertEqual((year, month, day), _ord2ymd(n))
                    self.assertEqual(n, _ymd2ord(year, month, day))
                    n += 1


class TestTime(unittest.TestCase):

    theclass = time

    def test_basic_attributes(self):
        t = self.theclass(12, 0)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)
        self.assertEqual(t.microsecond, 0)

    def test_basic_attributes_nonzero(self):
        # Make sure all attributes are non-zero so bugs in
        # bit-shifting access show up.
        t = self.theclass(12, 59, 59, 8000)
        self.assertEqual(t.hour, 12)
        self.assertEqual(t.minute, 59)
        self.assertEqual(t.second, 59)
        self.assertEqual(t.microsecond, 8000)

    def test_roundtrip(self):
        for t in (self.theclass(1, 2, 3, 4),):
            # Verify t -> string -> time identity.
            s = repr(t)
            t2 = eval(s)
            self.assertEqual(t, t2)

            # Verify identity via reconstructing from pieces.
            t2 = self.theclass(t.hour, t.minute, t.second,
                               t.microsecond)
            self.assertEqual(t, t2)

    def test_comparing(self):
        t1 = self.theclass(9, 0, 0)
        t2 = self.theclass(10, 0, 0)
        t3 = self.theclass(9, 0, 0)
        self.assertEqual(t1, t3)
        self.assert_(t2 > t3)

    def test_bad_constructor_arguments(self):
        # bad hours
        self.theclass(0, 0)    # no exception
        self.theclass(23, 0)   # no exception
        self.assertRaises(ValueError, self.theclass, -1, 0)
        self.assertRaises(ValueError, self.theclass, 24, 0)
        # bad minutes
        self.theclass(23, 0)    # no exception
        self.theclass(23, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, -1)
        self.assertRaises(ValueError, self.theclass, 23, 60)
        # bad seconds
        self.theclass(23, 59, 0)    # no exception
        self.theclass(23, 59, 59)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 60)
        # bad microseconds
        self.theclass(23, 59, 59, 0)        # no exception
        self.theclass(23, 59, 59, 999999)   # no exception
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, -1)
        self.assertRaises(ValueError, self.theclass, 23, 59, 59, 1000000)

    def test_hash_equality(self):
        d = self.theclass(23, 30, 17)
        e = self.theclass(23, 30, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

        d = self.theclass(0,  5, 17)
        e = self.theclass(0,  5, 17)
        self.assertEqual(d, e)
        self.assertEqual(hash(d), hash(e))

        dic = {d: 1}
        dic[e] = 2
        self.assertEqual(len(dic), 1)
        self.assertEqual(dic[d], 2)
        self.assertEqual(dic[e], 2)

    def test_isoformat(self):
        t = self.theclass(4, 5, 1, 123)
        self.assertEqual(t.isoformat(), "04:05:01.000123")

    def test_strftime(self):
        t = self.theclass(1, 2, 3, 4)
        self.assertEqual(t.strftime('%H %M %S'), "01 02 03")

    def test_str(self):
        self.assertEqual(str(self.theclass(1, 2, 3, 4)), "1:02:03.000004")
        self.assertEqual(str(self.theclass(10, 2, 3, 4000)), "10:02:03.004")
        self.assertEqual(str(self.theclass(0, 2, 3, 400000)), "0:02:03.4")
        self.assertEqual(str(self.theclass(12, 2, 3, 0)), "12:02:03")
        self.assertEqual(str(self.theclass(23, 15, 0, 0)), "23:15")

    def test_repr(self):
        self.assertEqual(repr(self.theclass(1, 2, 3, 4)),
                         "%s(1, 2, 3, 4)" % self.theclass.__name__)
        self.assertEqual(repr(self.theclass(10, 2, 3, 4000)),
                         "%s(10, 2, 3, 4000)" % self.theclass.__name__)
        self.assertEqual(repr(self.theclass(0, 2, 3, 400000)),
                         "%s(0, 2, 3, 400000)" % self.theclass.__name__)
        self.assertEqual(repr(self.theclass(12, 2, 3, 0)),
                         "%s(12, 2, 3)" % self.theclass.__name__)
        self.assertEqual(repr(self.theclass(23, 15, 0, 0)),
                         "%s(23, 15)" % self.theclass.__name__)

    def test_resolution_info(self):
        self.assert_(isinstance(self.theclass.min, self.theclass))
        self.assert_(isinstance(self.theclass.max, self.theclass))
        self.assert_(isinstance(self.theclass.resolution, timedelta))
        self.assert_(self.theclass.max > self.theclass.min)


class TestTimeTZ(TestTime):

    theclass = timetz

    def test_zones(self):
        est = FixedOffset(-300, "EST")
        utc = FixedOffset(0, "UTC")
        met = FixedOffset(60, "MET")
        t1 = timetz( 7, 47, tzinfo=est)
        t2 = timetz(12, 47, tzinfo=utc)
        t3 = timetz(13, 47, tzinfo=met)
        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertEqual(t1.utcoffset(), -300)
        self.assertEqual(t2.utcoffset(), 0)
        self.assertEqual(t3.utcoffset(), 60)
        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))
        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertEqual(str(t1), "7:47 -05:00")
        self.assertEqual(str(t2), "12:47 +00:00")
        self.assertEqual(str(t3), "13:47 +01:00")
        self.assertEqual(repr(t1), "timetz(7, 47, tzinfo=est)")
        self.assertEqual(repr(t2), "timetz(12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3), "timetz(13, 47, tzinfo=met)")
        self.assertEqual(t1.isoformat(), "07:47:00.000000-05:00")
        self.assertEqual(t2.isoformat(), "12:47:00.000000+00:00")
        self.assertEqual(t3.isoformat(), "13:47:00.000000+01:00")
        self.assertEqual(t1.strftime("%H:%M:%S %Z %z"), "07:47:00 EST -0500")
        self.assertEqual(t2.strftime("%H:%M:%S %Z %z"), "12:47:00 UTC +0000")
        self.assertEqual(t3.strftime("%H:%M:%S %Z %z"), "13:47:00 MET +0100")


class TestDateTime(TestDate):

    theclass = datetime

    def test_tmxxx(self):
        from datetime import tmxxx
        for timestamp in 123456789.0, 987654321.0:
            dt = self.theclass.utcfromtimestamp(timestamp)
            # Mangles the fields, but in such a way that normalization should
            # restore them to dt's values.
            tm = tmxxx(dt.year - 1, dt.month + 12, dt.day + 100,
                       dt.hour - 24*100, dt.minute - 3, dt.second + 12,
                       (3*60 - 12) * 1000000)
            dt2 = self.theclass(tm.year, tm.month, tm.day, tm.hour, tm.minute,
                                tm.second, tm.microsecond)
            self.assertEqual(dt, dt2)
            self.assertEqual(timestamp, tm.time())

    def test_combine(self):
        d = date(2002, 3, 4)
        t = time(18, 45, 3, 1234)
        dt = datetime.combine(d, t)
        self.assertEqual(dt, datetime(2002, 3, 4, 18, 45, 3, 1234))

    def test_extract(self):
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))


class FixedOffset(object):
    def __init__(self, offset, name):
        self.__offset = offset
        self.__name = name
    def __repr__(self):
        return self.__name.lower()
    def utcoffset(self, dt):
        return self.__offset
    def tzname(self, dt):
        return self.__name
    def dst(self, dt):
        return 0


class TestDateTimeTZ(TestDateTime):

    theclass = datetimetz

    def test_zones(self):
        est = FixedOffset(-300, "EST")
        utc = FixedOffset(0, "UTC")
        met = FixedOffset(60, "MET")
        t1 = datetimetz(2002, 3, 19,  7, 47, tzinfo=est)
        t2 = datetimetz(2002, 3, 19, 12, 47, tzinfo=utc)
        t3 = datetimetz(2002, 3, 19, 13, 47, tzinfo=met)
        self.assertEqual(t1.tzinfo, est)
        self.assertEqual(t2.tzinfo, utc)
        self.assertEqual(t3.tzinfo, met)
        self.assertEqual(t1.utcoffset(), -300)
        self.assertEqual(t2.utcoffset(), 0)
        self.assertEqual(t3.utcoffset(), 60)
        self.assertEqual(t1.tzname(), "EST")
        self.assertEqual(t2.tzname(), "UTC")
        self.assertEqual(t3.tzname(), "MET")
        self.assertEqual(hash(t1), hash(t2))
        self.assertEqual(hash(t1), hash(t3))
        self.assertEqual(hash(t2), hash(t3))
        self.assertEqual(t1, t2)
        self.assertEqual(t1, t3)
        self.assertEqual(t2, t3)
        self.assertEqual(str(t1), "2002-03-19 07:47:00.000000-05:00")
        self.assertEqual(str(t2), "2002-03-19 12:47:00.000000+00:00")
        self.assertEqual(str(t3), "2002-03-19 13:47:00.000000+01:00")
        self.assertEqual(repr(t1),
                         "datetimetz(2002, 3, 19, 7, 47, tzinfo=est)")
        self.assertEqual(repr(t2),
                         "datetimetz(2002, 3, 19, 12, 47, tzinfo=utc)")
        self.assertEqual(repr(t3),
                         "datetimetz(2002, 3, 19, 13, 47, tzinfo=met)")

    def test_combine(self):
        met = FixedOffset(60, "MET")
        d = date(2002, 3, 4)
        tz = timetz(18, 45, 3, 1234, tzinfo=met)
        dt = datetimetz.combine(d, tz)
        self.assertEqual(dt, datetimetz(2002, 3, 4, 18, 45, 3, 1234,
                                        tzinfo=met))

    def test_extract(self):
        met = FixedOffset(60, "MET")
        dt = self.theclass(2002, 3, 4, 18, 45, 3, 1234, tzinfo=met)
        self.assertEqual(dt.date(), date(2002, 3, 4))
        self.assertEqual(dt.time(), time(18, 45, 3, 1234))
        self.assertEqual(dt.timetz(), timetz(18, 45, 3, 1234, tzinfo=met))


def test_suite():
    s2 = unittest.makeSuite(TestDate, 'test')
    s3 = unittest.makeSuite(TestTime, 'test')
    s4 = unittest.makeSuite(TestTimeTZ, 'test')
    s5 = unittest.makeSuite(TestDateTime, 'test')
    s6 = unittest.makeSuite(TestDateTimeTZ, 'test')
    return unittest.TestSuite([s2, s3, s4, s5, s6])

def test_main():
    r = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    s = test_suite()
    r.run(s)

if __name__ == "__main__":
    test_main()
