##############################################################################
#
# Copyright (c) 2002-2004 Zope Corporation and Contributors.
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
"""PostgreSQL Database Adapter for Zope 3

$Id$
"""
from zope.app.rdb import ZopeDatabaseAdapter, parseDSN

from datetime import date, time, datetime, timedelta
import psycopg
import re

PG_ENCODING = 'utf8'

# These OIDs are taken from include/server/pg_type.h from PostgreSQL headers.
# Unfortunatelly psycopg does not export them as constants, and
# we cannot use psycopg.FOO.values because they overlap.
DATE_OID        = 1082
TIME_OID        = 1083
TIMETZ_OID      = 1266
TIMESTAMP_OID   = 1114
TIMESTAMPTZ_OID = 1184
INTERVAL_OID    = 1186

CHAR_OID = 18
TEXT_OID = 25
BPCHAR_OID = 1042
VARCHAR_OID = 1043

# The following ones are obsolete and we don't handle them
#ABSTIME_OID     = 702
#RELTIME_OID     = 703
#TINTERVAL_OID   = 704

# Date/time parsing functions

_dateFmt = re.compile(r"^(\d\d\d\d)-?([01]\d)-?([0-3]\d)$")

def parse_date(s):
    """Parses ISO-8601 compliant dates and returns a tuple (year, month,
    day).

    The following formats are accepted:
        YYYY-MM-DD  (extended format)
        YYYYMMDD    (basic format)
    """
    m = _dateFmt.match(s)
    if m is None:
        raise ValueError, 'invalid date string: %s' % s
    year, month, day = m.groups()
    return int(year), int(month), int(day)


_timeFmt = re.compile(
    r"^([0-2]\d)(?::?([0-5]\d)(?::?([0-5]\d)(?:[.,](\d+))?)?)?$")

def parse_time(s):
    """Parses ISO-8601 compliant times and returns a tuple (hour, minute,
    second).

    The following formats are accepted:
        HH:MM:SS.ssss or HHMMSS.ssss
        HH:MM:SS,ssss or HHMMSS,ssss
        HH:MM:SS      or HHMMSS
        HH:MM         or HHMM
        HH
    """
    m = _timeFmt.match(s)
    if m is None:
        raise ValueError, 'invalid time string: %s' % s
    hr, mn, sc, msc = m.groups(0)
    if msc != 0:
        sc = float("%s.%s" % (sc, msc))
    else:
        sc = int(sc)
    return int(hr), int(mn), sc


_tzFmt = re.compile(r"^([+-])([0-2]\d)(?::?([0-5]\d))?$")

def parse_tz(s):
    """Parses ISO-8601 timezones and returns the offset east of UTC in
    minutes.

    The following formats are accepted:
        +/-HH:MM
        +/-HHMM
        +/-HH
        Z           (equivalent to +0000)
    """
    if s == 'Z':
        return 0
    m = _tzFmt.match(s)
    if m is None:
        raise ValueError, 'invalid time zone: %s' % s
    d, hoff, moff = m.groups(0)
    if d == "-":
        return - int(hoff) * 60 - int(moff)
    return int(hoff) * 60 + int(moff)


_tzPos = re.compile(r"[Z+-]")

def parse_timetz(s):
    """Parses ISO-8601 compliant times that may include timezone information
    and returns a tuple (hour, minute, second, tzoffset).

    tzoffset is the offset east of UTC in minutes.  It will be None if s does
    not include time zone information.

    Formats accepted are those listed in the descriptions of parse_time() and
    parse_tz().  Time zone should immediatelly follow time without intervening
    spaces.
    """
    m = _tzPos.search(s)
    if m is None:
        return parse_time(s) + (None,)
    pos = m.start()
    return parse_time(s[:pos]) + (parse_tz(s[pos:]),)


_datetimeFmt = re.compile(r"[T ]")

def _split_datetime(s):
    """Split date and time parts of ISO-8601 compliant timestamp and
    return a tuple (date, time).

    ' ' or 'T' used to separate date and time parts.
    """
    m = _datetimeFmt.search(s)
    if m is None:
        raise ValueError, 'time part of datetime missing: %s' % s
    pos = m.start()
    return s[:pos], s[pos + 1:]


def parse_datetime(s):
    """Parses ISO-8601 compliant timestamp and returns a tuple (year, month,
    day, hour, minute, second).

    Formats accepted are those listed in the descriptions of parse_date() and
    parse_time() with ' ' or 'T' used to separate date and time parts.
    """
    dt, tm = _split_datetime(s)
    return parse_date(dt) + parse_time(tm)


def parse_datetimetz(s):
    """Parses ISO-8601 compliant timestamp that may include timezone
    information and returns a tuple (year, month, day, hour, minute, second,
    tzoffset).

    tzoffset is the offset east of UTC in minutes.  It will be None if s does
    not include time zone information.

    Formats accepted are those listed in the descriptions of parse_date() and
    parse_timetz() with ' ' or 'T' used to separate date and time parts.
    """
    dt, tm = _split_datetime(s)
    return parse_date(dt) + parse_timetz(tm)


def parse_interval(s):
    """Parses PostgreSQL interval notation and returns a tuple (years, months,
    days, hours, minutes, seconds).

    Values accepted:
        interval  ::= date
                   |  time
                   |  date time
        date      ::= date_comp
                   |  date date_comp
        date_comp ::= 1 'day'
                   |  number 'days'
                   |  1 'month'
                   |  number 'months'
                   |  1 'year'
                   |  number 'years'
        time      ::= number ':' number
                   |  number ':' number ':' number
                   |  number ':' number ':' number '.' fraction
    """
    years = months = days = 0
    hours = minutes = seconds = 0
    elements = s.split()
    for i in range(0, len(elements) - 1, 2):
        count, unit = elements[i:i+2]
        if unit == 'day' and count == '1':
            days += 1
        elif unit == 'days':
            days += int(count)
        elif unit == 'month' and count == '1':
            months += 1
        elif unit == 'months':
            months += int(count)
        elif unit == 'year' and count == '1':
            years += 1
        elif unit == 'years':
            years += int(count)
        else:
            raise ValueError, 'unknown time interval %s %s' % (count, unit)
    if len(elements) % 2 == 1:
        hours, minutes, seconds = parse_time(elements[-1])
    return (years, months, days, hours, minutes, seconds)


# Type conversions
def _conv_date(s):
    if s:
        return date(*parse_date(s))

def _conv_time(s):
    if s:
        hr, mn, sc = parse_time(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        return time(hr, mn, int(sc), int(micro))

def _conv_timetz(s):
    if s:
        from zope.app.datetimeutils import tzinfo
        hr, mn, sc, tz = parse_timetz(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        if tz: tz = tzinfo(tz)
        return time(hr, mn, int(sc), int(micro), tz)

def _conv_timestamp(s):
    if s:
        y, m, d, hr, mn, sc = parse_datetime(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        return datetime(y, m, d, hr, mn, int(sc), int(micro))

def _conv_timestamptz(s):
    if s:
        from zope.app.datetimeutils import tzinfo
        y, m, d, hr, mn, sc, tz = parse_datetimetz(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        if tz: tz = tzinfo(tz)
        return datetime(y, m, d, hr, mn, int(sc), int(micro), tz)

def _conv_interval(s):
    if s:
        y, m, d, hr, mn, sc = parse_interval(s)
        if (y, m) != (0, 0):
            # XXX: Currently there's no way to represent years and months as
            # timedeltas
            return s
        else:
            return timedelta(days=d, hours=hr, minutes=mn, seconds=sc)


def _conv_string(str):
    return str.decode(PG_ENCODING)

# User-defined types
DATE = psycopg.new_type((DATE_OID,), "ZDATE", _conv_date)
TIME = psycopg.new_type((TIME_OID,), "ZTIME", _conv_time)
TIMETZ = psycopg.new_type((TIMETZ_OID,), "ZTIMETZ", _conv_timetz)
TIMESTAMP = psycopg.new_type((TIMESTAMP_OID,), "ZTIMESTAMP", _conv_timestamp)
TIMESTAMPTZ = psycopg.new_type((TIMESTAMPTZ_OID,), "ZTIMESTAMPTZ",
                                _conv_timestamptz)
INTERVAL = psycopg.new_type((INTERVAL_OID,), "ZINTERVAL", _conv_interval)

STRING = psycopg.new_type((CHAR_OID, TEXT_OID, BPCHAR_OID, VARCHAR_OID),
                          "ZSTRING", _conv_string)


dsn2option_mapping = {'host': 'host',
                      'port': 'port',
                      'dbname': 'dbname',
                      'username': 'user',
                      'password': 'password'}


class PsycopgAdapter(ZopeDatabaseAdapter):
    """A PsycoPG adapter for Zope3.

    The following type conversions are performed:

        DATE -> datetime.date
        TIME -> datetime.time
        TIMETZ -> datetime.time
        TIMESTAMP -> datetime.datetime
        TIMESTAMPTZ -> datetime.datetime

    XXX: INTERVAL cannot be represented exactly as datetime.timedelta since
    it might be something like '1 month', which is a variable number of days.
    """

    def _connection_factory(self):
        """Create a Psycopg DBI connection based on the DSN"""
        conn_info = parseDSN(self.dsn)
        conn_list = []
        for dsnname, optname in dsn2option_mapping.iteritems():
            if conn_info[dsnname]:
                conn_list.append('%s=%s' % (optname, conn_info[dsnname]))
        conn_str = ' '.join(conn_list)
        self._registerTypes()
        return psycopg.connect(conn_str)

    def _registerTypes(self):
        """Register type conversions for psycopg"""
        psycopg.register_type(DATE)
        psycopg.register_type(TIME)
        psycopg.register_type(TIMETZ)
        psycopg.register_type(TIMESTAMP)
        psycopg.register_type(TIMESTAMPTZ)
        psycopg.register_type(INTERVAL)
        psycopg.register_type(STRING)
            
