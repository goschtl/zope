##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Encapsulation of date/time values

$Id: DateTimeParse.py,v 1.5 2002/11/11 16:37:57 stevea Exp $
"""
    
import re, math, DateTimeZone
from types import StringTypes
from time import \
     time as _time, gmtime, localtime, daylight, timezone, altzone
try: from time import tzname
except ImportError: tzname = ('UNKNOWN','UNKNOWN')

class DateTimeError(Exception): "Date-time error"
class DateError(DateTimeError): 'Invalid Date Components'
class TimeError(DateTimeError): 'Invalid Time Components'
class SyntaxError(DateTimeError): 'Invalid Date-Time String'

# Determine machine epoch
tm=((0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334),
    (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
yr,mo,dy,hr,mn,sc=gmtime(0)[:6]
i=int(yr-1)
to_year =int(i*365+i/4-i/100+i/400-693960.0)
to_month=tm[yr%4==0 and (yr%100!=0 or yr%400==0)][mo]
EPOCH  =(to_year+to_month+dy+(hr/24.0+mn/1440.0+sc/86400.0))*86400
jd1901 =2415385L


numericTimeZoneMatch=re.compile(r'[+-][0-9][0-9][0-9][0-9]').match #TS

class _timezone:
    def __init__(self,data):
        self.name,self.timect,self.typect, \
        self.ttrans,self.tindex,self.tinfo,self.az=data

    def default_index(self):
        if self.timect == 0: return 0
        for i in range(self.typect):
            if self.tinfo[i][1] == 0: return i
        return 0

    def index(self,t=None):
        t=t or _time()
        if self.timect==0: idx=(0, 0, 0)
        elif t < self.ttrans[0]:
            i=self.default_index()
            idx=(i, ord(self.tindex[0]),i)
        elif t >= self.ttrans[-1]:
            if self.timect > 1:
                idx=(ord(self.tindex[-1]),ord(self.tindex[-1]),
                     ord(self.tindex[-2]))
            else:
                idx=(ord(self.tindex[-1]),ord(self.tindex[-1]),
                     self.default_index())
        else:
            for i in range(self.timect-1):
                if t < self.ttrans[i+1]:
                    if i==0: idx=(ord(self.tindex[0]),ord(self.tindex[1]),
                                  self.default_index())
                    else:    idx=(ord(self.tindex[i]),ord(self.tindex[i+1]),
                                  ord(self.tindex[i-1]))
                    break
        return idx

    def info(self,t=None):
        idx=self.index(t)[0]
        zs =self.az[self.tinfo[idx][2]:]
        return self.tinfo[idx][0],self.tinfo[idx][1],zs[: zs.find('\000')]




class _cache:

    _zlst=['Brazil/Acre','Brazil/DeNoronha','Brazil/East',
           'Brazil/West','Canada/Atlantic','Canada/Central',
           'Canada/Eastern','Canada/East-Saskatchewan',
           'Canada/Mountain','Canada/Newfoundland',
           'Canada/Pacific','Canada/Yukon',
           'Chile/Continental','Chile/EasterIsland','CST','Cuba',
           'Egypt','EST','GB-Eire','Greenwich','Hongkong','Iceland',
           'Iran','Israel','Jamaica','Japan','Mexico/BajaNorte',
           'Mexico/BajaSur','Mexico/General','MST','Poland','PST',
           'Singapore','Turkey','Universal','US/Alaska','US/Aleutian',
           'US/Arizona','US/Central','US/Eastern','US/East-Indiana',
           'US/Hawaii','US/Indiana-Starke','US/Michigan',
           'US/Mountain','US/Pacific','US/Samoa','UTC','UCT','GMT',

           'GMT+0100','GMT+0200','GMT+0300','GMT+0400','GMT+0500',
           'GMT+0600','GMT+0700','GMT+0800','GMT+0900','GMT+1000',
           'GMT+1100','GMT+1200','GMT+1300','GMT-0100','GMT-0200',
           'GMT-0300','GMT-0400','GMT-0500','GMT-0600','GMT-0700',
           'GMT-0800','GMT-0900','GMT-1000','GMT-1100','GMT-1200',
           'GMT+1',

           'GMT+0130', 'GMT+0230', 'GMT+0330', 'GMT+0430', 'GMT+0530',
           'GMT+0630', 'GMT+0730', 'GMT+0830', 'GMT+0930', 'GMT+1030',
           'GMT+1130', 'GMT+1230',

           'GMT-0130', 'GMT-0230', 'GMT-0330', 'GMT-0430', 'GMT-0530',
           'GMT-0630', 'GMT-0730', 'GMT-0830', 'GMT-0930', 'GMT-1030',
           'GMT-1130', 'GMT-1230',

           'UT','BST','MEST','SST','FST','WADT','EADT','NZDT',
           'WET','WAT','AT','AST','NT','IDLW','CET','MET',
           'MEWT','SWT','FWT','EET','EEST','BT','ZP4','ZP5','ZP6',
           'WAST','CCT','JST','EAST','GST','NZT','NZST','IDLE']


    _zmap={'aest':'GMT+1000', 'aedt':'GMT+1100',
           'aus eastern standard time':'GMT+1000',
           'sydney standard time':'GMT+1000',
           'tasmania standard time':'GMT+1000',
           'e. australia standard time':'GMT+1000',
           'aus central standard time':'GMT+0930',
           'cen. australia standard time':'GMT+0930',
           'w. australia standard time':'GMT+0800',

           'brazil/acre':'Brazil/Acre',
           'brazil/denoronha':'Brazil/Denoronha',
           'brazil/east':'Brazil/East','brazil/west':'Brazil/West',
           'canada/atlantic':'Canada/Atlantic',
           'canada/central':'Canada/Central',
           'canada/eastern':'Canada/Eastern',
           'canada/east-saskatchewan':'Canada/East-Saskatchewan',
           'canada/mountain':'Canada/Mountain',
           'canada/newfoundland':'Canada/Newfoundland',
           'canada/pacific':'Canada/Pacific','canada/yukon':'Canada/Yukon',
           'central europe standard time':'GMT+0100',
           'chile/continental':'Chile/Continental',
           'chile/easterisland':'Chile/EasterIsland',
           'cst':'US/Central','cuba':'Cuba','est':'US/Eastern','egypt':'Egypt',
           'eastern standard time':'US/Eastern',
           'us eastern standard time':'US/Eastern',
           'central standard time':'US/Central',
           'mountain standard time':'US/Mountain',
           'pacific standard time':'US/Pacific',
           'gb-eire':'GB-Eire','gmt':'GMT',

           'gmt+0000':'GMT+0', 'gmt+0':'GMT+0',


           'gmt+0100':'GMT+1', 'gmt+0200':'GMT+2', 'gmt+0300':'GMT+3',
           'gmt+0400':'GMT+4', 'gmt+0500':'GMT+5', 'gmt+0600':'GMT+6',
           'gmt+0700':'GMT+7', 'gmt+0800':'GMT+8', 'gmt+0900':'GMT+9',
           'gmt+1000':'GMT+10','gmt+1100':'GMT+11','gmt+1200':'GMT+12',
           'gmt+1300':'GMT+13',
           'gmt-0100':'GMT-1', 'gmt-0200':'GMT-2', 'gmt-0300':'GMT-3',
           'gmt-0400':'GMT-4', 'gmt-0500':'GMT-5', 'gmt-0600':'GMT-6',
           'gmt-0700':'GMT-7', 'gmt-0800':'GMT-8', 'gmt-0900':'GMT-9',
           'gmt-1000':'GMT-10','gmt-1100':'GMT-11','gmt-1200':'GMT-12',

           'gmt+1': 'GMT+1', 'gmt+2': 'GMT+2', 'gmt+3': 'GMT+3',
           'gmt+4': 'GMT+4', 'gmt+5': 'GMT+5', 'gmt+6': 'GMT+6',
           'gmt+7': 'GMT+7', 'gmt+8': 'GMT+8', 'gmt+9': 'GMT+9',
           'gmt+10':'GMT+10','gmt+11':'GMT+11','gmt+12':'GMT+12',
           'gmt+13':'GMT+13',
           'gmt-1': 'GMT-1', 'gmt-2': 'GMT-2', 'gmt-3': 'GMT-3',
           'gmt-4': 'GMT-4', 'gmt-5': 'GMT-5', 'gmt-6': 'GMT-6',
           'gmt-7': 'GMT-7', 'gmt-8': 'GMT-8', 'gmt-9': 'GMT-9',
           'gmt-10':'GMT-10','gmt-11':'GMT-11','gmt-12':'GMT-12',

           'gmt+130':'GMT+0130',  'gmt+0130':'GMT+0130',
           'gmt+230':'GMT+0230',  'gmt+0230':'GMT+0230',
           'gmt+330':'GMT+0330',  'gmt+0330':'GMT+0330',
           'gmt+430':'GMT+0430',  'gmt+0430':'GMT+0430',           
           'gmt+530':'GMT+0530',  'gmt+0530':'GMT+0530',
           'gmt+630':'GMT+0630',  'gmt+0630':'GMT+0630',
           'gmt+730':'GMT+0730',  'gmt+0730':'GMT+0730',
           'gmt+830':'GMT+0830',  'gmt+0830':'GMT+0830',           
           'gmt+930':'GMT+0930',  'gmt+0930':'GMT+0930',
           'gmt+1030':'GMT+1030',
           'gmt+1130':'GMT+1130',
           'gmt+1230':'GMT+1230',      

           'gmt-130':'GMT-0130',  'gmt-0130':'GMT-0130',
           'gmt-230':'GMT-0230',  'gmt-0230':'GMT-0230',
           'gmt-330':'GMT-0330',  'gmt-0330':'GMT-0330',
           'gmt-430':'GMT-0430',  'gmt-0430':'GMT-0430',           
           'gmt-530':'GMT-0530',  'gmt-0530':'GMT-0530',
           'gmt-630':'GMT-0630',  'gmt-0630':'GMT-0630',
           'gmt-730':'GMT-0730',  'gmt-0730':'GMT-0730',
           'gmt-830':'GMT-0830',  'gmt-0830':'GMT-0830',           
           'gmt-930':'GMT-0930',  'gmt-0930':'GMT-0930',
           'gmt-1030':'GMT-1030',
           'gmt-1130':'GMT-1130',
           'gmt-1230':'GMT-1230',

           'greenwich':'Greenwich','hongkong':'Hongkong',
           'iceland':'Iceland','iran':'Iran','israel':'Israel',
           'jamaica':'Jamaica','japan':'Japan',
           'mexico/bajanorte':'Mexico/BajaNorte',
           'mexico/bajasur':'Mexico/BajaSur','mexico/general':'Mexico/General',
           'mst':'US/Mountain','pst':'US/Pacific','poland':'Poland',
           'singapore':'Singapore','turkey':'Turkey','universal':'Universal',
           'utc':'Universal','uct':'Universal','us/alaska':'US/Alaska',
           'us/aleutian':'US/Aleutian','us/arizona':'US/Arizona',
           'us/central':'US/Central','us/eastern':'US/Eastern',
           'us/east-indiana':'US/East-Indiana','us/hawaii':'US/Hawaii',
           'us/indiana-starke':'US/Indiana-Starke','us/michigan':'US/Michigan',
           'us/mountain':'US/Mountain','us/pacific':'US/Pacific',
           'us/samoa':'US/Samoa',

           'ut':'Universal',      
           'bst':'GMT+1', 'mest':'GMT+2', 'sst':'GMT+2',
           'fst':'GMT+2', 'wadt':'GMT+8', 'eadt':'GMT+11', 'nzdt':'GMT+13',
           'wet':'GMT', 'wat':'GMT-1', 'at':'GMT-2', 'ast':'GMT-4',
           'nt':'GMT-11', 'idlw':'GMT-12', 'cet':'GMT+1', 'cest':'GMT+2',
           'met':'GMT+1',
           'mewt':'GMT+1', 'swt':'GMT+1', 'fwt':'GMT+1', 'eet':'GMT+2',
           'eest':'GMT+3',
           'bt':'GMT+3', 'zp4':'GMT+4', 'zp5':'GMT+5', 'zp6':'GMT+6',
           'wast':'GMT+7', 'cct':'GMT+8', 'jst':'GMT+9', 'east':'GMT+10',
           'gst':'GMT+10', 'nzt':'GMT+12', 'nzst':'GMT+12', 'idle':'GMT+12',
           'ret':'GMT+4'
           }

    def __init__(self):
        self._db=DateTimeZone._data
        self._d,self._zidx={},self._zmap.keys()

    def __getitem__(self,k):
        try:   n=self._zmap[k.lower()]
        except KeyError:
            if numericTimeZoneMatch(k) == None:
                raise 'DateTimeError','Unrecognized timezone: %s' % k
            return k
        try: return self._d[n]
        except KeyError:
            z=self._d[n]=_timezone(self._db[n])
            return z

def _findLocalTimeZoneName(isDST):
    if not daylight:
        # Daylight savings does not occur in this time zone.
        isDST = 0
    try:
        # Get the name of the current time zone depending
        # on DST.
        _localzone = _cache._zmap[tzname[isDST].lower()]
    except:
        try:
            # Generate a GMT-offset zone name.
            if isDST:
                localzone = altzone
            else:
                localzone = timezone
            offset=(-localzone/(60*60))
            majorOffset=int(offset)
            if majorOffset != 0 :
                minorOffset=abs(int((offset % majorOffset) * 60.0))
            else: minorOffset = 0
            m=majorOffset >= 0 and '+' or ''
            lz='%s%0.02d%0.02d' % (m, majorOffset, minorOffset)
            _localzone = _cache._zmap[('GMT%s' % lz).lower()]
        except:
            _localzone = ''
    return _localzone
    
# Some utility functions for calculating dates:

def _calcSD(t):
    # Returns timezone-independent days since epoch and the fractional
    # part of the days.
    dd = t + EPOCH - 86400.0
    d = dd / 86400.0
    s = d - math.floor(d)
    return s, d

def _calcDependentSecond(tz, t):
    # Calculates the timezone-dependent second (integer part only)
    # from the timezone-independent second.
    fset = _tzoffset(tz, t)
    return fset + long(math.floor(t)) + long(EPOCH) - 86400L
    
def _calcDependentSecond2(yr,mo,dy,hr,mn,sc):
    # Calculates the timezone-dependent second (integer part only)
    # from the date given.
    ss = int(hr) * 3600 + int(mn) * 60 + int(sc)
    x = long(_julianday(yr,mo,dy)-jd1901) * 86400 + ss
    return x

def _calcIndependentSecondEtc(tz, x, ms):
    # Derive the timezone-independent second from the timezone
    # dependent second.
    fsetAtEpoch = _tzoffset(tz, 0.0)
    nearTime = x - fsetAtEpoch - long(EPOCH) + 86400L + ms
    # nearTime is now within an hour of being correct.
    # Recalculate t according to DST.
    fset = long(_tzoffset(tz, nearTime))
    x_adjusted = x - fset + ms
    d = x_adjusted / 86400.0
    t = x_adjusted - long(EPOCH) + 86400L
    millis = (x + 86400 - fset) * 1000 + \
             long(ms * 1000.0) - long(EPOCH * 1000.0)
    s = d - math.floor(d)
    return s,d,t,millis

def _calcHMS(x, ms):
    # hours, minutes, seconds from integer and float.
    hr = x / 3600
    x = x - hr * 3600
    mn = x / 60
    sc = x - mn * 60 + ms
    return hr,mn,sc

def _calcYMDHMS(x, ms):
    # x is a timezone-dependent integer of seconds.
    # Produces yr,mo,dy,hr,mn,sc.
    yr,mo,dy=_calendarday(x / 86400 + jd1901)
    x = int(x - (x / 86400) * 86400)
    hr = x / 3600
    x = x - hr * 3600
    mn = x / 60
    sc = x - mn * 60 + ms
    return yr,mo,dy,hr,mn,sc

def _julianday(yr,mo,dy):
    y,m,d=long(yr),long(mo),long(dy)
    if m > 12L:
        y=y+m/12L
        m=m%12L
    elif m < 1L:
        m=-m
        y=y-m/12L-1L
        m=12L-m%12L
    if y > 0L: yr_correct=0L
    else:      yr_correct=3L
    if m < 3L: y, m=y-1L,m+12L
    if y*10000L+m*100L+d > 15821014L: b=2L-y/100L+y/400L
    else: b=0L
    return (1461L*y-yr_correct)/4L+306001L*(m+1L)/10000L+d+1720994L+b

def _calendarday(j):
    j=long(j)
    if(j < 2299160L):
        b=j+1525L
    else:
        a=(4L*j-7468861L)/146097L
        b=j+1526L+a-a/4L
    c=(20L*b-2442L)/7305L
    d=1461L*c/4L
    e=10000L*(b-d)/306001L
    dy=int(b-d-306001L*e/10000L)
    mo=(e < 14L) and int(e-1L) or int(e-13L)
    yr=(mo > 2) and (c-4716L) or (c-4715L)
    return int(yr),int(mo),int(dy)

def _tzoffset(tz, t):
    try:
        return DateTimeParser._tzinfo[tz].info(t)[0]
    except:
        if numericTimeZoneMatch(tz) is not None:
            return -int(tz[1:3])*3600-int(tz[3:5])*60
        else:
            return 0 # ??

def _correctYear(year):
    # Y2K patch.
    if year >= 0 and year < 100:
        # 00-69 means 2000-2069, 70-99 means 1970-1999.
        if year < 70:
            year = 2000 + year
        else:
            year = 1900 + year
    return year

def safegmtime(t):
    '''gmtime with a safety zone.'''
    try:
        t_int = int(t)
    except OverflowError:
        raise TimeError('The time %f is beyond the range ' 
                        'of this Python implementation.' % float(t))
    rval = gmtime(t_int)
    return rval

def safelocaltime(t):
    '''localtime with a safety zone.'''
    try:
        t_int = int(t)
    except OverflowError:
        raise TimeError('The time %f is beyond the range ' 
                        'of this Python implementation.' % float(t))
    rval = localtime(t_int)
    return rval

class DateTimeParser:

    def parse(self, arg, local=1):
        """Parse a string containing some sort of date-time data
        
        As a general rule, any date-time representation that is 
        recognized and unambigous to a resident of North America is
        acceptable.(The reason for this qualification is that
        in North America, a date like: 2/1/1994 is interpreted
        as February 1, 1994, while in some parts of the world,
        it is interpreted as January 2, 1994.) A date/time
        string consists of two components, a date component and
        an optional time component, separated by one or more
        spaces. If the time component is omited, 12:00am is
        assumed. Any recognized timezone name specified as the
        final element of the date/time string will be used for
        computing the date/time value. (If you create a DateTime
        with the string 'Mar 9, 1997 1:45pm US/Pacific', the
        value will essentially be the same as if you had captured
        time.time() at the specified date and time on a machine in
        that timezone)
        
        x=DateTime('1997/3/9 1:45pm')
        # returns specified time, represented in local machine zone.
        
        y=DateTime('Mar 9, 1997 13:45:00')
        # y is equal to x
        
        The function automatically detects and handles
        ISO8601 compliant dates (YYYY-MM-DDThh:ss:mmTZD).
        See http://www.w3.org/TR/NOTE-datetime for full specs.
        
        The date component consists of year, month, and day
        values. The year value must be a one-, two-, or
        four-digit integer. If a one- or two-digit year is
        used, the year is assumed to be in the twentieth
        century. The month may an integer, from 1 to 12, a
        month name, or a month abreviation, where a period may
        optionally follow the abreviation. The day must be an
        integer from 1 to the number of days in the month. The
        year, month, and day values may be separated by
        periods, hyphens, forward, shashes, or spaces. Extra
        spaces are permitted around the delimiters. Year,
        month, and day values may be given in any order as long
        as it is possible to distinguish the components. If all
        three components are numbers that are less than 13,
        then a a month-day-year ordering is assumed.
        
        The time component consists of hour, minute, and second
        values separated by colons.  The hour value must be an
        integer between 0 and 23 inclusively. The minute value
        must be an integer between 0 and 59 inclusively. The
        second value may be an integer value between 0 and
        59.999 inclusively. The second value or both the minute
        and second values may be ommitted. The time may be
        followed by am or pm in upper or lower case, in which
        case a 12-hour clock is assumed.

        If a string argument passed to the DateTime constructor cannot be
        parsed, it will raise SyntaxError. Invalid date components
        will raise a DateError, while invalid time or timezone components
        will raise a DateTimeError. 
        """
        if not isinstance(arg, StringTypes):
            raise TypeError, 'Expected a string argument'

        if not arg:
            raise SyntaxError(arg)

        if arg.find(' ')==-1 and arg[4]=='-':
            yr,mo,dy,hr,mn,sc,tz=self._parse_iso8601(arg)
        else:
            yr,mo,dy,hr,mn,sc,tz=self._parse(arg, local)


        if not self._validDate(yr,mo,dy):
            raise DateError(arg, yr, mo, dy)
        if not self._validTime(hr,mn,int(sc)):
            raise TimeError(arg)

        return yr, mo, dy, hr, mn, sc, tz

    def time(self, arg):

        yr, mo, dy, hr, mn, sc, tz = self.parse(arg)
        
        ms = sc - math.floor(sc)
        x = _calcDependentSecond2(yr,mo,dy,hr,mn,sc)

        if tz:
            try:
                tz=self._tzinfo._zmap[tz.lower()]
            except KeyError:
                if numericTimeZoneMatch(tz) is None:
                    raise DateTimeError('Unknown time zone in date: %s' % arg)
        else:
            tz = self._calcTimezoneName(x, ms)
        s,d,t,millisecs = _calcIndependentSecondEtc(tz, x, ms)

        return t
        

    int_pattern  =re.compile(r'([0-9]+)') #AJ
    flt_pattern  =re.compile(r':([0-9]+\.[0-9]+)') #AJ
    name_pattern =re.compile(r'([a-zA-Z]+)', re.I) #AJ
    space_chars  =' \t\n'
    delimiters   ='-/.:,+'
    _month_len  =((0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31), 
                  (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31))
    _until_month=((0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334),
                  (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335))
    _monthmap   ={'january': 1,   'jan': 1,
                  'february': 2,  'feb': 2,
                  'march': 3,     'mar': 3,
                  'april': 4,     'apr': 4,
                  'may': 5,
                  'june': 6,      'jun': 6,
                  'july': 7,      'jul': 7,
                  'august': 8,    'aug': 8,
                  'september': 9, 'sep': 9, 'sept': 9,
                  'october': 10,  'oct': 10,
                  'november': 11, 'nov': 11,
                  'december': 12, 'dec': 12}
    _daymap     ={'sunday': 1,    'sun': 1,
                  'monday': 2,    'mon': 2,
                  'tuesday': 3,   'tues': 3,  'tue': 3,
                  'wednesday': 4, 'wed': 4,
                  'thursday': 5,  'thurs': 5, 'thur': 5, 'thu': 5,
                  'friday': 6,    'fri': 6,
                  'saturday': 7,  'sat': 7}

    _localzone0 = _findLocalTimeZoneName(0)
    _localzone1 = _findLocalTimeZoneName(1)
    _multipleZones = (_localzone0 != _localzone1)
    # For backward compatibility only:
    _isDST = localtime(_time())[8]
    _localzone  = _isDST and _localzone1 or _localzone0
    
    _tzinfo     = _cache()

    def localZone(self, ltm=None):
        '''Returns the time zone on the given date.  The time zone
        can change according to daylight savings.'''
        if not self._multipleZones:
            return self._localzone0
        if ltm == None:
            ltm = localtime(_time())
        isDST = ltm[8]
        lz = isDST and self._localzone1 or self._localzone0
        return lz
        
    def _calcTimezoneName(self, x, ms):
        # Derive the name of the local time zone at the given
        # timezone-dependent second.
        if not self._multipleZones:
            return self._localzone0
        fsetAtEpoch = _tzoffset(self._localzone0, 0.0)
        nearTime = x - fsetAtEpoch - long(EPOCH) + 86400L + ms
        # nearTime is within an hour of being correct.
        try:
            ltm = safelocaltime(nearTime)
        except:
            # We are beyond the range of Python's date support.
            # Hopefully we can assume that daylight savings schedules
            # repeat every 28 years.  Calculate the name of the
            # time zone using a supported range of years.
            yr,mo,dy,hr,mn,sc = _calcYMDHMS(x, 0)
            yr = ((yr - 1970) % 28) + 1970
            x = _calcDependentSecond2(yr,mo,dy,hr,mn,sc)
            nearTime = x - fsetAtEpoch - long(EPOCH) + 86400L + ms
            ltm = safelocaltime(nearTime)
        tz = self.localZone(ltm)
        return tz

    def _parse(self, string, local=1):
        # Parse date-time components from a string
        month = year = tz = tm = None
        spaces         = self.space_chars
        intpat         = self.int_pattern
        fltpat         = self.flt_pattern
        wordpat        = self.name_pattern
        delimiters     = self.delimiters
        MonthNumbers   = self._monthmap
        DayOfWeekNames = self._daymap
        ValidZones     = self._tzinfo._zidx
        TimeModifiers  = ['am','pm']

        string = string.strip()

        # Find timezone first, since it should always be the last
        # element, and may contain a slash, confusing the parser.

        
        # First check for time zone of form +dd:dd
        tz = _iso_tz_re.search(string)
        if tz:
            tz = tz.start(0)
            tz, string = string[tz:], string[:tz].strip()
            tz = tz[:3]+tz[4:]
        else:
            # Look at last token
            sp=string.split()
            tz = sp[-1]
            if tz and (tz.lower() in ValidZones):
                string=' '.join(sp[:-1])
            else:
                tz = None  # Decide later, since the default time zone
                           # could depend on the date.

        ints,dels=[],[]
        i,l=0,len(string)
        while i < l:
            while i < l and string[i] in spaces    : i=i+1
            if i < l and string[i] in delimiters:
                d=string[i]
                i=i+1
            else: d=''
            while i < l and string[i] in spaces    : i=i+1

            # The float pattern needs to look back 1 character, because it
            # actually looks for a preceding colon like ':33.33'. This is
            # needed to avoid accidentally matching the date part of a
            # dot-separated date string such as '1999.12.31'.
            if i > 0: b=i-1
            else: b=i

            ts_results = fltpat.match(string, b)
            if ts_results:
                s=ts_results.group(1)
                i=i+len(s)
                ints.append(float(s))
                continue
            
            #AJ
            ts_results = intpat.match(string, i)
            if ts_results: 
                s=ts_results.group(0)

                ls=len(s)
                i=i+ls
                if (ls==4 and d and d in '+-' and
                    (len(ints) + (not not month) >= 3)):
                    tz='%s%s' % (d,s)
                else:
                    v=int(s)
                    ints.append(v)
                continue


            ts_results = wordpat.match(string, i)
            if ts_results:
                o,s=ts_results.group(0),ts_results.group(0).lower()
                i=i+len(s)
                if i < l and string[i]=='.': i=i+1
                # Check for month name:
                if s in MonthNumbers:
                    v=MonthNumbers[s]
                    if month is None: month=v
                    else: raise SyntaxError(string)
                    continue
                # Check for time modifier:
                if s in TimeModifiers:
                    if tm is None: tm=s
                    else: raise SyntaxError(string)
                    continue
                # Check for and skip day of week:
                if s in DayOfWeekNames:
                    continue
            raise SyntaxError(string)

        day=None
        if ints[-1] > 60 and d not in ['.',':'] and len(ints) > 2:
            year=ints[-1]
            del ints[-1]
            if month:
                day=ints[0]
                del ints[:1]
            else:
                month=ints[0]
                day=ints[1]
                del ints[:2]
        elif month:
            if len(ints) > 1:
                if ints[0] > 31:
                    year=ints[0]
                    day=ints[1]
                else:
                    year=ints[1]
                    day=ints[0]
                del ints[:2]
        elif len(ints) > 2:
            if ints[0] > 31:
                year=ints[0]
                if ints[1] > 12:
                    day=ints[1]
                    month=ints[2]
                else:
                    day=ints[2]
                    month=ints[1]
            if ints[1] > 31:
                year=ints[1]
                if ints[0] > 12 and ints[2] <= 12:
                    day=ints[0]
                    month=ints[2]
                elif ints[2] > 12 and ints[0] <= 12:
                    day=ints[2]
                    month=ints[0]
            elif ints[2] > 31:
                year=ints[2]
                if ints[0] > 12:
                    day=ints[0]
                    month=ints[1]
                else:
                    day=ints[1]
                    month=ints[0]
            elif ints[0] <= 12:
                month=ints[0]
                day=ints[1]
                year=ints[2]
            del ints[:3]
            
        if day is None:
            # Use today's date.
            year,month,day = localtime(_time())[:3]

        year = _correctYear(year)
        if year < 1000: raise SyntaxError(string)
        
        leap = year%4==0 and (year%100!=0 or year%400==0)
        try:
            if not day or day > self._month_len[leap][month]:
                raise DateError(string)
        except IndexError:
            raise DateError(string)
        tod=0
        if ints:
            i=ints[0]
            # Modify hour to reflect am/pm
            if tm and (tm=='pm') and i<12:  i=i+12
            if tm and (tm=='am') and i==12: i=0
            if i > 24: raise DateTimeError(string)
            tod = tod + int(i) * 3600
            del ints[0]
            if ints:
                i=ints[0]
                if i > 60: raise DateTimeError(string)
                tod = tod + int(i) * 60
                del ints[0]
                if ints:
                    i=ints[0]
                    if i > 60: raise DateTimeError(string)
                    tod = tod + i
                    del ints[0]
                    if ints: raise SyntaxError(string)

    
        tod_int = int(math.floor(tod))
        ms = tod - tod_int
        hr,mn,sc = _calcHMS(tod_int, ms)

        if local and not tz:
            # Figure out what time zone it is in the local area
            # on the given date.
            x = _calcDependentSecond2(year,month,day,hr,mn,sc)
            tz = self._calcTimezoneName(x, ms)

        return year,month,day,hr,mn,sc,tz

    def _validDate(self,y,m,d):
        if m<1 or m>12 or y<0 or d<1 or d>31: return 0
        return d<=self._month_len[(y%4==0 and (y%100!=0 or y%400==0))][m]

    def _validTime(self,h,m,s):
        return h>=0 and h<=23 and m>=0 and m<=59 and s>=0 and s < 60

    def _parse_iso8601(self,s):
        try:
            return self.__parse_iso8601(s)
        except IndexError:
            raise DateError(
                'Not an ISO 8601 compliant date string: "%s"' %  s)


    def __parse_iso8601(self,s):
        """ parse an ISO 8601 compliant date """
        year=0
        month=day=1
        hour=minute=seconds=hour_off=min_off=0
        
        datereg = re.compile(
            '([0-9]{4})(-([0-9][0-9]))?(-([0-9][0-9]))?')
        timereg = re.compile(
            '([0-9]{2})(:([0-9][0-9]))?(:([0-9][0-9]))?(\.[0-9]{1,20})?')
    
        # Date part
    
        fields = datereg.split(s.strip())
        if fields[1]:   year  = int(fields[1])
        if fields[3]:   month = int(fields[3])
        if fields[5]:   day   = int(fields[5])
    
        if s.find('T')>-1:
            fields = timereg.split(s[s.find('T')+1:])
    
            if fields[1]:   hour     = int(fields[1])
            if fields[3]:   minute   = int(fields[3])
            if fields[5]:   seconds  = int(fields[5])
            if fields[6]:   seconds  = seconds+float(fields[6])
    
        if s.find('Z')>-1:
            pass
    
        if s[-3]==':' and s[-6] in ['+','-']:
            hour_off = int(s[-6:-3])
            min_off  = int(s[-2:])

        return (year,month,day,hour,minute,seconds,
                'GMT%+03d%02d' % (hour_off,min_off))

parser = DateTimeParser()
parse = parser.parse
time = parser.time

class tzinfo(object):

    __slots__ = ('offset', )
    
    def __init__(self, offset):
        self.offset = offset

    def utcoffset(self, dt=None):
        return self.offset

    __getstate__ = utcoffset
    __setstate__ = __init__

    def dst(self, dt): return 0
    def tzname(self, dt): return ''

from datetime import datetimetz as _datetimetz
def parseDatetimetz(string):
    y, mo, d, h, m, s, tz = parse(string)
    s, micro = divmod(s, 1.0)
    micro = int(micro * 1000000)
    offset = _tzoffset(tz, None) / 60
    return _datetimetz(y, mo, d, h, m, s, micro, tzinfo(offset))

_iso_tz_re = re.compile("[-+]\d\d:\d\d$")

    
